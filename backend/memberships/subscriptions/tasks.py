from django.db import transaction
from django_fsm import can_proceed
from django_q.tasks import async_task
from memberships.analytics.tasks import refresh_stats
from memberships.subscriptions.models import Membership, Subscription


@transaction.atomic
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
    active_subscription: Subscription = membership.active_subscription
    scheduled_subscription: Subscription = membership.scheduled_subscription

    if not active_subscription:
        return

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

    refresh_stats(active_subscription.creator_user_id)


def refresh_creator_memberships(creator_user_id):
    for membership_id in Membership.objects.filter(
        creator_user_id=creator_user_id
    ).values_list("id", flat=True):
        async_task(refresh_membership, membership_id)
