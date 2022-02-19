import pytest

from memberships.payments.models import BankAccount
from memberships.payments.tests.factories import BankAccountFactory


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
