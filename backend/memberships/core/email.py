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
