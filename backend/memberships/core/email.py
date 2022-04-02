from notifications.utils import notify


def notify_new_member(membership):
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
