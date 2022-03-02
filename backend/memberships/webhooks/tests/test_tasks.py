import pytest
from django.utils import timezone
from dateutil.relativedelta import relativedelta
from memberships.conftest import membership
from memberships.webhooks.models import WebhookMessage

from memberships.subscriptions.tasks import refresh_membership
from memberships.webhooks.tasks import process_razorpay_webhook


pytestmark = pytest.mark.django_db


class TestProcessRazorpayWebhook:
    def test_subscription_pending(self, active_membership, time_machine):
        subscription = active_membership.active_subscription
        webhook_payload = {
            "event": "subscription.pending",
            "payload": {
                "subscription": {
                    "entity": {
                        "id": subscription.external_id,
                        "plan_id": subscription.plan.external_id,
                    }
                }
            },
        }
        webhook_message = WebhookMessage.objects.create(
            sender=WebhookMessage.Sender.RAZORPAY,
            external_id="rzp_001",
            payload=webhook_payload,
        )

        process_razorpay_webhook(webhook_message.id)
