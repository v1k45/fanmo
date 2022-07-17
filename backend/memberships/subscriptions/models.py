from moneyed import Money, INR
from decimal import Decimal
from dateutil.relativedelta import relativedelta
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.conf import settings
from django_fsm import FSMField, transition, can_proceed
from djmoney.models.fields import MoneyField
from simple_history.models import HistoricalRecords
from versatileimagefield.fields import VersatileImageField
from memberships.core.notifications import (
    notify_membership_change,
    notify_membership_renewed,
    notify_new_membership,
    notify_membership_stop,
    notify_membership_halted,
    notify_membership_pending,
)

from memberships.payments.models import Payment, Payout
from memberships.subscriptions.querysets import SubscriptionQuerySet
from memberships.utils import razorpay_client
from memberships.utils.models import BaseModel, IPAddressHistoricalModel
from memberships.core.tasks import async_task


class Tier(BaseModel):
    class CoverBackgroundStyle(models.TextChoices):
        CONTAIN = "contain"
        COVER = "cover"

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    cover = VersatileImageField(upload_to="uploads/covers/", blank=True)
    cover_background_style = models.CharField(
        max_length=16,
        choices=CoverBackgroundStyle.choices,
        default=CoverBackgroundStyle.CONTAIN,
    )
    welcome_message = models.TextField(blank=True)
    benefits = ArrayField(models.CharField(max_length=50), size=8, default=list)

    amount = MoneyField(max_digits=7, decimal_places=2)

    is_active = models.BooleanField(default=True)
    is_public = models.BooleanField(default=True)
    is_recommended = models.BooleanField(default=False)

    creator_user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    history = HistoricalRecords(bases=[IPAddressHistoricalModel])

    class Meta:
        ordering = ["creator_user", "amount"]

    def __str__(self):
        return self.name


