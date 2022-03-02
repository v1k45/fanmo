import pytest
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

from memberships.webhooks.tasks import subscription_cancelled


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def creator_user() -> User:
    user = UserFactory(is_creator=True)
    TierFactory(seller_user=user)
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
def api_client():
    return APIClient()
