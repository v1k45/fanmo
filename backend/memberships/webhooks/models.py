from operator import sub
from django.db import models

from memberships.subscriptions.models import Subscription
from memberships.utils.models import BaseModel


class WebhookMessage(BaseModel):
    class Sender(models.TextChoices):
        RAZORPAY = "razorpay"

    sender = models.CharField(max_length=15, choices=Sender.choices)
    payload = models.JSONField()

    is_processed = models.BooleanField(default=False)
    external_id = models.CharField(max_length=255, unique=True)

    def process(self):
        pass

    def process_razorpay(self):
        event_name = self.payload["event"]

        # subscription is paid
        # update active status
        # create a payout
        if self.payload["event"] == "subscription.charged":
            # todo handle subscription with active ids?
            subscription = Subscription.objects.get(
                external_id=self.payload["subscription"]["id"]
            )
            subscription.renew()

        # subscription is failed
        # update active status
        elif self.payload["event"] == "subscription.pending":
            # todo handle subscription with active ids?
            subscription = Subscription.objects.get(
                external_id=self.payload["subscription"]["id"]
            )
            subscription.start_renewal()
            subscription.save()

        # subscription is halted
        # update active status
        elif self.payload["event"] == "subscription.halted":
            # todo handle subscription with active ids?
            subscription = Subscription.objects.get(
                external_id=self.payload["subscription"]["id"]
            )
            subscription.halt()
            subscription.save()

        # subscription is cancelled
        # update active status
        elif self.payload["event"] == "subscription.cancelled":
            # todo handle subscription with active ids?
            subscription = Subscription.objects.get(
                external_id=self.payload["subscription"]["id"]
            )
            subscription.cancel()

        # subscription is paused
        # update active status
        elif self.payload["event"] == "subscription.paused":
            # todo handle subscription with active ids?
            subscription = Subscription.objects.get(
                external_id=self.payload["subscription"]["id"]
            )
            subscription.pause()

        # subscription is resumed
        # update active status
        elif self.payload["event"] == "subscription.resumed":
            # todo handle subscription with active ids?
            subscription = Subscription.objects.get(
                external_id=self.payload["subscription"]["id"]
            )
            subscription.resume()

        # donation is paid
        # publish donation
        # create a payload
        elif self.payload["event"] == "order.paid":
            # todo handle subscription with active ids?
            subscription = Subscription.objects.get(
                external_id=self.payload["subscription"]["id"]
            )
            subscription.resume()
