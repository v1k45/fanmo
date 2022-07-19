from decimal import Decimal

import pytest
from dateutil.relativedelta import relativedelta
from moneyed import INR, Money

from memberships.donations.models import Donation
from memberships.payments.models import Payment, Payout
from memberships.webhooks.models import WebhookMessage
from memberships.webhooks.tasks import process_razorpay_webhook

pytestmark = pytest.mark.django_db


class TestProcessRazorpayWebhook:
    def test_subscription_charged(self, membership, mocker):
        """
        When subscription.charged is received,
        the task should record the payment and scheduled a payout for the creator user.
        """
        transfer_mock = mocker.patch(
            "memberships.payments.models.razorpay_client.payment.transfer",
            return_value={"items": [{"id": "trf_123"}]},
        )

        subscription = membership.scheduled_subscription
        subscription.authenticate()
        subscription.save()
        webhook_payload = {
            "event": "subscription.charged",
            "payload": {
                "subscription": {
                    "entity": {
                        "id": subscription.external_id,
                        "plan_id": subscription.plan.external_id,
                        "current_end": subscription.cycle_end_at.timestamp(),
                    },
                },
                "payment": {
                    "entity": {
                        "id": "rzp_pay123",
                        "amount": 100_00,
                        "currency": "INR",
                        "method": "upi",
                        "status": "captured",
                    }
                },
            },
        }
        webhook_message = WebhookMessage.objects.create(
            sender=WebhookMessage.Sender.RAZORPAY,
            external_id="rzp_001",
            payload=webhook_payload,
        )

        process_razorpay_webhook(webhook_message.id)

        membership.refresh_from_db()
        assert membership.is_active
        assert membership.active_subscription.id == subscription.id
        assert membership.active_subscription.cycle_end_at == subscription.cycle_end_at
        assert membership.scheduled_subscription is None

        payment = Payment.objects.get(
            creator_user=membership.creator_user,
            fan_user=membership.fan_user,
        )
        assert payment.subscription == membership.active_subscription
        assert payment.amount.amount == Decimal("100")
        assert payment.amount_currency == "INR"
        assert payment.method == "upi"
        assert payment.status == "captured"

        payout = Payout.objects.get(payment=payment)
        assert payout.amount.amount == Decimal("95.10")
        assert payout.external_id == "trf_123"
        transfer_mock.assert_called_once_with(
            "rzp_pay123",
            {
                "transfers": [
                    {
                        "account": membership.creator_user.bank_accounts.first().external_id,
                        "amount": 95_10,
                        "currency": "INR",
                    }
                ]
            },
        )

    def test_subscription_charged_for_future_cycle(self, active_membership, mocker):
        """
        When subscription.charged is received for a pending subscription,
        the task should activate the membership, record the payment and scheduled a payout for the creator user.
        """
        transfer_mock = mocker.patch(
            "memberships.payments.models.razorpay_client.payment.transfer",
            return_value={"items": [{"id": "trf_123"}]},
        )

        subscription = active_membership.active_subscription
        next_cycle_at = subscription.cycle_end_at + relativedelta(months=1)
        webhook_payload = {
            "event": "subscription.charged",
            "payload": {
                "subscription": {
                    "entity": {
                        "id": subscription.external_id,
                        "plan_id": subscription.plan.external_id,
                        "current_end": next_cycle_at.timestamp(),
                    },
                },
                "payment": {
                    "entity": {
                        "id": "rzp_pay123",
                        "amount": 100_00,
                        "currency": "INR",
                        "method": "upi",
                        "status": "captured",
                    }
                },
            },
        }
        webhook_message = WebhookMessage.objects.create(
            sender=WebhookMessage.Sender.RAZORPAY,
            external_id="rzp_001",
            payload=webhook_payload,
        )

        process_razorpay_webhook(webhook_message.id)

        active_membership.refresh_from_db()
        assert active_membership.is_active
        assert active_membership.active_subscription.id == subscription.id
        assert (
            active_membership.active_subscription.cycle_end_at
            != subscription.cycle_end_at
        )
        assert active_membership.active_subscription.cycle_end_at == next_cycle_at

        payment = Payment.objects.get(
            creator_user=active_membership.creator_user,
            fan_user=active_membership.fan_user,
        )
        assert payment.subscription == active_membership.active_subscription
        assert payment.amount.amount == Decimal("100")
        assert payment.amount_currency == "INR"
        assert payment.method == "upi"
        assert payment.status == "captured"

        payout = Payout.objects.get(payment=payment)
        assert payout.amount.amount == Decimal("95.10")
        assert payout.external_id == "trf_123"
        transfer_mock.assert_called_once_with(
            "rzp_pay123",
            {
                "transfers": [
                    {
                        "account": active_membership.creator_user.bank_accounts.first().external_id,
                        "amount": 95_10,
                        "currency": "INR",
                    }
                ]
            },
        )

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

    def test_order_paid(self, creator_user, user, mocker):
        transfer_mock = mocker.patch(
            "memberships.payments.models.razorpay_client.payment.transfer",
            return_value={"items": [{"id": "trf_123"}]},
        )

        donation = Donation.objects.create(
            creator_user=creator_user,
            fan_user=user,
            amount=Money(Decimal("100"), INR),
            external_id="don_123",
            status=Donation.Status.SUCCESSFUL,
        )
        payment = Payment.objects.create(
            type=Payment.Type.DONATION,
            donation=donation,
            creator_user=creator_user,
            fan_user=user,
            amount=Money(Decimal("100"), INR),
            method=Payment.Status.CAPTURED,
        )
        webhook_payload = {
            "event": "order.paid",
            "payload": {
                "order": {
                    "entity": {
                        "id": donation.external_id,
                    },
                },
                "payment": {
                    "entity": {
                        "id": payment.external_id,
                        "amount": 100_00,
                        "currency": "INR",
                        "method": "upi",
                        "status": "captured",
                    }
                },
            },
        }
        webhook_message = WebhookMessage.objects.create(
            sender=WebhookMessage.Sender.RAZORPAY,
            external_id="rzp_001",
            payload=webhook_payload,
        )

        process_razorpay_webhook(webhook_message.id)

        payout = Payout.objects.get(payment=payment)
        assert payout.amount.amount == Decimal("95.10")
        assert payout.external_id == "trf_123"
        transfer_mock.assert_called_once_with(
            payment.external_id,
            {
                "transfers": [
                    {
                        "account": creator_user.bank_accounts.first().external_id,
                        "amount": 95_10,
                        "currency": "INR",
                    }
                ]
            },
        )

    def test_transfer_processed(self, creator_user, user):
        donation = Donation.objects.create(
            creator_user=creator_user,
            fan_user=user,
            amount=Money(Decimal("100"), INR),
            external_id="don_123",
            status=Donation.Status.SUCCESSFUL,
        )
        payment = Payment.objects.create(
            type=Payment.Type.DONATION,
            donation=donation,
            creator_user=creator_user,
            fan_user=user,
            amount=Money(Decimal("100"), INR),
            method=Payment.Status.CAPTURED,
        )
        payout = Payout.objects.create(
            payment=payment,
            status=Payout.Status.SCHEDULED,
            amount=Money(Decimal("95.10"), INR),
            bank_account=creator_user.bank_accounts.get(),
            external_id="trf_123",
        )
        webhook_payload = {
            "event": "transfer.processed",
            "payload": {
                "transfer": {
                    "entity": {
                        "id": payout.external_id,
                    },
                },
            },
        }
        webhook_message = WebhookMessage.objects.create(
            sender=WebhookMessage.Sender.RAZORPAY,
            external_id="rzp_001",
            payload=webhook_payload,
        )

        process_razorpay_webhook(webhook_message.id)

        payout = Payout.objects.get(payment=payment)
        assert payout.status == Payout.Status.PROCESSED

    def test_settlement_processed(self, creator_user, user, mocker):
        transfer_mock = mocker.patch(
            "memberships.payments.models.razorpay_client.transfer.all",
            return_value={"items": [{"id": "trf_123"}]},
        )

        donation = Donation.objects.create(
            creator_user=creator_user,
            fan_user=user,
            amount=Money(Decimal("100"), INR),
            external_id="don_123",
            status=Donation.Status.SUCCESSFUL,
        )
        payment = Payment.objects.create(
            type=Payment.Type.DONATION,
            donation=donation,
            creator_user=creator_user,
            fan_user=user,
            amount=Money(Decimal("100"), INR),
            method=Payment.Status.CAPTURED,
        )
        payout = Payout.objects.create(
            payment=payment,
            status=Payout.Status.SCHEDULED,
            amount=Money(Decimal("95.10"), INR),
            bank_account=creator_user.bank_accounts.get(),
            external_id="trf_123",
        )
        webhook_payload = {
            "event": "settlement.processed",
            "payload": {
                "settlement": {
                    "entity": {
                        "id": "setl_123",
                    },
                },
            },
        }
        webhook_message = WebhookMessage.objects.create(
            sender=WebhookMessage.Sender.RAZORPAY,
            external_id="rzp_001",
            payload=webhook_payload,
        )

        process_razorpay_webhook(webhook_message.id)

        payout = Payout.objects.get(payment=payment)
        assert payout.status == Payout.Status.SETTLED

        transfer_mock.assert_called_once_with({"recipient_settlement_id": "setl_123"})
