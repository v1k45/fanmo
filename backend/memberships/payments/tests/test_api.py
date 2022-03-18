from decimal import Decimal
from moneyed import Money, INR
from datetime import timedelta
import pytest
from razorpay.errors import SignatureVerificationError

from memberships.payments.models import BankAccount, Payment
from memberships.payments.tests.factories import BankAccountFactory
from memberships.subscriptions.models import Subscription
from memberships.subscriptions.tests.factories import (
    MembershipFactory,
    PlanFactory,
    SubscriptionFactory,
    TierFactory,
)

from dateutil.relativedelta import relativedelta
from django.utils import timezone


pytestmark = pytest.mark.django_db


class TestBankAccountFlow:
    def test_create(self, user, api_client):
        assert user.user_onboarding.is_bank_account_added == False

        api_client.force_authenticate(user)
        response = api_client.post(
            "/api/accounts/",
            {
                "account_name": "Ashok Kumar",
                "account_number": "12345",
                "account_type": "Individual",
                "ifsc": "ICICI0000123",
            },
        )
        assert response.status_code == 201
        response_data = response.json()
        assert BankAccount.objects.filter(id=response_data["id"]).exists()
        assert response_data == {
            "id": response_data["id"],
            "status": "created",
            "account_name": "Ashok Kumar",
            "account_number": "12345",
            "account_type": "Individual",
            "ifsc": "ICICI0000123",
        }

        user.refresh_from_db()
        assert user.user_onboarding.is_bank_account_added == True

    def test_create_does_not_allow_multiple(self, user, api_client):
        BankAccountFactory(beneficiary_user=user)
        api_client.force_authenticate(user)
        response = api_client.post(
            "/api/accounts/",
            {
                "account_name": "Ashok Kumar",
                "account_number": "00000",
                "account_type": "Individual",
                "ifsc": "SBI0000123",
            },
        )
        assert response.status_code == 400
        assert response.json() == {
            "non_field_errors": [
                {
                    "message": "Multiple bank accounts are not supported. Please contact support.",
                    "code": "permission_denied",
                }
            ]
        }

    def test_update(self, user, api_client):
        bank_account = BankAccountFactory(beneficiary_user=user)
        api_client.force_authenticate(user)
        response = api_client.patch(
            f"/api/accounts/{bank_account.id}/",
            {
                "account_name": "Ashok Kumar",
                "account_number": "00000",
                "account_type": "Individual",
                "ifsc": "SBI0000123",
            },
        )
        assert response.status_code == 200
        assert response.json() == {
            "id": bank_account.id,
            "status": "created",
            "account_name": "Ashok Kumar",
            "account_number": "00000",
            "account_type": "Individual",
            "ifsc": "SBI0000123",
        }

    @pytest.mark.parametrize(
        "status", [BankAccount.Status.PROCESSING, BankAccount.Status.LINKED]
    )
    def test_update_fails_on_linked_accounts(self, user, api_client, status):
        bank_account = BankAccountFactory(beneficiary_user=user, status=status)
        api_client.force_authenticate(user)
        response = api_client.patch(
            f"/api/accounts/{bank_account.id}/",
            {
                "account_name": "Ashok Kumar",
                "account_number": "00000",
                "account_type": "Individual",
                "ifsc": "SBI0000123",
            },
        )
        assert response.status_code == 400
        assert response.json() == {
            "non_field_errors": [
                {
                    "message": "You cannot make changes to a linked account. Please contact support.",
                    "code": "permission_denied",
                }
            ]
        }


