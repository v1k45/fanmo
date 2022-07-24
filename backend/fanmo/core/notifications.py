import time

from django.db.models import Q
from notifications.utils import notify

from fanmo.core.models import NotificationType


def notify_new_membership(membership_id):
    from fanmo.memberships.models import Membership

    membership = Membership.objects.get(id=membership_id)

    notify(
        recipient=membership.creator_user,
        obj=membership,
        action=NotificationType.NEW_MEMBER,
        silent=True,
        channels=("email", "creator_activity"),
    )
    notify(
        source=membership.creator_user,
        recipient=membership.fan_user,
        obj=membership,
        action=NotificationType.NEW_MEMBERSHIP,
        silent=True,  # Don't persist to the database
        channels=("email",),
        extra_data={
            "context": {"source_as_sender_name": True},
        },
    )


def notify_membership_renewed(membership_id):
    from fanmo.memberships.models import Membership

    membership = Membership.objects.get(id=membership_id)

    notify(
        recipient=membership.creator_user,
        obj=membership,
        action=NotificationType.MEMBER_RENEW,
        silent=True,
        channels=("creator_activity",),
    )
    notify(
        source=membership.creator_user,
        recipient=membership.fan_user,
        obj=membership,
        action=NotificationType.MEMBERSHIP_RENEW,
        silent=True,  # Don't persist to the database
        channels=("email",),
        extra_data={
            "context": {"source_as_sender_name": True},
        },
    )


def notify_membership_change(membership_id):
    from fanmo.memberships.models import Membership

    membership = Membership.objects.get(id=membership_id)
    old_tier = membership.tier
    new_tier = membership.scheduled_subscription.plan.tier

    notify(
        recipient=membership.creator_user,
        obj=membership,
        action=NotificationType.MEMBER_CHANGE,
        silent=True,
        channels=("creator_activity",),
        extra_data={
            "context": {
                "old_tier": old_tier,
                "new_tier": new_tier,
            }
        },
    )
    notify(
        source=membership.creator_user,
        recipient=membership.fan_user,
        obj=membership,
        action=NotificationType.MEMBERSHIP_CHANGE,
        silent=True,  # Don't persist to the database
        channels=("email",),
        extra_data={
            "context": {"source_as_sender_name": True},
        },
    )


def notify_membership_stop(membership_id):
    from fanmo.memberships.models import Membership

    membership = Membership.objects.get(id=membership_id)

    notify(
        recipient=membership.creator_user,
        obj=membership,
        action=NotificationType.MEMBER_CANCELLATION_SCHEDULED,
        silent=True,
        channels=("creator_activity",),
    )
    notify(
        source=membership.creator_user,
        recipient=membership.fan_user,
        obj=membership,
        action=NotificationType.MEMBERSHIP_CANCELLATION_SCHEDULED,
        silent=True,  # Don't persist to the database
        channels=("email",),
        extra_data={
            "context": {"source_as_sender_name": True},
        },
    )


def notify_membership_pending(membership_id):
    from fanmo.memberships.models import Membership

    membership = Membership.objects.get(id=membership_id)

    notify(
        recipient=membership.creator_user,
        obj=membership,
        action=NotificationType.MEMBER_PAYMENT_FAILED,
        silent=True,
        channels=("creator_activity",),
    )
    notify(
        source=membership.creator_user,
        recipient=membership.fan_user,
        obj=membership,
        action=NotificationType.MEMBERSHIP_PAYMENT_FAILED,
        silent=True,  # Don't persist to the database
        channels=("email",),
        extra_data={
            "context": {"source_as_sender_name": True},
        },
    )


def notify_membership_halted(membership_id):
    from fanmo.memberships.models import Membership

    membership = Membership.objects.get(id=membership_id)
    notify(
        recipient=membership.creator_user,
        obj=membership,
        action=NotificationType.MEMBER_HALTED,
        silent=True,
        channels=("creator_activity",),
    )
    notify(
        source=membership.creator_user,
        recipient=membership.fan_user,
        obj=membership,
        action=NotificationType.MEMBERSHIP_HALTED,
        silent=True,  # Don't persist to the database
        channels=("email",),
        extra_data={
            "context": {"source_as_sender_name": True},
        },
    )


def notify_donation(donation_id):
    from fanmo.donations.models import Donation

    donation = Donation.objects.get(id=donation_id)

    notify(
        recipient=donation.creator_user,
        obj=donation,
        action=NotificationType.DONATION_RECEIVED,
        silent=True,
        channels=("email", "creator_activity"),
    )
    notify(
        recipient=donation.fan_user,
        obj=donation,
        action=NotificationType.DONATION_SENT,
        silent=True,
        channels=("email",),
    )


def notify_new_post(post_id):
    from fanmo.posts.models import Post
    from fanmo.users.models import User

    post = Post.objects.get(id=post_id)

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
        action=NotificationType.NEW_POST,
        silent=True,
        channels=("email",),
        extra_data={
            "context": {
                "bulk": True,
                "recipients": recipients,
            }
        },
    )


def notify_comment(comment_id):
    from fanmo.posts.models import Comment

    # do not send notification if the commentor is same as post author
    comment = Comment.objects.get(id=comment_id)
    if comment.post.author_user_id != comment.author_user_id:
        notify(
            recipient=comment.post.author_user,
            obj=comment,
            action=NotificationType.COMMENT,
            silent=True,
            channels=("email", "creator_activity"),
        )

    if comment.parent and comment.parent.author_user_id != comment.author_user_id:
        notify(
            recipient=comment.parent.author_user,
            obj=comment,
            action=NotificationType.COMMENT_REPLY,
            silent=True,
            channels=("email",),
        )


def notify_password_change(user_id, user_ip):
    from fanmo.users.models import User

    user = User.objects.get(id=user_id)
    notify(
        recipient=user,
        obj=user,
        action=NotificationType.PASSWORD_CHANGE,
        silent=True,
        channels=("email",),
        extra_data={
            "context": {
                "user_ip": user_ip,
            }
        },
    )


def notify_creator_approved(user_id):
    from fanmo.users.models import User

    user = User.objects.get(id=user_id)
    notify(
        recipient=user,
        obj=user,
        action=NotificationType.CREATOR_APPROVED,
        silent=True,
        channels=("email",),
    )
