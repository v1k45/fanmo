from django_fsm import can_proceed

from django.conf import settings
from django.utils import timezone

from dateutil.relativedelta import relativedelta
from memberships.subscriptions.models import Membership, Subscription


def refresh_membership(membership_id: int):
    """
    Refresh membership to reflect the correct states based on:
        - active status
        - tier
        - active subscription
        - scheduled subscription

    How does the refresh process work?
    1. Check if the currently active subscription has expired.
    """
    now = timezone.now()

    # Set a grace period?
    membership: Membership = Membership.objects.select_related(
        "tier", "active_subscription", "scheduled_subscription"
    ).get(id=membership_id)
    active_subscription: Subscription = membership.active_subscription
    if not membership.is_active:
        return

    expiration_date = active_subscription.cycle_end_at + relativedelta(
        days=settings.SUBSCRIPTION_GRACE_PERIOD_DAYS
    )
    # TODO: Move conditions to FSM?
    if expiration_date < now and can_proceed(active_subscription.halt):
        active_subscription.halt()
        active_subscription.save()
    elif active_subscription.cycle_end_at < now and can_proceed(
        active_subscription.start_renewal
    ):
        active_subscription.start_renewal()
        active_subscription.save()
