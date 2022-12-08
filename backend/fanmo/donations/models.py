from decimal import Decimal

from django.db import models
from django_fsm import FSMField
from djmoney.models.fields import MoneyField
from moneyed import INR
from simple_history.models import HistoricalRecords

from fanmo.donations.constants import DONATION_TIERS
from fanmo.utils import razorpay_client
from fanmo.utils.models import BaseModel, IPAddressHistoricalModel
from fanmo.utils.money import Money, money_to_sub_unit


class Donation(BaseModel):
    class Status(models.TextChoices):
        PENDING = "pending"
        FAILED = "failed"
        SUCCESSFUL = "successful"

    fan_user = models.ForeignKey("users.User", on_delete=models.CASCADE)
    creator_user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="donations_received"
    )

    message = models.TextField(blank=True, max_length=3000)
    status = FSMField(default=Status.PENDING, choices=Status.choices)

    amount = MoneyField(max_digits=7, decimal_places=2)
    external_id = models.CharField(max_length=255)
    history = HistoricalRecords(bases=[IPAddressHistoricalModel])

    is_hidden = models.BooleanField(default=False)

    def create_external(self):
        external_data = razorpay_client.order.create(
            {
                "amount": money_to_sub_unit(self.amount),
                "currency": self.amount.currency.code,
                "notes": {"donation_id": self.pk},
            }
        )
        self.external_id = external_data["id"]
        self.save()

    def tier(self):
        if not self.creator_user.user_preferences.enable_donation_tiers:
            return None

        return next(
            (t for t in reversed(DONATION_TIERS) if self.amount >= t["min_amount"]),
            None,
        )
