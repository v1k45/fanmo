import pytest
from moneyed import Money, INR
from rest_framework.test import APIClient
from memberships.subscriptions.models import Membership, Subscription

from memberships.users.models import User
from memberships.users.tests.factories import UserFactory

from memberships.subscriptions.tests.factories import (
    TierFactory,
    MembershipFactory,
    PlanFactory,
    SubscriptionFactory,
)
from dateutil.relativedelta import relativedelta
from django.utils import timezone


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture(autouse=True)
def bootstrap_oembed(mocker):
    mocker.patch("memberships.posts.integrations.micawber.bootstrap_oembed")


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def creator_user() -> User:
    user = UserFactory(is_creator=True)
    TierFactory(creator_user=user)
    return user


@pytest.fixture
def membership(creator_user, user) -> Membership:
    # create a draft membership
    membership = MembershipFactory(creator_user=creator_user, fan_user=user)
    plan = PlanFactory(
        seller_user=creator_user, buyer_user=user, tier=creator_user.tiers.get()
    )
    subscription = SubscriptionFactory(
        plan=plan,
        membership=membership,
        seller_user=creator_user,
        buyer_user=user,
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
    tier = TierFactory(creator_user=creator_user, amount=Money("200", INR))
    plan = PlanFactory(
        seller_user=creator_user,
        buyer_user=user,
        tier=tier,
    )
    scheduled_subscription = SubscriptionFactory(
        plan=plan,
        membership=membership,
        seller_user=creator_user,
        buyer_user=user,
        cycle_start_at=timezone.now() + relativedelta(months=1),
        cycle_end_at=timezone.now() + relativedelta(months=2),
    )
    membership.scheduled_subscription = scheduled_subscription
    membership.save()
    return membership


@pytest.fixture
def api_client():
    return APIClient()
