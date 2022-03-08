import pytest
from dateutil.relativedelta import relativedelta
from memberships.subscriptions.models import Subscription

from memberships.subscriptions.tasks import refresh_membership


pytestmark = pytest.mark.django_db


class TestMembershipTasks:
    def test_refresh_membership_unchanged(self, active_membership, time_machine):
        assert active_membership.is_active == True
        subscription: Subscription = active_membership.active_subscription
        assert subscription.status == Subscription.Status.ACTIVE

        time_machine.move_to(subscription.cycle_end_at)
        refresh_membership(active_membership.id)
        active_membership.refresh_from_db()

        assert active_membership.is_active == True
        subscription.refresh_from_db()
        assert subscription.status == Subscription.Status.ACTIVE

    def test_refresh_membership_to_pending(self, active_membership, time_machine):
        assert active_membership.is_active == True
        subscription: Subscription = active_membership.active_subscription
        assert subscription.status == Subscription.Status.ACTIVE

        time_machine.move_to(subscription.cycle_end_at + relativedelta(days=1))
        refresh_membership(active_membership.id)
        active_membership.refresh_from_db()

        assert active_membership.is_active == True
        subscription.refresh_from_db()
        assert subscription.status == Subscription.Status.PENDING

    def test_refresh_membership_to_halted(self, active_membership, time_machine):
        assert active_membership.is_active == True
        subscription: Subscription = active_membership.active_subscription
        assert subscription.status == Subscription.Status.ACTIVE

        time_machine.move_to(
            subscription.cycle_end_at + relativedelta(days=3, seconds=1)
        )
        refresh_membership(active_membership.id)
        active_membership.refresh_from_db()

        assert active_membership.is_active == False
        subscription.refresh_from_db()
        assert subscription.status == Subscription.Status.HALTED
