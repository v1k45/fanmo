import pytest
from razorpay.errors import SignatureVerificationError
from memberships.conftest import membership

from memberships.payments.models import BankAccount
from memberships.payments.tests.factories import BankAccountFactory
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

        # replay the same request again.
        response = api_client.post("/api/payments/", payload)
        assert response.status_code == 400
        assert (
            response.json()["non_field_errors"][0]["code"]
            == "payment_already_processed"
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
