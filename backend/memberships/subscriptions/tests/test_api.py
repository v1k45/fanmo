from decimal import Decimal
import pytest
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from moneyed import Money, INR

from memberships.users.models import User
from memberships.payments.tests.factories import BankAccountFactory
from memberships.subscriptions.models import Membership, Plan, Subscription
from memberships.users.tests.factories import UserFactory
from memberships.subscriptions.tests.factories import TierFactory


pytestmark = pytest.mark.django_db


class TestTierAPI:
    def test_create_tier(self, api_client, creator_user):
        api_client.force_authenticate(creator_user)

        assert api_client.get("/api/tiers/").data["count"] == 1

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

        assert response.status_code == 201

        assert api_client.get("/api/tiers/").data["count"] == 2

    def test_update_tier(self, api_client, creator_user):
        api_client.force_authenticate(creator_user)
        tier = creator_user.tiers.all().get()

        response = api_client.patch(
            f"/api/tiers/{tier.id}/",
            {
                "name": "Standard",
                "amount": 120,
            },
        )
        tier.refresh_from_db()

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["name"] == tier.name == "Standard"
        assert Decimal(response_data["amount"]) == tier.amount.amount == Decimal("120")

    def test_recommend_tier(self, api_client, creator_user):
        api_client.force_authenticate(creator_user)
        tier = creator_user.tiers.all().get()
        tier.is_recommended = True
        tier.save()

        response = api_client.post(
            "/api/tiers/",
            {
                "name": "Standard",
                "amount": 100,
                "benefits": ["Private Posts", "Discord", "Private Streams"],
                "is_recommended": True,
            },
        )
        assert response.status_code == 400
        assert response.json()["is_recommended"][0]["code"] == "recommended_tier_exists"

        another_tier = TierFactory(creator_user=creator_user)
        response = api_client.patch(
            f"/api/tiers/{another_tier.id}/",
            {
                "name": "Standard",
                "amount": 120,
                "is_recommended": True,
            },
        )

        assert response.status_code == 400
        assert response.json()["is_recommended"][0]["code"] == "recommended_tier_exists"


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

    def test_cancel(self, api_client, active_membership, user, mocker):
        rzp_cancel_mock = mocker.patch(
            "memberships.subscriptions.models.razorpay_client.subscription.cancel",
        )

        api_client.force_authenticate(user)

        assert active_membership.is_active
        assert (
            active_membership.active_subscription.status == Subscription.Status.ACTIVE
        )

        response = api_client.post(f"/api/memberships/{active_membership.id}/cancel/")
        assert response.status_code == 200

        assert (
            response.json()["active_subscription"]["status"]
            == Subscription.Status.SCHEDULED_TO_CANCEL
        )
        rzp_cancel_mock.assert_called_once_with(
            active_membership.active_subscription.external_id,
            {"cancel_at_cycle_end": 1},
        )
        active_membership.refresh_from_db()
        assert active_membership.is_active
        assert (
            active_membership.active_subscription.status
            == Subscription.Status.SCHEDULED_TO_CANCEL
        )

    def test_cancel_errors(self, api_client, active_membership, user, mocker):
        api_client.force_authenticate(user)
        mocker.patch(
            "memberships.subscriptions.models.razorpay_client.subscription.cancel",
        )

        active_membership.active_subscription.schedule_to_cancel()
        active_membership.active_subscription.save()

        response = api_client.post(f"/api/memberships/{active_membership.id}/cancel/")
        assert response.status_code == 400
        assert response.json()["non_field_errors"][0]["code"] == "already_cancelled"

        active_membership.active_subscription.cancel()
        active_membership.active_subscription.save()

        response = api_client.post(f"/api/memberships/{active_membership.id}/cancel/")
        assert response.status_code == 400
        assert response.json()["non_field_errors"][0]["code"] == "already_cancelled"

    def test_update(self, api_client, active_membership, mocker):
        rzp_plan_mock = mocker.patch(
            "memberships.subscriptions.models.razorpay_client.plan.create",
            return_value={"id": "plan_456"},
        )
        rzp_sub_mock = mocker.patch(
            "memberships.subscriptions.models.razorpay_client.subscription.patch_url",
            return_value={"id": "sub_456"},
        )

        api_client.force_authenticate(active_membership.fan_user)

        new_tier = TierFactory(
            name="Gold Members",
            creator_user=active_membership.creator_user,
            amount=Money(Decimal("500"), INR),
        )

        response = api_client.patch(
            f"/api/memberships/{active_membership.id}/", {"tier_id": new_tier.id}
        )
        assert response.status_code == 200
        response_data = response.json()

        assert response_data["is_active"]
        assert response_data["tier"]["id"] == active_membership.tier.id

        active_subscription = response_data["active_subscription"]
        assert active_subscription["status"] == Subscription.Status.SCHEDULED_TO_CANCEL
        assert active_subscription["tier"]["id"] == active_membership.tier.id

        scheduled_subscription = response_data["scheduled_subscription"]
        assert (
            scheduled_subscription["status"]
            == Subscription.Status.SCHEDULED_TO_ACTIVATE
        )
        assert scheduled_subscription["tier"]["id"] == new_tier.id
        assert not scheduled_subscription["payment"]["requires_payment"]

        created_plan = Plan.objects.get(external_id="plan_456")
        rzp_plan_mock.assert_called_once_with(
            {
                "period": "monthly",
                "interval": 1,
                "item": {
                    "name": f"{new_tier.name} - {new_tier.creator_user.name}",
                    "amount": 500_00,
                    "currency": "INR",
                },
                "notes": {
                    "external_id": created_plan.id,
                },
            }
        )

        # subscription is created in rzp
        rzp_sub_mock.assert_called_once_with(
            f"/subscriptions/{active_membership.active_subscription.external_id}",
            {"plan_id": "plan_456", "schedule_change_at": "cycle_end"},
        )

    def test_update_after_scheduling_an_update(
        self, api_client, active_membership, mocker
    ):
        mocker.patch(
            "memberships.subscriptions.models.razorpay_client.plan.create",
            return_value={"id": "plan_456"},
        )
        mocker.patch(
            "memberships.subscriptions.models.razorpay_client.subscription.patch_url",
            return_value={"id": "sub_456"},
        )

        api_client.force_authenticate(active_membership.fan_user)

        new_tier = TierFactory(
            name="Gold Members",
            creator_user=active_membership.creator_user,
            amount=Money(Decimal("500"), INR),
        )

        response = api_client.patch(
            f"/api/memberships/{active_membership.id}/", {"tier_id": new_tier.id}
        )
        assert response.status_code == 200
        response_data = response.json()

        scheduled_subscription = response_data["scheduled_subscription"]
        assert (
            scheduled_subscription["status"]
            == Subscription.Status.SCHEDULED_TO_ACTIVATE
        )
        assert scheduled_subscription["tier"]["id"] == new_tier.id

        # change the tier again.
        diamond_tier = TierFactory(
            name="Diamond Members",
            creator_user=active_membership.creator_user,
            amount=Money(Decimal("700"), INR),
        )

        response = api_client.patch(
            f"/api/memberships/{active_membership.id}/", {"tier_id": diamond_tier.id}
        )
        assert response.status_code == 400
        assert response.json()["non_field_errors"][0]["code"] == "already_scheduled"

    def test_update_upi_membership(self, api_client, active_membership, mocker):
        rzp_plan_mock = mocker.patch(
            "memberships.subscriptions.models.razorpay_client.plan.create",
            return_value={"id": "plan_456"},
        )
        rzp_sub_mock = mocker.patch(
            "memberships.subscriptions.models.razorpay_client.subscription.create",
            return_value={"id": "sub_456"},
        )

        # mock active subscription as UPI
        active_membership.active_subscription.payment_method = (
            Subscription.PaymentMethod.UPI
        )
        active_membership.active_subscription.save()

        api_client.force_authenticate(active_membership.fan_user)

        new_tier = TierFactory(
            name="Gold Members",
            creator_user=active_membership.creator_user,
            amount=Money(Decimal("500"), INR),
        )

        response = api_client.patch(
            f"/api/memberships/{active_membership.id}/", {"tier_id": new_tier.id}
        )
        assert response.status_code == 200
        response_data = response.json()
        active_membership.refresh_from_db()

        assert response_data["is_active"]
        assert response_data["tier"]["id"] == active_membership.tier.id

        # active subscription is not transitioned to "scheduled_to_cancel"
        # because the change subscription is not authenticated yet.
        active_subscription = response_data["active_subscription"]
        assert active_subscription["status"] == Subscription.Status.ACTIVE
        assert active_subscription["tier"]["id"] == active_membership.tier.id

        scheduled_subscription = response_data["scheduled_subscription"]
        assert scheduled_subscription["status"] == Subscription.Status.CREATED
        assert scheduled_subscription["tier"]["id"] == new_tier.id
        assert scheduled_subscription["payment"]["requires_payment"]

        created_plan = Plan.objects.get(external_id="plan_456")
        rzp_plan_mock.assert_called_once_with(
            {
                "period": "monthly",
                "interval": 1,
                "item": {
                    "name": f"{new_tier.name} - {new_tier.creator_user.name}",
                    "amount": 500_00,
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
                "plan_id": "plan_456",
                "total_count": 12,
                "start_at": active_membership.scheduled_subscription.cycle_start_at.timestamp(),
                "notes": {"external_id": response_data["scheduled_subscription"]["id"]},
            }
        )
