from django.db.models import Q
from notifications.utils import notify
from memberships.core.models import NotificationType


def notify_new_membership(membership_id):
    from memberships.subscriptions.models import Membership

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
    from memberships.subscriptions.models import Membership

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
    from memberships.subscriptions.models import Membership

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
    from memberships.subscriptions.models import Membership

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
    from memberships.subscriptions.models import Membership

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
    from memberships.subscriptions.models import Membership

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
    from memberships.donations.models import Donation

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
    from memberships.users.models import User
    from memberships.posts.models import Post

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
    from memberships.posts.models import Comment

    # do not send notification if the commentor is same as post author
    comment = Comment.objects.get(id=comment_id)
    if comment.post.author_user_id == comment.author_user_id:
        return

    notify(
        recipient=comment.post.author_user,
        obj=comment,
        action=NotificationType.COMMENT,
        silent=True,
        channels=("email", "creator_activity"),
    )
    parent_comment = comment.parent
    if parent_comment and parent_comment.author_user_id != comment.author_user_id:
        notify(
            recipient=comment.author_user,
            obj=comment,
            action=NotificationType.COMMENT_REPLY,
            silent=True,
            channels=("email",),
        )
