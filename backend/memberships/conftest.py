from decimal import Decimal
import pytest
from moneyed import Money, INR
from rest_framework.test import APIClient
from memberships.analytics.utils import register_metrics
from memberships.subscriptions.models import Membership, Subscription

from memberships.users.models import User
from memberships.users.tests.factories import UserFactory
from memberships.donations.models import Donation

from memberships.subscriptions.tests.factories import (
    TierFactory,
    MembershipFactory,
    PlanFactory,
    SubscriptionFactory,
)
from memberships.payments.tests.factories import BankAccountFactory
from dateutil.relativedelta import relativedelta
from django.utils import timezone


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture(autouse=True)
def setup_metrics():
    register_metrics()


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def creator_user() -> User:
    user = UserFactory(is_creator=True)
    TierFactory(creator_user=user, welcome_message="Thanks!")
    BankAccountFactory(beneficiary_user=user)
    return user


@pytest.fixture
def membership(creator_user, user) -> Membership:
    # create a draft membership
    membership = MembershipFactory(creator_user=creator_user, fan_user=user)
    plan = PlanFactory(tier=creator_user.tiers.get())
    subscription = SubscriptionFactory(
        plan=plan,
        membership=membership,
        creator_user=creator_user,
        fan_user=user,
        cycle_start_at=timezone.now(),
        cycle_end_at=timezone.now() + relativedelta(months=1),
    )
    membership.scheduled_subscription = subscription
    membership.save()
    return membership


@pytest.fixture
def active_membership(membership) -> Membership:
    subscription = membership.scheduled_subscription
    subscription.authenticate()
    subscription.activate()
    subscription.save()
    membership.refresh_from_db()
    return membership


@pytest.fixture
def membership_with_scheduled_change(
    active_membership, creator_user, user
) -> Membership:
    membership = active_membership
    # another subscription which is in scheduled state
    tier = TierFactory(
        creator_user=creator_user,
        amount=Money("200", INR),
        welcome_message="Thanks from future!",
    )
    plan = PlanFactory(
        tier=tier,
    )
    scheduled_subscription: Subscription = SubscriptionFactory(
        plan=plan,
        membership=membership,
        creator_user=creator_user,
        fan_user=user,
        cycle_start_at=timezone.now() + relativedelta(months=1),
        cycle_end_at=timezone.now() + relativedelta(months=2),
    )
    membership.scheduled_subscription = scheduled_subscription
    membership.save()
    membership.refresh_from_db()
    return membership


@pytest.fixture
def unpaid_donation(creator_user, user):
    return Donation.objects.create(
        external_id="ord_123",
        message="Hello, world",
        amount=Money(Decimal("100"), INR),
        creator_user=creator_user,
        fan_user=user,
    )


@pytest.fixture
def api_client():
    return APIClient()
