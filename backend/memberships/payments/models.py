from decimal import Decimal
from django.conf import settings
from django.core.exceptions import SuspiciousFileOperation
from django.db import models
from django_extensions.db.fields import RandomCharField
from django_fsm import FSMField
from djmoney.models.fields import MoneyField

from memberships.donations.models import Donation
from memberships.subscriptions.models import Subscription

from memberships.utils import razorpay_client
from memberships.utils.models import BaseModel
from memberships.utils.money import deduct_platform_fee, money_from_sub_unit


class Payment(BaseModel):
    class Type(models.TextChoices):
        DONATION = "donation"
        SUBSCRIPTION = "subscription"

    class Status(models.TextChoices):
        CREATED = "created"
        AUTHORIZED = "authorized"
        CAPTURED = "captured"
        REFUNDED = "refunded"
        FAILED = "failed"

    subscription = models.ForeignKey(
        "subscriptions.Subscription", on_delete=models.CASCADE, null=True
    )
    donation = models.ForeignKey(
        "donations.Donation", on_delete=models.CASCADE, null=True
    )

    seller_user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="received_payments"
    )
    buyer_user = models.ForeignKey("users.User", on_delete=models.CASCADE, null=True)

    status = FSMField(default=Status.CREATED, choices=Status.choices)
    type = models.CharField(max_length=16, choices=Type.choices)

    amount = MoneyField(max_digits=7, decimal_places=2)
    external_id = models.CharField(max_length=255)

    @classmethod
    def from_razorpay_response(cls, payload):
        pass

    @classmethod
    def from_razorpay_webhook(cls, payload):
        razorpay_client.utils.verify_payment_signature(payload)
        pass

    @classmethod
    def for_subscription(cls, subscription, payload):
        payment, _ = Payment.objects.get_or_create(
            type=Payment.Type.SUBSCRIPTION,
            subscription=subscription,
            status=Payment.Status.CAPTURED,
            amount=money_from_sub_unit(payload["amount"], payload["currency"]),
            external_id=payload["id"],
            seller=subscription.seller,
            buyer=subscription.buyer,
        )
        Payout.for_payment(payment)
        return payment

    @classmethod
    def capture_subscription(cls, payload):
        payload.update(
            {
                "razorpay_order_id": payload["razorpay_payment_id"],
                "razorpay_payment_id": payload["razorpay_subscription_id"],
            }
        )
        razorpay_client.utility.verify_payment_signature(payload)

        subscription = Subscription.objects.select_for_update().get(
            external_id=payload["razorpay_subscription_id"]
        )

        payment, _created = Payment.objects.get_or_create(
            type=Payment.Type.SUBSCRIPTION,
            subscription=subscription,
            amount=subscription.plan.amount,
            external_id=payload["razorpay_payment_id"],
            seller_user=subscription.seller_user,
            buyer_user=subscription.buyer_user,
            defaults={"status": Payment.Status.AUTHORIZED},
        )

        # fetch subscription?
        if _created:
            subscription.authenticate()
            subscription.save()

        # in background?
        # Payout.for_payment(payment)
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
            seller=donation.seller,
            buyer=donation.buyer,
        )

        razorpay_client.payments.capture(
            payment.external_id,
            payment.amount.get_amount_in_sub_unit(),
            {"currency": payment.amount.currency.code},
        )

        donation.state = Donation.STATE.completed
        donation.save()

        # in background?
        Payout.for_payment(payment)
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
        payout = cls.objects.create(
            payment=payment,
            amount=deduct_platform_fee(payment.amount, payment.seller),
        )
        payout.create_external()
        return payout

    def create_external(self):
        external_data = razorpay_client.payment.transfer(
            self.payment.external_id,
            {
                "transfers": [
                    {
                        "account": self.recipient.bank_account.external_id,
                        "amount": self.amount.get_amount_in_sub_unit(),
                        "currency": self.amount.currency.code,
                    }
                ],
            },
        )
        self.external_id = external_data["id"]
        self.save()


class BankAccount(BaseModel):
    class AccountType(models.TextChoices):
        PRIVATE_LIMITED = "Private Limited"
        PARTNERSHIP = "Partnership"
        PROPRIETORSHIP = "Proprietorship"
        INDIVIDUAL = "Individual"
        LLP = "LLP"

    class Status(models.TextChoices):
        PROCESSING = "processing"
        LINKED = "linked"

    beneficiary_user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    status = models.CharField(
        max_length=16, choices=Status.choices, default=Status.PROCESSING
    )

    account_name = models.CharField(max_length=255)
    mobile_number = models.CharField(max_length=10)

    account_number = models.CharField(max_length=255)
    account_type = models.CharField(
        max_length=32, choices=AccountType.choices, default=AccountType.INDIVIDUAL
    )
    beneficiary_name = models.CharField(max_length=255)
    ifsc = models.CharField(max_length=16)

    is_active = models.BooleanField(default=True)

    external_id = models.CharField(max_length=12)