class Membership(BaseModel):
    tier = models.ForeignKey("subscriptions.Tier", on_delete=models.SET_NULL, null=True)
    creator_user = models.ForeignKey(
        "users.User", related_name="members", on_delete=models.CASCADE
    )
    fan_user = models.ForeignKey(
        "users.User", related_name="memberships", on_delete=models.CASCADE
    )

    active_subscription = models.OneToOneField(
        "subscriptions.Subscription",
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )
    scheduled_subscription = models.OneToOneField(
        "subscriptions.Subscription",
        null=True,
        on_delete=models.SET_NULL,
        related_name="+",
    )

    is_active = models.BooleanField(default=None, null=True)
    history = HistoricalRecords(bases=[IPAddressHistoricalModel])

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=["creator_user", "fan_user"], name="unique_membership"
            )
        ]

    def __str__(self):
        return f"{self.fan_user} -> {self.creator_user} ({self.tier})"

    def start(self, tier, period=None):
        plan = Plan.objects.create(
            name=f"{tier.name} - {self.creator_user.name}",
            tier=tier,
            # todo: guess amount based on currency.
            amount=tier.amount,
            period=period,
            interval=1,
        )
        plan.create_external()

        subscription = Subscription.objects.create(
            plan=plan,
            membership=self,
            status=Subscription.Status.CREATED,
            creator_user=self.creator_user,
            fan_user=self.fan_user,
            cycle_start_at=timezone.now(),
            cycle_end_at=timezone.now() + plan.get_delta(),
        )
        subscription.create_external()

        self.scheduled_subscription = subscription
        self.save()

    def giveaway(self, tier, period=None):
        # TODO: Send different email for giveaway
        plan = Plan.objects.create(
            name=f"{tier.name} - {self.creator_user.name}",
            tier=tier,
            amount=Money(Decimal(0), INR),
            period=period,
            interval=1,
            external_id="giveaway",
        )

        subscription = Subscription.objects.create(
            plan=plan,
            membership=self,
            status=Subscription.Status.CREATED,
            creator_user=self.creator_user,
            fan_user=self.fan_user,
            cycle_start_at=timezone.now(),
            cycle_end_at=timezone.now() + plan.get_delta(),
            external_id="giveaway",
        )

        payment = Payment.objects.create(
            subscription=subscription,
            type=Payment.Type.SUBSCRIPTION,
            status=Payment.Status.CAPTURED,
            creator_user=self.creator_user,
            fan_user=self.fan_user,
            amount=plan.amount,
            method="giveaway",
            external_id="giveaway",
        )

        Payout.objects.create(
            payment=payment,
            status=Payout.Status.PROCESSED,
            bank_account=self.creator_user.bank_accounts.first(),
            amount=plan.amount,
            external_id="giveaway",
        )

        subscription.authenticate()
        subscription.activate()
        subscription.save()

    def update(self, tier, period=None):
        """Update membership with active subscription to a new tier"""
        active_subscription = self.active_subscription
        if not active_subscription:
            raise ValidationError(
                "This membership does not have an active subscription.",
                "no_active_membership",
            )

        # scheduled subscription already exists.
        # make sure we don't remove a subscription that is paid-for
        # TODO: cancel schedule update and create a new update
        scheduled_subscription = self.scheduled_subscription
        if (
            scheduled_subscription
            and scheduled_subscription.status != Subscription.Status.CREATED
        ):
            raise ValidationError(
                f"This membership is already scheduled to update on {scheduled_subscription.cycle_start_at}.",
                "already_scheduled",
            )

        plan = Plan.objects.create(
            name=f"{tier.name} - {self.creator_user.name}",
            tier=tier,
            # todo: guess amount based on currency.
            amount=tier.amount,
            period=period,
            interval=1,
        )
        plan.create_external()
        self.scheduled_subscription = active_subscription.update(plan)
        self.save()

        # membership change does not require further actions, safe to notify user now.
        if (
            self.scheduled_subscription.external_id
            == self.active_subscription.external_id
        ):
            async_task(notify_membership_change, self.id)

    def cancel(self):
        active_subscription = self.active_subscription
        if not active_subscription:
            raise ValidationError(
                "This membership does not have an active subscription.",
                "no_active_membership",
            )

        if active_subscription.status == Subscription.Status.SCHEDULED_TO_CANCEL:
            raise ValidationError(
                f"This membership is already scheduled to cancel on {active_subscription.cycle_end_at}.",
                "already_cancelled",
            )

        if active_subscription.status == Subscription.Status.CANCELLED:
            raise ValidationError(
                "This membership is already cancelled.", "already_cancelled"
            )

        active_subscription.schedule_to_cancel()
        active_subscription.save()
        # send cancellation email and create activity
        async_task(notify_membership_stop, self.pk)

    def activate(self, subscription):
        # clear scheduled subscription
        if self.scheduled_subscription == subscription:
            self.scheduled_subscription = None
        self.active_subscription = subscription
        self.tier = self.active_subscription.plan.tier
        self.is_active = True
        self.save()


