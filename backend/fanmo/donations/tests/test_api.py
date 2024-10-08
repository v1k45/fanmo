from decimal import Decimal

import pytest
from djmoney.money import Money
from moneyed import INR

from fanmo.donations.models import Donation
from fanmo.payments.models import Payment
from fanmo.posts.models import Reaction
from fanmo.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestDonationAPI:
    def test_lifetime_donation(self, api_client, creator_user, user):
        donation = Donation.objects.create(
            creator_user=creator_user,
            fan_user=user,
            amount=Money(Decimal("100"), INR),
            status=Donation.Status.SUCCESSFUL,
        )
        Payment.objects.create(
            donation=donation,
            type=Payment.Type.DONATION,
            status=Payment.Status.CAPTURED,
            creator_user=creator_user,
            fan_user=user,
            amount=donation.amount,
        )

        donation_2 = Donation.objects.create(
            creator_user=creator_user,
            fan_user=user,
            amount=Money(Decimal("150"), INR),
            status=Donation.Status.SUCCESSFUL,
        )
        Payment.objects.create(
            donation=donation_2,
            type=Payment.Type.DONATION,
            status=Payment.Status.CAPTURED,
            creator_user=creator_user,
            fan_user=user,
            amount=donation_2.amount,
        )

        donation_3 = Donation.objects.create(
            creator_user=creator_user,
            fan_user=creator_user,
            amount=Money(Decimal("100"), INR),
            status=Donation.Status.SUCCESSFUL,
        )
        Payment.objects.create(
            donation=donation_3,
            type=Payment.Type.DONATION,
            status=Payment.Status.CAPTURED,
            creator_user=creator_user,
            fan_user=creator_user,
            amount=donation_3.amount,
        )

        donation_4 = Donation.objects.create(
            creator_user=user,
            fan_user=user,
            amount=Money(Decimal("50"), INR),
            status=Donation.Status.SUCCESSFUL,
        )
        Payment.objects.create(
            donation=donation_4,
            type=Payment.Type.DONATION,
            status=Payment.Status.CAPTURED,
            creator_user=user,
            fan_user=user,
            amount=donation_4.amount,
        )

        api_client.force_authenticate(creator_user)
        response = api_client.get(f"/api/donations/{donation.id}/")
        assert response.json()["lifetime_amount"] == "250.00"

        response = api_client.get(f"/api/donations/{donation_2.id}/")
        assert response.json()["lifetime_amount"] == "250.00"

        response = api_client.get(f"/api/donations/{donation_3.id}/")
        assert response.json()["lifetime_amount"] == "100.00"

        api_client.force_authenticate(user)
        response = api_client.get(f"/api/donations/{donation_4.id}/")
        assert response.json()["lifetime_amount"] == "50.00"

    def test_create_anonymous(self, api_client, creator_user, mocker):
        mocker.patch(
            "fanmo.donations.models.razorpay_client.order.create",
            return_value={"id": "ord_123"},
        )
        mocker.patch(
            "fanmo.users.adapters.AccountAdapter.generate_name",
            return_value="confused racoon",
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
        assert response_data["fan_user"]["username"] == "confused_racoon"
        assert response_data["creator_user"]["username"] == creator_user.username
        assert response_data["amount"] == "100.00"
        assert response_data["payment"] == {
            "processor": "razorpay",
            "payload": {
                "key": "rzp_test_key",
                "image": None,
                "order_id": "ord_123",
                "name": creator_user.name,
                "prefill": {"name": "confused racoon", "email": "fan@example.com"},
                "notes": {"donation_id": response_data["id"]},
                "theme": {"color": "#6266f1"},
            },
            "is_required": True,
        }

    def test_create(self, api_client, creator_user, user, mocker):
        mocker.patch(
            "fanmo.donations.models.razorpay_client.order.create",
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
        assert response_data["tier"] is None
        assert response_data["amount"] == "100.00"
        assert response_data["payment"] == {
            "processor": "razorpay",
            "payload": {
                "key": "rzp_test_key",
                "image": None,
                "order_id": "ord_123",
                "name": creator_user.name,
                "prefill": {"name": user.display_name, "email": user.email},
                "notes": {"donation_id": response_data["id"]},
                "theme": {"color": "#6266f1"},
            },
            "is_required": True,
        }

    def test_create_minimum_amount(self, api_client, creator_user, user, mocker):
        mocker.patch(
            "fanmo.donations.models.razorpay_client.order.create",
            return_value={"id": "ord_123"},
        )

        api_client.force_authenticate(user)
        response = api_client.post(
            "/api/donations/",
            {
                "creator_username": creator_user.username,
                "message": "Some fancy text goes here!",
                "amount": "9",
            },
        )
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["non_field_errors"][0]["code"] == "min_amount"

    def test_create_with_donation_tier_enabled_does_not_allow_messages_for_small_donation(
        self, api_client, creator_user, user, mocker
    ):
        # enable donation tier
        creator_user.user_preferences.enable_donation_tiers = True
        creator_user.user_preferences.save()

        mocker.patch(
            "fanmo.donations.models.razorpay_client.order.create",
            return_value={"id": "ord_123"},
        )

        api_client.force_authenticate(user)
        response = api_client.post(
            "/api/donations/",
            {
                "creator_username": creator_user.username,
                "message": "Some fancy text goes here!",
                "amount": "49",
            },
        )
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["non_field_errors"][0]["code"] == "min_tier"

    def test_create_with_donation_tier_enabled_validate_message_length_for_amount(
        self, api_client, creator_user, user, mocker
    ):
        # enable donation tier
        creator_user.user_preferences.enable_donation_tiers = True
        creator_user.user_preferences.save()

        mocker.patch(
            "fanmo.donations.models.razorpay_client.order.create",
            return_value={"id": "ord_123"},
        )

        api_client.force_authenticate(user)
        response = api_client.post(
            "/api/donations/",
            {
                "creator_username": creator_user.username,
                "message": "na" * 100,
                "amount": "99",
            },
        )
        assert response.status_code == 400
        response_data = response.json()
        assert response_data["non_field_errors"][0]["code"] == "invalid_tier"

    def test_update_as_creator(self, api_client, creator_user, user):
        donation = Donation.objects.create(
            fan_user=user,
            creator_user=creator_user,
            amount=Money(Decimal("100"), INR),
            message="Hello world!",
            status=Donation.Status.SUCCESSFUL,
        )
        api_client.force_authenticate(creator_user)

        response = api_client.patch(
            f"/api/donations/{donation.id}/",
            {
                "message": "This change shouldn't reflect!",
                "amount": "500",
                "is_hidden": True,
            },
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["message"] == "Hello world!"
        assert response_data["amount"] == "100.00"
        assert response_data["is_hidden"]

        response = api_client.patch(
            f"/api/donations/{donation.id}/",
            {
                "message": "This change shouldn't reflect!",
                "amount": "500",
                "is_hidden": False,
            },
        )
        assert response.status_code == 200
        response_data = response.json()
        assert response_data["message"] == "Hello world!"
        assert response_data["amount"] == "100.00"
        assert not response_data["is_hidden"]

    def test_update_as_fan(self, api_client, creator_user, user):
        donation = Donation.objects.create(
            fan_user=user,
            creator_user=creator_user,
            amount=Money(Decimal("100"), INR),
            message="Hello world!",
            status=Donation.Status.SUCCESSFUL,
        )
        api_client.force_authenticate(user)

        response = api_client.patch(
            f"/api/donations/{donation.id}/",
            {
                "message": "This change shouldn't reflect!",
                "amount": "500",
                "is_hidden": True,
            },
        )
        assert response.status_code == 403
        response_data = response.json()
        assert response_data["detail"]["code"] == "permission_denied"

    def test_add_reactions(self, api_client, donation):
        user = UserFactory()
        api_client.force_authenticate(user)

        response = api_client.post(
            f"/api/donations/{donation.id}/reactions/",
            {
                "action": "add",
                "emoji": "heart",
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["reactions"] == [
            {
                "count": 1,
                "is_reacted": True,
                "emoji": Reaction.Emoji.HEART.value,
            }
        ]

    def test_remove_reactions(self, api_client, donation):
        user = UserFactory()
        api_client.force_authenticate(user)

        Reaction.objects.create(
            author_user=user, emoji=Reaction.Emoji.HEART, donation=donation
        )

        response = api_client.post(
            f"/api/donations/{donation.id}/reactions/",
            {"action": "remove", "emoji": "heart"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["reactions"] == []
