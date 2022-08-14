from decimal import Decimal

import pytest
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from moneyed import INR, Money

from fanmo.memberships.models import Membership, Plan, Subscription
from fanmo.memberships.tests.factories import TierFactory
from fanmo.payments.models import Payment
from fanmo.payments.tests.factories import BankAccountFactory
from fanmo.users.models import User
from fanmo.users.tests.factories import UserFactory

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

        # payments
        Payment.objects.create(
            creator_user=membership.creator_user,
            fan_user=membership.fan_user,
            amount=Money(Decimal("500"), INR),
            status=Payment.Status.CAPTURED,
            method=Payment.Method.UPI,
            type=Payment.Type.SUBSCRIPTION,
            subscription=membership.active_subscription,
        )
        Payment.objects.create(
            creator_user=membership.creator_user,
            fan_user=membership.fan_user,
            amount=Money(Decimal("500"), INR),
            status=Payment.Status.CAPTURED,
            method=Payment.Method.UPI,
            type=Payment.Type.SUBSCRIPTION,
            subscription=membership.active_subscription,
        )
        Payment.objects.create(
            creator_user=membership.creator_user,
            fan_user=membership.fan_user,
            amount=Money(Decimal("5"), INR),
            status=Payment.Status.REFUNDED,
            method=Payment.Method.UPI,
            type=Payment.Type.SUBSCRIPTION,
            subscription=membership.active_subscription,
        )

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
        assert membership_json["lifetime_amount"] == "1000.00"

    def test_create_anonymous(self, creator_user, api_client, mocker):
        rzp_plan_mock = mocker.patch(
            "fanmo.memberships.models.razorpay_client.plan.create",
            return_value={"id": "plan_123"},
        )
        rzp_sub_mock = mocker.patch(
            "fanmo.memberships.models.razorpay_client.subscription.create",
            return_value={"id": "sub_123"},
        )
        mocker.patch(
            "fanmo.users.adapters.AccountAdapter.generate_name",
            return_value="confused racoon",
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
            "processor": "razorpay",
            "payload": {
                "key": "rzp_test_key",
                "image": None,
                "subscription_id": "sub_123",
                "subscription_card_change": 0,
                "name": f"{tier.name} - {creator_user.name}",
                "prefill": {"name": "confused racoon", "email": "peter@griffins.com"},
                "notes": {"subscription_id": membership.scheduled_subscription_id},
                "theme": {"color": "#6266f1"},
            },
            "is_required": True,
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
                "total_count": 12 * 5,
                "notes": {"external_id": response_data["scheduled_subscription"]["id"]},
                "customer_notify": 0,
                "expire_by": int(
                    (
                        membership.scheduled_subscription.cycle_start_at
                        + relativedelta(hours=1)
                    ).timestamp()
                ),
            }
        )

    def test_create(self, creator_user, user, api_client, mocker):
        rzp_plan_mock = mocker.patch(
            "fanmo.memberships.models.razorpay_client.plan.create",
            return_value={"id": "plan_123"},
        )
        rzp_sub_mock = mocker.patch(
            "fanmo.memberships.models.razorpay_client.subscription.create",
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
            "processor": "razorpay",
            "payload": {
                "key": "rzp_test_key",
                "image": None,
                "subscription_id": "sub_123",
                "subscription_card_change": 0,
                "name": f"{tier.name} - {creator_user.name}",
                "prefill": {"name": user.name, "email": user.email},
                "notes": {"subscription_id": membership.scheduled_subscription_id},
                "theme": {"color": "#6266f1"},
            },
            "is_required": True,
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
                "total_count": 12 * 5,
                "notes": {"external_id": response_data["scheduled_subscription"]["id"]},
                "customer_notify": 0,
                "expire_by": int(
                    (
                        membership.scheduled_subscription.cycle_start_at
                        + relativedelta(hours=1)
                    ).timestamp()
                ),
            }
        )

    def test_cancel(self, api_client, active_membership, user, mocker):
        rzp_cancel_mock = mocker.patch(
            "fanmo.memberships.models.razorpay_client.subscription.cancel",
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

    def test_cancel_errors(
        self, api_client, active_membership, user, mocker, time_machine
    ):
        api_client.force_authenticate(user)
        mocker.patch(
            "fanmo.memberships.models.razorpay_client.subscription.cancel",
        )

        active_membership.active_subscription.schedule_to_cancel()
        active_membership.active_subscription.save()

        response = api_client.post(f"/api/memberships/{active_membership.id}/cancel/")
        assert response.status_code == 400
        assert response.json()["non_field_errors"][0]["code"] == "already_cancelled"

        time_machine.move_to(
            active_membership.active_subscription.cycle_end_at + relativedelta(days=1)
        )
        active_membership.active_subscription.cancel()
        active_membership.active_subscription.save()

        response = api_client.post(f"/api/memberships/{active_membership.id}/cancel/")
        assert response.status_code == 400
        assert response.json()["non_field_errors"][0]["code"] == "already_cancelled"

    def test_update(self, api_client, active_membership, mocker):
        rzp_plan_mock = mocker.patch(
            "fanmo.memberships.models.razorpay_client.plan.create",
            return_value={"id": "plan_456"},
        )
        rzp_sub_mock = mocker.patch(
            "fanmo.memberships.models.razorpay_client.subscription.patch_url",
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
        assert not scheduled_subscription["payment"]["is_required"]

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
            "fanmo.memberships.models.razorpay_client.plan.create",
            return_value={"id": "plan_456"},
        )
        mocker.patch(
            "fanmo.memberships.models.razorpay_client.subscription.patch_url",
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
            "fanmo.memberships.models.razorpay_client.plan.create",
            return_value={"id": "plan_456"},
        )
        rzp_sub_mock = mocker.patch(
            "fanmo.memberships.models.razorpay_client.subscription.create",
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
        assert scheduled_subscription["payment"]["is_required"]

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
                "total_count": 12 * 5,
                "start_at": int(
                    active_membership.scheduled_subscription.cycle_start_at.timestamp()
                ),
                "expire_by": int(
                    (
                        active_membership.scheduled_subscription.cycle_start_at
                        + relativedelta(hours=1)
                    ).timestamp()
                ),
                "notes": {"external_id": response_data["scheduled_subscription"]["id"]},
                "customer_notify": 0,
            }
        )

    def test_update_disallowed_for_creator(self, api_client, active_membership, mocker):
        api_client.force_authenticate(active_membership.creator_user)

        new_tier = TierFactory(
            name="Gold Members",
            creator_user=active_membership.creator_user,
            amount=Money(Decimal("500"), INR),
        )

        response = api_client.patch(
            f"/api/memberships/{active_membership.id}/", {"tier_id": new_tier.id}
        )
        assert response.status_code == 400
        assert response.json()["non_field_errors"][0]["code"] == "permission_denied"

    def test_giveaway_membership(self, api_client, creator_user, mocker):
        assert not Membership.objects.exists()

        api_client.force_authenticate(creator_user)
        response = api_client.post(
            "/api/memberships/giveaway/",
            [
                {
                    "tier_id": creator_user.tiers.get().pk,
                    "email": "foo.bar@chu.com",
                },
                {
                    "tier_id": creator_user.tiers.get().pk,
                    "email": "bam.baz@chu.com",
                },
            ],
        )
        assert response.status_code == 201

        membership = Membership.objects.get(id=response.json()[0]["id"])
        assert membership.creator_user == creator_user
        assert membership.fan_user.email == "foo.bar@chu.com"
        assert membership.tier.id == creator_user.tiers.get().pk
        assert membership.active_subscription.status == "active"
        assert (
            membership.active_subscription.cycle_end_at.date()
            == (timezone.now() + relativedelta(months=1)).date()
        )
        assert membership.is_active

        membership = Membership.objects.get(id=response.json()[1]["id"])
        assert membership.creator_user == creator_user
        assert membership.fan_user.email == "bam.baz@chu.com"
        assert membership.tier.id == creator_user.tiers.get().pk
        assert membership.active_subscription.status == "active"
        assert (
            membership.active_subscription.cycle_end_at.date()
            == (timezone.now() + relativedelta(months=1)).date()
        )
        assert membership.is_active


