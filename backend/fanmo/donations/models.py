from django.db import models
from django_fsm import FSMField
from djmoney.models.fields import MoneyField
from simple_history.models import HistoricalRecords

from fanmo.utils import razorpay_client
from fanmo.utils.models import BaseModel, IPAddressHistoricalModel


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
                "amount": self.amount.get_amount_in_sub_unit(),
                "currency": self.amount.currency.code,
                "notes": {"donation_id": self.pk},
            }
        )
        self.external_id = external_data["id"]
        self.save()
