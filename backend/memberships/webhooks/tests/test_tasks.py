import pytest
from memberships.webhooks.models import WebhookMessage

from memberships.webhooks.tasks import process_razorpay_webhook


pytestmark = pytest.mark.django_db


class TestProcessRazorpayWebhook:
    def test_subscription_pending(self, active_membership, mocker):
        refresh_membership_mock = mocker.patch(
            "memberships.webhooks.tasks.refresh_membership"
        )
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
        refresh_membership_mock.assert_called_once_with(active_membership.id)

    def test_subscription_halted(self, active_membership, mocker):
        refresh_membership_mock = mocker.patch(
            "memberships.webhooks.tasks.refresh_membership"
        )
        subscription = active_membership.active_subscription
        webhook_payload = {
            "event": "subscription.halted",
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
        refresh_membership_mock.assert_called_once_with(active_membership.id)
