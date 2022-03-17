from django_fsm import can_proceed
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
    # TODO: Record an activity?
    # Set a grace period?
    membership: Membership = Membership.objects.select_for_update().get(
        id=membership_id
    )
    if not membership.is_active:
        return

    active_subscription: Subscription = membership.active_subscription
    scheduled_subscription: Subscription = membership.scheduled_subscription

    if can_proceed(active_subscription.halt):
        active_subscription.halt()
        active_subscription.save()

    elif can_proceed(active_subscription.cancel):
        active_subscription.cancel()
        active_subscription.save()

        if scheduled_subscription and can_proceed(scheduled_subscription.activate):
            scheduled_subscription.activate()
            scheduled_subscription.save()

    elif can_proceed(active_subscription.start_renewal):
        active_subscription.start_renewal()
        active_subscription.save()
