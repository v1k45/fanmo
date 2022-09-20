from django.core.exceptions import ValidationError
from django.db import models
from django_fsm import FSMField, can_proceed
from djmoney.models.fields import MoneyField

from fanmo.core.notifications import notify_donation
from fanmo.core.tasks import async_task
from fanmo.utils import razorpay_client
from fanmo.utils.models import BaseModel
from fanmo.utils.money import (
    deduct_platform_fee,
    money_from_sub_unit,
    money_to_sub_unit,
)


class Payment(BaseModel):
    class Type(models.TextChoices):
        DONATION = "donation"
        # todo: rename to membership
        SUBSCRIPTION = "subscription"

    class Status(models.TextChoices):
        CREATED = "created"
        AUTHORIZED = "authorized"
        CAPTURED = "captured"
        REFUNDED = "refunded"
        FAILED = "failed"

    class Method(models.TextChoices):
        CARD = "card"
        NETBANKING = "netbanking"
        UPI = "upi"
        WALLET = "wallet"

    subscription = models.ForeignKey(
        "memberships.Subscription", on_delete=models.CASCADE, null=True, blank=True
    )
    donation = models.ForeignKey(
        "donations.Donation", on_delete=models.CASCADE, null=True, blank=True
    )

    creator_user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="received_payments"
    )
    fan_user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, null=True, blank=True
    )

    status = FSMField(default=Status.CREATED, choices=Status.choices)
    type = models.CharField(max_length=16, choices=Type.choices)
    method = models.CharField(max_length=16, choices=Method.choices)

    amount = MoneyField(max_digits=7, decimal_places=2)
    external_id = models.CharField(max_length=255)

    @classmethod
    def for_subscription(cls, subscription, payload):
        payment, _ = Payment.objects.get_or_create(
            type=Payment.Type.SUBSCRIPTION,
            subscription=subscription,
            status=Payment.Status.CAPTURED,
            amount=money_from_sub_unit(payload["amount"], payload["currency"]),
            external_id=payload["id"],
            creator_user=subscription.creator_user,
            fan_user=subscription.fan_user,
        )
        Payout.for_payment(payment)
        return payment

    @classmethod
    def authenticate_subscription(cls, payload):
        from fanmo.memberships.models import Subscription

        # only usable for "created" subscription
        razorpay_client.utility.verify_payment_signature(payload)

        # how to identify the payment for which the user is creating subscription?
        # only possible if there is 1:1 reference between local and external subscription.
        try:
            subscription: Subscription = (
                Subscription.objects.filter(status=Subscription.Status.CREATED)
                .select_for_update()
                .get(external_id=payload["razorpay_subscription_id"])
            )
        except Subscription.DoesNotExist:
            raise ValidationError(
                "This subscription has been already processed.",
                "payment_already_processed",
            )

        subscription.authenticate()

        razorpay_payment = razorpay_client.payment.fetch(payload["razorpay_order_id"])
        # TODO: figure out what to with authentication payments.
        # make sure payment is not already processed?
        # allow soft reprocessing if it is for real local subscription.
        # cannot use the payment id provided in the payload because it is refunded.
        payment, _ = Payment.objects.get_or_create(
            type=Payment.Type.SUBSCRIPTION,
            subscription=subscription,
            amount=money_from_sub_unit(
                razorpay_payment["amount"], razorpay_payment["currency"]
            ),
            # payment id is stored in order_id field of subscription
            external_id=razorpay_payment["id"],
            creator_user=subscription.creator_user,
            fan_user=subscription.fan_user,
            defaults={
                "status": razorpay_payment["status"],
                "method": razorpay_payment["method"],
            },
        )
        subscription.payment_method = razorpay_payment["method"]
        if can_proceed(subscription.activate):
            subscription.activate()
        else:
            subscription.schedule_to_activate()
        subscription.save()
        return payment

    @classmethod
    def capture_donation(cls, payload):
        from fanmo.donations.models import Donation

        razorpay_client.utility.verify_payment_signature(payload)

        donation = Donation.objects.get(external_id=payload["razorpay_order_id"])
        razorpay_payment = razorpay_client.payment.capture(
            payload["razorpay_payment_id"],
            money_to_sub_unit(donation.amount),
            {"currency": donation.amount.currency.code},
        )
        donation.status = Donation.Status.SUCCESSFUL
        donation.save()

        payment, _ = Payment.objects.get_or_create(
            type=Payment.Type.DONATION,
            donation=donation,
            external_id=razorpay_payment["id"],
            creator_user=donation.creator_user,
            fan_user=donation.fan_user,
            defaults={
                "status": razorpay_payment["status"],
                "method": razorpay_payment["method"],
                "amount": money_from_sub_unit(
                    razorpay_payment["amount"], razorpay_payment["currency"]
                ),
            },
        )
        async_task(notify_donation, donation.pk)
        return payment


class Payout(BaseModel):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled"
        PROCESSED = "processed"
        SETTLED = "settled"

    payment = models.OneToOneField(
        "payments.Payment", on_delete=models.CASCADE, related_name="payout"
    )
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.SCHEDULED
    )

    amount = MoneyField(decimal_places=2, max_digits=7)
    bank_account = models.ForeignKey(
        "payments.BankAccount", on_delete=models.SET_NULL, null=True
    )

    external_id = models.CharField(max_length=255)

    @classmethod
    def for_payment(cls, payment):
        payout, _created = cls.objects.get_or_create(
            payment=payment,
            amount=deduct_platform_fee(payment.amount, payment.creator_user),
            bank_account=payment.creator_user.bank_accounts.first(),
        )
        if _created:
            payout.create_external()
        return payout

    def create_external(self):
        external_data = razorpay_client.payment.transfer(
            self.payment.external_id,
            {
                "transfers": [
                    {
                        "account": self.bank_account.external_id,
                        "amount": money_to_sub_unit(self.amount),
                        "currency": self.amount.currency.code,
                    }
                ],
            },
        )
        self.external_id = external_data["items"][0]["id"]
        self.save()


class BankAccount(BaseModel):
    class AccountType(models.TextChoices):
        PRIVATE_LIMITED = "Private Limited"
        PARTNERSHIP = "Partnership"
        PROPRIETORSHIP = "Proprietorship"
        INDIVIDUAL = "Individual"
        LLP = "LLP"

    class Status(models.TextChoices):
        CREATED = "created"
        PROCESSING = "processing"
        LINKED = "linked"

    beneficiary_user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.CREATED
    )

    account_name = models.CharField(max_length=255)

    account_number = models.CharField(max_length=255)
    account_type = models.CharField(
        max_length=32, choices=AccountType.choices, default=AccountType.INDIVIDUAL
    )
    ifsc = models.CharField(max_length=16)

    is_active = models.BooleanField(default=True)
    external_id = models.CharField(max_length=255)
