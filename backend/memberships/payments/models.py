from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone
from django_fsm import FSMField, can_proceed
from djmoney.models.fields import MoneyField

from memberships.donations.models import Donation
from memberships.subscriptions.models import Subscription
from memberships.utils import razorpay_client
from memberships.utils.models import BaseModel
from memberships.utils.money import deduct_platform_fee, money_from_sub_unit


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
        "subscriptions.Subscription", on_delete=models.CASCADE, null=True, blank=True
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
        if can_proceed(subscription.activate):
            subscription.activate()
        else:
            subscription.schedule_to_activate()
        subscription.save()

        # TODO: figure out what to with authentication payments.
        # make sure payment is not already processed?
        # allow soft reprocessing if it is for real local subscription.
        payment, _ = Payment.objects.get_or_create(
            type=Payment.Type.SUBSCRIPTION,
            subscription=subscription,
            amount=subscription.plan.amount,
            # payment id is stored in order_id field of subscription
            external_id=payload["razorpay_order_id"],
            creator_user=subscription.creator_user,
            fan_user=subscription.fan_user,
            defaults={"status": Payment.Status.CAPTURED},
        )
        return payment

    @classmethod
    def capture_donation(cls, payload):
        razorpay_client.utility.verify_payment_signature(payload)

        donation = Donation.objects.get(external_id=payload["razorpay_order_id"])

        payment, _ = Payment.objects.get_or_create(
            type=Payment.Type.DONATION,
            donation=donation,
            amount=donation.amount,
            external_id=payload["razorpay_payment_id"],
            creator_user=donation.creator_user,
            fan_user=donation.fan_user,
        )

        # not needed?
        razorpay_client.payment.capture(
            payment.external_id,
            payment.amount.get_amount_in_sub_unit(),
            {"currency": payment.amount.currency.code},
        )
        payment.status = Payment.Status.CAPTURED
        payment.save()

        donation.status = Donation.Status.SUCCESSFUL
        donation.save()
        return payment


class Payout(BaseModel):
    class Status(models.TextChoices):
        SCHEDULED = "scheduled"
        PROCESSED = "processed"

    payment = models.ForeignKey("payments.Payment", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.SCHEDULED
    )

    amount = MoneyField(decimal_places=2, max_digits=7)
    bank_account = models.ForeignKey("payments.BankAccount", on_delete=models.CASCADE)

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
                        "amount": self.amount.get_amount_in_sub_unit(),
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
