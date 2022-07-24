from decimal import Decimal

import pytest
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from moneyed import INR, Money
from rest_framework.test import APIClient

from fanmo.analytics.utils import register_metrics
from fanmo.core.tasks import register_scheduled_tasks
from fanmo.donations.models import Donation
from fanmo.memberships.models import Membership, Subscription
from fanmo.memberships.tests.factories import (
    MembershipFactory,
    PlanFactory,
    SubscriptionFactory,
    TierFactory,
)
from fanmo.payments.models import BankAccount
from fanmo.payments.tests.factories import BankAccountFactory
from fanmo.users.models import User
from fanmo.users.tests.factories import UserFactory


@pytest.fixture(autouse=True)
def media_storage(settings, tmpdir):
    settings.MEDIA_ROOT = tmpdir.strpath


@pytest.fixture(autouse=True)
def initialize_helpers():
    register_metrics()
    register_scheduled_tasks()


@pytest.fixture
def user() -> User:
    return UserFactory()


@pytest.fixture
def creator_user() -> User:
    user = UserFactory(is_creator=True)
    TierFactory(creator_user=user, welcome_message="Thanks!")

    # mock internal approval.
    user.user_onboarding.is_creator_approved = True
    user.user_onboarding.save()

    user.user_preferences.is_accepting_payments = True
    user.user_preferences.save()

    BankAccountFactory(beneficiary_user=user, status=BankAccount.Status.LINKED)
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