class TestPaymentProcessingFlow:
    def test_process_subscription(self, membership, api_client, mocker):
        rzp_verify_mock = mocker.patch(
            "memberships.payments.models.razorpay_client.utility.verify_payment_signature",
            return_value=True,
        )

        subscription = membership.scheduled_subscription
        response = api_client.post(
            "/api/payments/",
            {
                "type": "subscription",
                "subscription_id": subscription.id,
                "processor": "razorpay",
                "payload": {
                    "razorpay_subscription_id": subscription.external_id,
                    "razorpay_payment_id": "pay_123",
                    "razorpay_signature": "sign123",
                },
            },
        )

        assert response.status_code == 201
        assert rzp_verify_mock.called

        membership.refresh_from_db()
        assert membership.is_active
        assert membership.active_subscription == subscription
        assert membership.scheduled_subscription is None
        payment = subscription.payments.all().get()
        assert payment.external_id == "pay_123"

    def test_process_future_subscription(
        self, membership_with_scheduled_change, api_client, mocker
    ):
        rzp_verify_mock = mocker.patch(
            "memberships.payments.models.razorpay_client.utility.verify_payment_signature",
            return_value=True,
        )
        rzp_cancel_mock = mocker.patch(
            "memberships.subscriptions.models.razorpay_client.subscription.cancel",
        )

        subscription = membership_with_scheduled_change.scheduled_subscription
        response = api_client.post(
            "/api/payments/",
            {
                "type": "subscription",
                "subscription_id": subscription.id,
                "processor": "razorpay",
                "payload": {
                    "razorpay_subscription_id": subscription.external_id,
                    "razorpay_payment_id": "pay_123",
                    "razorpay_signature": "sign123",
                },
            },
        )

        assert response.status_code == 201
        assert rzp_verify_mock.called

        membership = membership_with_scheduled_change
        membership.refresh_from_db()
        assert membership.is_active
        assert (
            membership.active_subscription.status
            == Subscription.Status.SCHEDULED_TO_CANCEL
        )
        assert (
            membership.scheduled_subscription.status
            == Subscription.Status.SCHEDULED_TO_ACTIVATE
        )

        payment = subscription.payments.all().get()
        # should payment be even recorded?
        assert payment.external_id == "pay_123"

        rzp_cancel_mock.assert_called_once_with(
            membership.active_subscription.external_id,
            {"cancel_at_cycle_end": 1},
        )

    def test_invalid_subscription_id(self, membership, api_client, mocker):
        mocker.patch(
            "memberships.payments.models.razorpay_client.utility.verify_payment_signature",
            side_effect=SignatureVerificationError,
        )

        subscription = membership.scheduled_subscription
        response = api_client.post(
            "/api/payments/",
            {
                "type": "subscription",
                "subscription_id": subscription.id,
                "processor": "razorpay",
                "payload": {
                    "razorpay_subscription_id": "sub_123",
                    "razorpay_payment_id": "pay_123",
                    "razorpay_signature": "sign123",
                },
            },
        )
        assert response.status_code == 400
        assert response.json()["non_field_errors"][0]["code"] == "subscription_mismatch"
        assert not subscription.payments.exists()

    def test_subscription_cannot_be_reprocessed(self, membership, api_client, mocker):
        mocker.patch(
            "memberships.payments.models.razorpay_client.utility.verify_payment_signature",
            return_value=True,
        )
        subscription = membership.scheduled_subscription
        payload = {
            "type": "subscription",
            "subscription_id": subscription.id,
            "processor": "razorpay",
            "payload": {
                "razorpay_subscription_id": subscription.external_id,
                "razorpay_payment_id": "pay_123",
                "razorpay_signature": "sign123",
            },
        }
        response = api_client.post("/api/payments/", payload)
        assert response.status_code == 201
        assert Payment.objects.filter(external_id="pay_123").exists()

        # upgrade the membership
        # this will create new subscription instance with the same external id.
        membership.refresh_from_db()
        assert membership.is_active
        assert membership.active_subscription.id == subscription.id
        assert membership.scheduled_subscription is None

        response = api_client.post("/api/payments/", payload)
        assert response.status_code == 400
        assert (
            response.json()["non_field_errors"][0]["code"]
            == "payment_already_processed"
        )

    def test_subscription_in_halted_cannot_be_reprocessed(
        self, membership, api_client, mocker, time_machine
    ):
        mocker.patch(
            "memberships.payments.models.razorpay_client.utility.verify_payment_signature",
            return_value=True,
        )

        subscription = membership.scheduled_subscription
        payload = {
            "type": "subscription",
            "subscription_id": subscription.id,
            "processor": "razorpay",
            "payload": {
                "razorpay_subscription_id": subscription.external_id,
                "razorpay_payment_id": "pay_123",
                "razorpay_signature": "sign123",
            },
        }
        response = api_client.post("/api/payments/", payload)
        assert response.status_code == 201
        payment = subscription.payments.all().get()
        assert payment.external_id == "pay_123"

        subscription.refresh_from_db()
        time_machine.move_to(subscription.cycle_end_at + relativedelta(days=4))
        subscription.halt()
        subscription.save()

        # replay the same request again.
        response = api_client.post("/api/payments/", payload)
        assert response.status_code == 400
        assert (
            response.json()["non_field_errors"][0]["code"]
            == "payment_already_processed"
        )

    def test_subscription_with_invalid_state(self, membership, api_client, mocker):
        mocker.patch(
            "memberships.payments.models.razorpay_client.utility.verify_payment_signature",
            return_value=True,
        )

        subscription: Subscription = membership.scheduled_subscription
        subscription.authenticate()
        subscription.save()
        payload = {
            "type": "subscription",
            "subscription_id": subscription.id,
            "processor": "razorpay",
            "payload": {
                "razorpay_subscription_id": subscription.external_id,
                "razorpay_payment_id": "pay_123",
                "razorpay_signature": "sign123",
            },
        }
        response = api_client.post("/api/payments/", payload)
        assert response.status_code == 400
        assert (
            response.json()["non_field_errors"][0]["code"]
            == "invalid_subscription_state"
        )

    def test_invalid_subscription_signature(self, membership, api_client, mocker):
        mocker.patch(
            "memberships.payments.models.razorpay_client.utility.verify_payment_signature",
            side_effect=SignatureVerificationError,
        )

        subscription = membership.scheduled_subscription
        response = api_client.post(
            "/api/payments/",
            {
                "type": "subscription",
                "subscription_id": subscription.id,
                "processor": "razorpay",
                "payload": {
                    "razorpay_subscription_id": subscription.external_id,
                    "razorpay_payment_id": "pay_123",
                    "razorpay_signature": "sign123",
                },
            },
        )
        assert response.status_code == 400
        assert response.json()["non_field_errors"][0]["code"] == "signature_mismatch"
        assert not subscription.payments.exists()
