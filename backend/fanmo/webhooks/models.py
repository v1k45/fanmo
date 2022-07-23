from django.db import models

from fanmo.utils.models import BaseModel


class WebhookMessage(BaseModel):
    class Sender(models.TextChoices):
        RAZORPAY = "razorpay"

    sender = models.CharField(max_length=15, choices=Sender.choices)
    payload = models.JSONField()

    is_processed = models.BooleanField(default=False)
    external_id = models.CharField(max_length=255, unique=True)
