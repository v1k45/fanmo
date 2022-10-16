import pytest
from dateutil.relativedelta import relativedelta

from fanmo.memberships.models import Subscription
from fanmo.memberships.tasks import refresh_membership

pytestmark = pytest.mark.django_db


class TestMembershipTasks:
    def test_refresh_membership_unchanged(
        self, active_membership, time_machine, mocker
    ):
        assert active_membership.is_active == True
        subscription: Subscription = active_membership.active_subscription
        assert subscription.status == Subscription.Status.ACTIVE

        add_fan_to_discord_server_mock = mocker.patch(
            "fanmo.integrations.tasks.add_fan_to_discord_server"
        )
        remove_fan_from_discord_server_mock = mocker.patch(
            "fanmo.integrations.tasks.remove_fan_from_discord_server"
        )
        time_machine.move_to(subscription.cycle_end_at - relativedelta(days=2))
        refresh_membership(active_membership.id)
        active_membership.refresh_from_db()

        assert active_membership.is_active == True
        subscription.refresh_from_db()
        assert subscription.status == Subscription.Status.ACTIVE
        assert not add_fan_to_discord_server_mock.called
        assert not remove_fan_from_discord_server_mock.called

    def test_refresh_membership_to_pending(
        self, active_membership, time_machine, mocker
    ):
        assert active_membership.is_active == True
        subscription: Subscription = active_membership.active_subscription
        assert subscription.status == Subscription.Status.ACTIVE

        add_fan_to_discord_server_mock = mocker.patch(
            "fanmo.integrations.tasks.add_fan_to_discord_server"
        )
        remove_fan_from_discord_server_mock = mocker.patch(
            "fanmo.integrations.tasks.remove_fan_from_discord_server"
        )
        time_machine.move_to(subscription.cycle_end_at + relativedelta(days=1))
        refresh_membership(active_membership.id)
        active_membership.refresh_from_db()

        assert active_membership.is_active == True
        subscription.refresh_from_db()
        assert subscription.status == Subscription.Status.PENDING
        assert not add_fan_to_discord_server_mock.called
        assert not remove_fan_from_discord_server_mock.called

    def test_refresh_membership_to_halted(
        self, active_membership, time_machine, mocker
    ):
        assert active_membership.is_active == True
        subscription: Subscription = active_membership.active_subscription
        assert subscription.status == Subscription.Status.ACTIVE

        add_fan_to_discord_server_mock = mocker.patch(
            "fanmo.integrations.tasks.add_fan_to_discord_server"
        )
        remove_fan_from_discord_server_mock = mocker.patch(
            "fanmo.integrations.tasks.remove_fan_from_discord_server"
        )
        time_machine.move_to(
            subscription.cycle_end_at + relativedelta(days=3, seconds=1)
        )
        refresh_membership(active_membership.id)
        active_membership.refresh_from_db()

        assert active_membership.is_active == False
        subscription.refresh_from_db()
        assert subscription.status == Subscription.Status.HALTED
        assert not add_fan_to_discord_server_mock.called
        assert remove_fan_from_discord_server_mock.called

    def test_refresh_membership_upgrade(
        self, membership_with_scheduled_change, time_machine, mocker
    ):
        mocker.patch(
            "fanmo.memberships.models.razorpay_client.subscription.cancel",
        )

        active_membership = membership_with_scheduled_change
        active_subscription: Subscription = active_membership.active_subscription
        assert active_membership.is_active == True
        assert active_membership.tier == active_subscription.plan.tier

        # schedule the next subscription to activate.
        scheduled_subscription: Subscription = active_membership.scheduled_subscription
        scheduled_subscription.authenticate()
        scheduled_subscription.schedule_to_activate()
        scheduled_subscription.save()

        add_fan_to_discord_server_mock = mocker.patch(
            "fanmo.integrations.tasks.add_fan_to_discord_server"
        )
        remove_fan_from_discord_server_mock = mocker.patch(
            "fanmo.integrations.tasks.remove_fan_from_discord_server"
        )
        # move to active subscription's end time.
        time_machine.move_to(
            active_subscription.cycle_end_at + relativedelta(days=1, months=1)
        )
        refresh_membership(active_membership.id)
        active_membership.refresh_from_db()

        # membership has transitioned.
        assert active_membership.is_active == True
        assert active_membership.tier == scheduled_subscription.plan.tier
        assert active_membership.active_subscription.id == scheduled_subscription.id
        assert active_membership.scheduled_subscription is None
        assert remove_fan_from_discord_server_mock.called
        assert add_fan_to_discord_server_mock.called

    def test_refresh_membership_ignores_dangling_scheduled_subscription(
        self, membership_with_scheduled_change, time_machine, mocker
    ):
        mocker.patch(
            "fanmo.memberships.models.razorpay_client.subscription.cancel",
        )

        active_membership = membership_with_scheduled_change
        active_subscription: Subscription = active_membership.active_subscription
        assert active_membership.is_active == True
        assert active_membership.tier == active_subscription.plan.tier
        scheduled_subscription: Subscription = active_membership.scheduled_subscription

        add_fan_to_discord_server_mock = mocker.patch(
            "fanmo.integrations.tasks.add_fan_to_discord_server"
        )
        remove_fan_from_discord_server_mock = mocker.patch(
            "fanmo.integrations.tasks.remove_fan_from_discord_server"
        )
        # move to active subscription's end time.
        time_machine.move_to(
            active_subscription.cycle_end_at + relativedelta(days=1, months=1)
        )
        refresh_membership(active_membership.id)
        active_membership.refresh_from_db()

        # membership has transitioned.
        assert active_membership.is_active == False
        assert active_membership.tier == active_subscription.plan.tier
        assert active_membership.scheduled_subscription.id == scheduled_subscription.id
        assert not add_fan_to_discord_server_mock.called
        assert remove_fan_from_discord_server_mock.called
