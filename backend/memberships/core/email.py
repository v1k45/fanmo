from django.db.models import Q
from notifications.utils import notify


def notify_new_membership(membership):
    notify(
        recipient=membership.creator_user,
        obj=membership,
        action="new_member",
        category="memberships",
        silent=True,
        channels=("email",),
    )

    notify(
        source=membership.creator_user,
        recipient=membership.fan_user,
        obj=membership,
        action="new_membership",
        category="memberships",
        silent=True,  # Don't persist to the database
        channels=("email",),
        extra_data={
            "context": {"source_as_sender_name": True},
        },
    )


def notify_donation(donation):
    notify(
        recipient=donation.creator_user,
        obj=donation,
        action="donation_received",
        category="donations",
        silent=True,
        channels=("email",),
    )

    notify(
        recipient=donation.fan_user,
        obj=donation,
        action="donation_sent",
        category="donations",
        silent=True,
        channels=("email",),
    )


def notify_new_post(post):
    from memberships.users.models import User

    creator_user = post.author_user
    recipients = (
        User.objects.filter(is_active=True)
        .filter(
            # users who are following the creator
            Q(followings=creator_user)
            # users who are member of the creator
            | Q(memberships__creator_user=creator_user, memberships__is_active=True)
        )
        .distinct()
    )
    notify(
        source=creator_user,
        obj=post,
        action="new_post",
        category="post",
        silent=True,
        channels=("email",),
        extra_data={
            "context": {
                "bulk": True,
                "recipients": recipients,
            }
        },
    )
