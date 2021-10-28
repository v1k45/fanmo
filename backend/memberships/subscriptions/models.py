import copy
from dateutil.relativedelta import relativedelta

from django.db import models
from django.contrib.postgres.fields import ArrayField

from django.utils import timezone
from versatileimagefield.fields import VersatileImageField

from memberships.utils import razorpay_client
from djmoney.models.fields import MoneyField

from django_fsm import FSMField, transition

from memberships.utils.models import BaseModel


class Tier(BaseModel):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cover = VersatileImageField(upload_to="uploads/covers/", blank=True)
    welcome_message = models.TextField(blank=True)
    benefits = ArrayField(models.CharField(max_length=50), size=8)

    amount = MoneyField(max_digits=7, decimal_places=2)

    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)

    seller_user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Plan(BaseModel):
    name = models.CharField(max_length=255)
    tier = models.ForeignKey("subscriptions.Tier", on_delete=models.CASCADE, null=True)

    # hardcode for now.
    period = "monthly"
    interval = 1

    amount = MoneyField(max_digits=7, decimal_places=2)
    external_id = models.CharField(max_length=255)

    seller_user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    buyer_user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="custom_plans", null=True
    )

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    @classmethod
    def for_subscription(cls, amount, seller, buyer):
        tier = (
            Tier.objects.filter(amount__lte=amount, seller_user=seller)
            .order_by("-amount")
            .first()
        )

        tier_name = tier.name if tier else "Custom"
        default_name = f"{tier_name} ({amount}) - {seller.name}"

        # todo - cleanup orpahed plans?
        plan, created = cls.objects.get_or_create(
            amount=amount,
            tier=tier,
            seller_user=seller,
            buyer_user=buyer,
            defaults={"name": default_name},
        )
        if created:
            plan.create_external()

        return plan

    def subscribe(self, subscriber):
        subscription = Subscription.objects.create(
            plan=self,
            status=Subscription.Status.CREATED,
            subscriber=subscriber,
            expires_at=timezone.now() + relativedelta(month=1),
        )
        subscription.create_external()
        return subscription

    def create_external(self):
        external_plan = razorpay_client.plan.create(
            {
                "period": self.period,
                "interval": self.interval,
                "item": {
                    "name": self.name,
                    "amount": self.amount.get_amount_in_sub_unit(),
                    "currency": self.amount.currency.code,
                },
                "notes": {"external_id": self.id},
            }
        )
        self.external_id = external_plan["id"]
        self.save()


class Subscription(BaseModel):
    class Status(models.TextChoices):
        CREATED = "created"
        AUTHENTICATED = "authenticated"
        ACTIVE = "active"
        PENDING = "pending"
        HALTED = "halted"
        CANCELLED = "cancelled"
        PAUSED = "paused"
        EXPIRED = "expired"
        COMPLETED = "completed"

    plan = models.ForeignKey("subscriptions.Plan", on_delete=models.CASCADE)
    status = FSMField(default=Status.CREATED)
    external_id = models.CharField(max_length=255)

    # inception and end
    cycle_start_at = models.DateField()
    cycle_end_at = models.DateField()

    is_active = models.BooleanField(default=False)

    seller_user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="subscribers"
    )
    buyer_user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    scheduled_to_cancel = models.BooleanField(default=False)
    scheduled_to_change = models.BooleanField(default=True)

    def create_external(self):
        external_subscription = razorpay_client.subscription.create(
            {
                "plan_id": self.plan.external_id,
                "total_count": 12,
                "notes": {"external_id": self.id},
            }
        )
        self.external_id = external_subscription["id"]
        self.save()

    @transition(
        field=status,
        source=[Status.AUTHENTICATED, Status.PENDING, Status.HALTED],
        target=Status.ACTIVE,
    )
    def activate(self, start_at):
        self.cycle_start_at = start_at
        self.cycle_end_at = relativedelta(start_at, months=1)
        self.save() 

    # tbd?
    @transition(field=status, source=Status.ACTIVE, target=Status.PAUSED)
    def pause(self):
        razorpay_client.subscription.post_url(
            f"{razorpay_client.subscription.base_url}/{self.external_id}/pause",
            {"pause_at": "now"},
        )

    # tbd?
    @transition(field=status, source=Status.PAUSED, target=Status.ACTIVE)
    def resume(self):
        razorpay_client.subscription.post_url(
            f"{razorpay_client.subscription.base_url}/{self.external_id}/resume",
            {"resume_at": "now"},
        )

    @transition(field=status, source="*", target=Status.CANCELLED)
    def cancel(self):
        razorpay_client.subscription.cancel(
            self.external_id,
            {"schedule_change_at": "cycle_end"}
        )
        self.scheduled_to_cancel = True
        self.save() 

    @transition(field=status, source=[Status.ACTIVE], target=Status.COMPLETED)
    def update(self, plan):
        razorpay_client.subscription.post_url(
            f"{razorpay_client.subscription.base_url}/{self.external_id}/update",
            {
                "plan_id": plan.external_id,
                "schedule_change_at": "cycle_end",
            },
        )

        self.scheduled_to_change = True
        self.save()

        new_subscription = copy.deepcopy(self)
        new_subscription.pk = None
        new_subscription.plan = plan
        new_subscription.status = self.Status.AUTHENTICATED
        new_subscription.save()
        return new_subscription

    @transition(
        field=status,
        source=[
            Status.ACTIVE,
        ],
        target=Status.PENDING,
    )
    def start_renewal(self):
        """
        Subscription is past its end time, attempt renewal
        """ 
        pass

    @transition(
        field=status, source=[Status.PENDING, Status.ACTIVE], target=Status.ACTIVE
    )
    def renew(self):
        """Subscription was renewned""" 
        self.cycle_start_at = timezone.now()
        self.cycle_end_at = relativedelta(self.cycle_start_at, months=1)
        self.save()

    @transition(
        field=status, source=[Status.PENDING, Status.ACTIVE], target=Status.HALTED
    )
    def halt(self):
        pass
