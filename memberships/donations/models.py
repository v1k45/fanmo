from django.db import models
from django_extensions.db.fields import RandomCharField
from djmoney.models.fields import MoneyField

from model_utils import Choices

from django_fsm import FSMField, transition
from razorpay.errors import SignatureVerificationError
from memberships.utils.models import BaseModel
from memberships.utils import razorpay_client


class Donation(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending"
        FAILED = "failed"
        SUCCESSFUL = "successful"

    sender_user = models.ForeignKey("users.User", on_delete=models.SET_NULL, null=True)
    receiver_user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="received_donations"
    )

    name = models.CharField(max_length=30, blank=True)
    message = models.TextField(blank=True, max_length=500)
    is_anonymous = models.BooleanField(default=False)

    status = FSMField(default=Status.PENDING, choices=Status.choices)

    amount = MoneyField(max_digits=7, decimal_places=2)
    external_id = models.CharField(max_length=12)

    def create_external(self):
        external_data = razorpay_client.orders.create(
            {
                "amount": self.amount.get_amount_in_subunit(),
                "currency": self.amount.currency.code,
            }
        )
        self.external_id = external_data["id"]
        self.save()