class Plan(BaseModel):
    """
    Subscription plan, similar to a tier, but private.
    """

    class Period(models.TextChoices):
        WEEKLY = "weekly"
        MONTHLY = "monthly"
        YEARLY = "yearly"

    name = models.CharField(max_length=255)
    tier = models.ForeignKey("subscriptions.Tier", on_delete=models.CASCADE, null=True)

    period = models.CharField(
        max_length=16, choices=Period.choices, default=Period.MONTHLY
    )
    interval = models.PositiveSmallIntegerField(default=1)

    amount = MoneyField(max_digits=7, decimal_places=2)
    external_id = models.CharField(max_length=255)

    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    def get_delta(self):
        if self.period == self.Period.WEEKLY:
            return relativedelta(weeks=self.interval)
        elif self.period == self.Period.YEARLY:
            return relativedelta(years=self.interval)
        else:
            return relativedelta(months=self.interval)

    def get_term_count(self):
        base_term = {
            self.Period.WEEKLY: 52,
            self.Period.MONTHLY: 12,
            self.Period.YEARLY: 1,
        }
        return (base_term[self.period] * 5) // self.interval

    @classmethod
    def for_subscription(cls, amount, creator_user):
        tier = (
            Tier.objects.filter(amount__lte=amount, creator_user=creator_user)
            .order_by("-amount")
            .first()
        )

        tier_name = tier.name if tier else "Custom"
        default_name = f"{tier_name} ({amount}) - {creator_user.name}"

        # todo - cleanup orpahed plans?
        plan, created = cls.objects.get_or_create(
            amount=amount,
            tier=tier,
            defaults={"name": default_name},
        )
        if created:
            plan.create_external()

        return plan

    def subscribe(self, fan_user):
        # update subscription if it already exists.
        try:
            existing_subscription = Subscription.objects.active(
                self.creator_user, self.fan_user
            )
            updated_subscription = existing_subscription.update(self)
            existing_subscription.save()
            return updated_subscription
        except Subscription.DoesNotExist:
            pass

        subscription = Subscription.objects.create(
            plan=self,
            status=Subscription.Status.CREATED,
            creator_user=self.tier.creator_user,
            fan_user=fan_user,
            cycle_start_at=timezone.now(),
            cycle_end_at=timezone.now() + self.get_delta(),
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
        # authorized by fan
        AUTHENTICATED = "authenticated"
        # charged successfully
        ACTIVE = "active"
        # will be activated in next cycle
        SCHEDULED_TO_ACTIVATE = "scheduled_to_activate"
        # renewing at end of cycle
        PENDING = "pending"
        HALTED = "halted"
        # used when updating current subscription.
        SCHEDULED_TO_CANCEL = "scheduled_to_cancel"
        CANCELLED = "cancelled"
        # final states
        PAUSED = "paused"
        EXPIRED = "expired"
        COMPLETED = "completed"

    class PaymentMethod(models.TextChoices):
        CARD = "card"
        EMANDATE = "emandate"
        UPI = "upi"
        WALLET = "wallet"

    plan = models.ForeignKey("subscriptions.Plan", on_delete=models.CASCADE)
    status = FSMField(default=Status.CREATED)
    external_id = models.CharField(max_length=255)

    payment_method = models.CharField(
        max_length=16, choices=PaymentMethod.choices, blank=True
    )

    # inception and end
    cycle_start_at = models.DateTimeField()
    cycle_end_at = models.DateTimeField()

    is_active = models.BooleanField(default=False)

    membership = models.ForeignKey(
        "subscriptions.Membership", on_delete=models.CASCADE, null=True
    )

    creator_user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="subscribers"
    )
    fan_user = models.ForeignKey("users.User", on_delete=models.CASCADE)

    objects = SubscriptionQuerySet.as_manager()
    history = HistoricalRecords(bases=[IPAddressHistoricalModel])

    def create_external(self):
        subscription_data = {
            "plan_id": self.plan.external_id,
            "total_count": self.plan.get_term_count(),
            "notes": {"external_id": self.id},
            "customer_notify": 0,
        }
        if self.cycle_start_at > timezone.now():
            subscription_data["start_at"] = int(self.cycle_start_at.timestamp())

        external_subscription = razorpay_client.subscription.create(subscription_data)
        self.external_id = external_subscription["id"]
        self.save()

    def is_giveaway(self):
        return self.external_id == "giveaway"

    @transition(
        field=status,
        source=Status.CREATED,
        target=Status.AUTHENTICATED,
    )
    def authenticate(self):
        # schedule current subscription to cancel
        active_subscription = self.membership.active_subscription
        if (
            active_subscription
            and active_subscription.external_id != self.external_id
            and can_proceed(active_subscription.schedule_to_cancel)
        ):
            active_subscription.schedule_to_cancel()
            active_subscription.save()

    def can_activate(self):
        return self.cycle_start_at < timezone.now()

    @transition(
        field=status,
        source=[
            Status.AUTHENTICATED,
            Status.SCHEDULED_TO_ACTIVATE,
        ],
        target=Status.ACTIVE,
        conditions=[can_activate],
    )
    def activate(self):
        # todo: remove is_active field
        self.is_active = True
        self.membership.activate(self)
        self.membership.save()
        async_task(notify_new_membership, self.membership_id)

    @transition(
        field=status,
        source=[Status.AUTHENTICATED, Status.PENDING, Status.HALTED],
        target=Status.SCHEDULED_TO_ACTIVATE,
    )
    def schedule_to_activate(self):
        async_task(notify_membership_change, self.membership_id)

    @transition(
        field=status,
        source=[
            Status.CREATED,
            Status.AUTHENTICATED,
            Status.ACTIVE,
            Status.PENDING,
            Status.SCHEDULED_TO_ACTIVATE,
            Status.PAUSED,
        ],
        target=Status.SCHEDULED_TO_CANCEL,
    )
    def schedule_to_cancel(self):
        if self.is_giveaway() or self.can_cancel():
            return

        razorpay_client.subscription.cancel(
            self.external_id, {"cancel_at_cycle_end": 1}
        )

    def can_cancel(self):
        return self.cycle_end_at < timezone.now()

    @transition(
        field=status,
        source=Status.SCHEDULED_TO_CANCEL,
        target=Status.CANCELLED,
        conditions=[can_cancel],
    )
    def cancel(self):
        # hard cancel when the subscription is future not charged yet.
        self.is_active = False
        self.membership.is_active = False
        self.membership.save()

    def update(self, plan):
        # when using upi, subscription cannot be updated
        # create a new one
        # and schedule current one for cancellation only after new one is authorized.
        if self.payment_method == self.PaymentMethod.UPI:
            new_subscription = Subscription.objects.create(
                membership=self.membership,
                plan=plan,
                status=Subscription.Status.CREATED,
                # pad time to day end?
                cycle_start_at=self.cycle_end_at,
                cycle_end_at=self.cycle_end_at + plan.get_delta(),
                fan_user=self.fan_user,
                creator_user=self.creator_user,
            )
            new_subscription.create_external()
        else:
            # todo
            # if subscription is scheduled to cancel
            # create a new one
            razorpay_client.subscription.patch_url(
                f"{razorpay_client.subscription.base_url}/{self.external_id}",
                {
                    "plan_id": plan.external_id,
                    "schedule_change_at": "cycle_end",
                },
            )

            # treat current subscripton as cancelled after the update.
            self.status = self.Status.SCHEDULED_TO_CANCEL
            self.save()

            new_subscription = Subscription.objects.create(
                membership=self.membership,
                plan=plan,
                status=Subscription.Status.SCHEDULED_TO_ACTIVATE,
                # pad time to day end?
                cycle_start_at=self.cycle_end_at,
                cycle_end_at=self.cycle_end_at + plan.get_delta(),
                fan_user=self.fan_user,
                creator_user=self.creator_user,
                external_id=self.external_id,
            )
        return new_subscription

    def can_start_renew(self):
        # allow starting renewal from a day before the expiry date.
        return (self.cycle_end_at - relativedelta(days=1)) < timezone.now()

    @transition(
        field=status,
        source=[
            Status.ACTIVE,
            Status.PENDING,
        ],
        target=Status.PENDING,
        conditions=[can_start_renew],
    )
    def start_renewal(self):
        """
        Subscription is past its end time, attempt renewal
        """
        async_task(notify_membership_pending, self.membership_id)

    @transition(
        field=status,
        source=[Status.PENDING, Status.PAUSED, Status.HALTED, Status.ACTIVE],
        target=Status.ACTIVE,
    )
    def renew(self, cycle_end_at):
        """Subscription was renewned"""
        self.cycle_end_at = cycle_end_at
        self.membership.activate(self)
        async_task(notify_membership_renewed, self.membership_id)

    def can_halt(self):
        halt_date = self.cycle_end_at + relativedelta(
            days=settings.SUBSCRIPTION_GRACE_PERIOD_DAYS
        )
        return halt_date < timezone.now()

    @transition(
        field=status,
        source=[Status.PENDING, Status.ACTIVE],
        target=Status.HALTED,
        conditions=[can_halt],
    )
    def halt(self):
        self.is_active = False
        self.membership.is_active = False
        self.membership.save()
        async_task(notify_membership_halted, self.membership_id)
