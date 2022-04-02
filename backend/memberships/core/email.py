from notifications.utils import notify


def notify_new_membership(membership):
    notify(
        recipient=membership.creator_user,
        obj=membership,
        action="new_member",
        category="memberships",
        silent=True,  # Don't persist to the database
        channels=("email",),
        extra_data={
            "context": {},  # Context for the specified Notification channels
        },
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
