import pytest
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from memberships.payments.models import BankAccount
from memberships.users.models import User
from memberships.payments.tests.factories import BankAccountFactory
from memberships.subscriptions.models import Membership, Plan, Subscription
from memberships.users.tests.factories import UserFactory

pytestmark = pytest.mark.django_db


class TestTierAPI:
    def test_create_tier(self, api_client, user):
        api_client.force_authenticate(user)

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


@pytest.mark.xfail
class TestSubscriptionFlow:
    def test_subscribe(self, api_client, user, mocker):
        # create a bank account
        BankAccountFactory(beneficiary_user=user)

        # users cant see each other's tiers
        ramesh = UserFactory()
        api_client.force_authenticate(ramesh)

        rzp_plan_mock = mocker.patch(
            "memberships.subscriptions.models.razorpay_client.plan.create",
            return_value={"id": "plan_123"},
        )
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

        print(response.json())
        assert response.status_code == 201
        response_data = response.json()

        # payment plan is created in rzp
        created_plan = Plan.objects.get(external_id="plan_123")
        rzp_plan_mock.assert_called_once_with(
            {
                "period": "monthly",
                "interval": 1,
                "item": {
                    "name": f"Custom (₹100.00) - {user.name}",
                    "amount": 10_000,
                    "currency": "INR",
                },
                "notes": {
                    "external_id": created_plan.id,
                },
            }
        )

        # subscription is created in rzp
        rzp_sub_mock.assert_called_once_with(
            {
                "plan_id": "plan_123",
                "total_count": 12,
                "notes": {"external_id": response_data["id"]},
            }
        )

    def xtest_crud(self, api_client, user, mocker, time_machine):
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
        assert rzp_mock.mock.assert_called_once_with(
            {
                "period": "monthly",
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
            "memberships.subscriptions.models.razorpay_client.subscription.patch_url"
        )
        response = api_client.post(
            "/api/subscriptions/", {"username": user.username, "amount": 50}
        )
        assert response.status_code == 201
        assert response.data["amount"] == "50.00"
        assert response.data["status"] == "authenticated"

        # todo: let ui know that this does not require payment authorization...
        assert rzp_plan_mock.called
        rzp_sub_update_mock.assert_called_once_with(
            "/subscriptions/sub_123",
            {"plan_id": "plan_002", "schedule_change_at": "cycle_end"},
        )


class TestMembershipFlow:
    def test_list_anonymous(self, membership, api_client):
        response = api_client.get("/api/memberships/")
        assert response.status_code == 200
        assert response.json()["count"] == 0

    def test_list(self, membership, api_client):
        api_client.force_authenticate(membership.fan_user)

        # unconfirmed memberships don't show up.
        response = api_client.get("/api/memberships/")
        assert response.status_code == 200
        assert response.json()["count"] == 0

        # activate the membership
        membership.is_active = True
        membership.active_subscription = membership.scheduled_subscription
        membership.scheduled_subsription = None
        membership.save()

        # unconfirmed memberships don't show up.
        response = api_client.get("/api/memberships/")
        assert response.status_code == 200
        assert response.json()["count"] == 1
        membership_json = response.json()["results"][0]
        assert membership_json["id"] == membership.id
        assert (
            membership_json["creator_user"]["username"]
            == membership.creator_user.username
        )
        assert membership_json["is_active"]

    def test_create_anonymous(self, creator_user, api_client, mocker):
        rzp_plan_mock = mocker.patch(
            "memberships.subscriptions.models.razorpay_client.plan.create",
            return_value={"id": "plan_123"},
        )
        rzp_sub_mock = mocker.patch(
            "memberships.subscriptions.models.razorpay_client.subscription.create",
            return_value={"id": "sub_123"},
        )

        tier = creator_user.tiers.first()
        response = api_client.post(
            "/api/memberships/",
            {
                "tier_id": tier.id,
                "creator_username": creator_user.username,
                "email": "peter@griffins.com",
            },
        )
        assert response.status_code == 201
        response_data = response.json()

        membership = Membership.objects.get(id=response_data["id"])
        # tier is set once the subscription is confirmed
        assert response_data["tier"] == None
        assert response_data["is_active"] is None
        assert response_data["creator_user"]["username"] == creator_user.username
        assert response_data["active_subscription"] == None
        assert response_data["scheduled_subscription"]["payment"] == {
            "payment_processor": "razorpay",
            "payment_payload": {
                "key": "rzp_test_key",
                "subscription_id": "sub_123",
                "name": f"{tier.name} - {creator_user.name}",
                "prefill": {"name": "peter", "email": "peter@griffins.com"},
                "notes": {"subscription_id": membership.scheduled_subscription_id},
            },
            "requires_payment": True,
        }

        # New user is created
        assert User.objects.filter(email="peter@griffins.com").exists()

        # payment plan is created in rzp
        created_plan = Plan.objects.get(external_id="plan_123")
        rzp_plan_mock.assert_called_once_with(
            {
                "period": "monthly",
                "interval": 1,
                "item": {
                    "name": f"{tier.name} - {creator_user.name}",
                    "amount": 100_00,
                    "currency": "INR",
                },
                "notes": {
                    "external_id": created_plan.id,
                },
            }
        )

        # subscription is created in rzp
        rzp_sub_mock.assert_called_once_with(
            {
                "plan_id": "plan_123",
                "total_count": 12,
                "notes": {"external_id": response_data["scheduled_subscription"]["id"]},
            }
        )

    def test_create(self, creator_user, user, api_client, mocker):
        rzp_plan_mock = mocker.patch(
            "memberships.subscriptions.models.razorpay_client.plan.create",
            return_value={"id": "plan_123"},
        )
        rzp_sub_mock = mocker.patch(
            "memberships.subscriptions.models.razorpay_client.subscription.create",
            return_value={"id": "sub_123"},
        )

        api_client.force_authenticate(user)
        tier = creator_user.tiers.first()
        response = api_client.post(
            "/api/memberships/",
            {
                "tier_id": tier.id,
                "creator_username": creator_user.username,
            },
        )
        assert response.status_code == 201
        response_data = response.json()

        membership = Membership.objects.get(id=response_data["id"])
        # tier is set once the subscription is confirmed
        assert response_data["tier"] == None
        assert response_data["is_active"] is None
        assert response_data["creator_user"]["username"] == creator_user.username
        assert response_data["active_subscription"] == None
        assert response_data["scheduled_subscription"]["payment"] == {
            "payment_processor": "razorpay",
            "payment_payload": {
                "key": "rzp_test_key",
                "subscription_id": "sub_123",
                "name": f"{tier.name} - {creator_user.name}",
                "prefill": {"name": user.name, "email": user.email},
                "notes": {"subscription_id": membership.scheduled_subscription_id},
            },
            "requires_payment": True,
        }

        # payment plan is created in rzp
        created_plan = Plan.objects.get(external_id="plan_123")
        rzp_plan_mock.assert_called_once_with(
            {
                "period": "monthly",
                "interval": 1,
                "item": {
                    "name": f"{tier.name} - {creator_user.name}",
                    "amount": 100_00,
                    "currency": "INR",
                },
                "notes": {
                    "external_id": created_plan.id,
                },
            }
        )

        # subscription is created in rzp
        rzp_sub_mock.assert_called_once_with(
            {
                "plan_id": "plan_123",
                "total_count": 12,
                "notes": {"external_id": response_data["scheduled_subscription"]["id"]},
            }
        )