class TestSubscriptionAPI:
    def test_list(self, active_membership, api_client):
        response = api_client.get("/api/subscriptions/")
        assert response.status_code == 403

        api_client.force_authenticate(active_membership.creator_user)
        response = api_client.get("/api/subscriptions/")
        assert response.status_code == 200
        assert response.json()["count"] == 1
        assert (
            response.json()["results"][0]["id"]
            == active_membership.active_subscription.id
        )

        api_client.force_authenticate(active_membership.fan_user)
        response = api_client.get("/api/subscriptions/")
        assert response.status_code == 200
        assert response.json()["count"] == 1
        assert (
            response.json()["results"][0]["id"]
            == active_membership.active_subscription.id
        )

        new_user = UserFactory()
        api_client.force_authenticate(new_user)
        response = api_client.get("/api/subscriptions/")
        assert response.status_code == 200
        assert response.json()["count"] == 0

    def test_list_filter_membership_id(self, active_membership, api_client):
        api_client.force_authenticate(active_membership.creator_user)
        response = api_client.get(
            f"/api/subscriptions/?membership_id={active_membership.id}"
        )
        assert response.status_code == 200
        assert response.json()["count"] == 1
        assert (
            response.json()["results"][0]["id"]
            == active_membership.active_subscription.id
        )
