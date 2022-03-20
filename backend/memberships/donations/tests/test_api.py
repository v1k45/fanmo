import pytest


pytestmark = pytest.mark.django_db


class TestDonationAPI:
    def test_create_anonymous(self, api_client, creator_user, mocker):
        mocker.patch(
            "memberships.donations.models.razorpay_client.order.create",
            return_value={"id": "ord_123"},
        )

        response = api_client.post(
            "/api/donations/",
            {
                "creator_username": creator_user.username,
                "message": "Some fancy text goes here!",
                "email": "fan@example.com",
                "amount": "100",
            },
        )
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["message"] == "Some fancy text goes here!"
        assert response_data["fan_user"]["username"] == "fan"
        assert response_data["creator_user"]["username"] == creator_user.username
        assert response_data["amount"] == "100.00"
        assert response_data["payment"] == {
            "processor": "razorpay",
            "payload": {
                "key": "rzp_test_key",
                "order_id": "ord_123",
                "name": creator_user.name,
                "prefill": {"name": "fan", "email": "fan@example.com"},
                "notes": {"donation_id": response_data["id"]},
            },
            "is_required": True,
        }

    def test_create(self, api_client, creator_user, user, mocker):
        mocker.patch(
            "memberships.donations.models.razorpay_client.order.create",
            return_value={"id": "ord_123"},
        )

        api_client.force_authenticate(user)
        response = api_client.post(
            "/api/donations/",
            {
                "creator_username": creator_user.username,
                "message": "Some fancy text goes here!",
                "amount": "100",
            },
        )
        assert response.status_code == 201
        response_data = response.json()
        assert response_data["message"] == "Some fancy text goes here!"
        assert response_data["fan_user"]["username"] == user.username
        assert response_data["creator_user"]["username"] == creator_user.username
        assert response_data["amount"] == "100.00"
        assert response_data["payment"] == {
            "processor": "razorpay",
            "payload": {
                "key": "rzp_test_key",
                "order_id": "ord_123",
                "name": creator_user.name,
                "prefill": {"name": user.display_name, "email": user.email},
                "notes": {"donation_id": response_data["id"]},
            },
            "is_required": True,
        }
