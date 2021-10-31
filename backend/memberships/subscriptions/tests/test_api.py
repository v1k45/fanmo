from dateutil.relativedelta import relativedelta
from django.utils import timezone
import pytest

from memberships.users.tests.factories import UserFactory
from memberships.subscriptions.models import Plan, Subscription
from memberships.payments.tests.factories import BankAccountFactory
from memberships.payments.models import BankAccount

pytestmark = pytest.mark.django_db


class TestSubscriptionFlow:
    def test_crud(self, api_client, user, mocker, time_machine):
        # mocks
        rzp_mock = mocker.patch(
            "memberships.subscriptions.models.razorpay_client.plan.create",
            return_value={"id": "fooBar123"},
        )
        # login
        api_client.force_authenticate(user)

        # list
        assert api_client.get("/api/tiers/").data["count"] == 0

        # create tier
        response = api_client.post(
            "/api/tiers/",
            {
                "name": "Standard",
                "amount": 100,
                "description": "Standard text",
                "welcome_message": "Hello standard!",
                "benefits": ["Private Posts", "Discord", "Private Streams"],
                "is_public": True,
            },
            format="json",
        )

        # tier create success
        assert response.status_code == 201
        assert api_client.get("/api/tiers/").data["count"] == 1

        # rzp payment plan
        tier_id = response.json()["id"]
        plan = Plan.objects.get(tier_id=tier_id, external_id="fooBar123")
        assert rzp_mock.mock.asser_called_once_with(
            {
                "period": 1,
                "interval": 1,
                "item": {
                    "name": "Standard",
                    "amount": 10_000,
                    "currency": "INR",
                    "notes": {
                        "external_id": plan.id,
                    },
                },
            }
        )

        # users cant see each other's tiers
        ramesh = UserFactory()
        api_client.force_authenticate(ramesh)
        assert api_client.get("/api/tiers/").data["count"] == 0

        # subscribe a tier
        response = api_client.post(
            "/api/subscriptions/",
            {
                "username": user.username,
                "amount": 100,
            },
        )
        assert response.status_code == 400
        assert (
            response.json()["non_field_errors"][0]["code"] == "cannot_accept_payments"
        )

        # create a bank account
        BankAccountFactory(beneficiary_user=user)

        # attempt subscribing again
        rzp_sub_mock = mocker.patch(
            "memberships.subscriptions.models.razorpay_client.subscription.create",
            return_value={"id": "sub_123"},
        )
        response = api_client.post(
            "/api/subscriptions/",
            {
                "username": user.username,
                "amount": 100,
            },
        )
        assert response.status_code == 201
        response_data = response.json()
        subscription_id = response_data["id"]
        assert rzp_sub_mock.called

        # check subscriptions
        response = api_client.get("/api/subscriptions/")
        response_data = response.json()
        assert response_data["count"] == 0

        # activate subscription
        subscription = Subscription.objects.get(
            id=subscription_id,
            external_id="sub_123",
            seller_user=user,
            buyer_user=ramesh,
        )
        subscription.authenticate()
        subscription.activate()
        subscription.save()

        # send email

        # check subscription again
        response = api_client.get("/api/subscriptions/")

        response_data = response.json()
        assert response_data["count"] == 1
        assert response_data["results"][0]["id"] == subscription_id

        # subscription detail
        response = api_client.get(f"/api/subscriptions/{subscription_id}/")

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["id"] == subscription_id
        assert response_data["seller_user"]["username"] == user.username
        assert response_data["tier"]["name"] == "Standard"

        # check creator subscription data
        api_client.force_authenticate(user)

        response = api_client.get("/api/subscriptions/")
        assert response.status_code == 200
        assert response.json()["count"] == 0

        response = api_client.get("/api/subscribers/")
        assert response.status_code == 200

        response_data = response.json()
        assert response_data["count"] == 1
        assert response_data["results"][0]["id"] == subscription_id
        assert response_data["results"][0]["buyer_user"]["username"] == ramesh.username
        assert response_data["results"][0]["tier"]["name"] == "Standard"

        # few days pass?
        time_machine.move_to(timezone.now() + relativedelta(days=3))

        # user decides to change plan to a lower amount
        api_client.force_authenticate(ramesh)
        rzp_plan_mock = mocker.patch(
            "memberships.subscriptions.models.razorpay_client.plan.create",
            return_value={"id": "plan_002"},
        )
        rzp_sub_update_mock = mocker.patch(
            "memberships.subscriptions.models.razorpay_client.subscription.post_url"
        )
        response = api_client.post(
            "/api/subscriptions/", {"username": user.username, "amount": 50}
        )
        assert response.status_code == 201
        assert response.data["amount"] == "50.00"
        assert response.data["status"] == "created"

        # todo: let ui know that this does not require payment authorization...
        assert rzp_plan_mock.called
        rzp_sub_update_mock.assert_called_once_with(
            "/subscriptions/sub_123/update",
            {"plan_id": "plan_002", "schedule_change_at": "cycle_end"},
        )
