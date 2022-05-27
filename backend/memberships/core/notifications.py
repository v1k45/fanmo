from django.db.models import Q
from notifications.utils import notify
from django.utils import timezone


def notify_new_membership(membership_id):
    from memberships.subscriptions.models import Membership
    from memberships.users.models import CreatorActivity

    membership = Membership.objects.get(id=membership_id)

    notify(
        recipient=membership.creator_user,
        obj=membership,
        action="new_member",
        category="memberships",
        silent=True,
        channels=("email",),
    )
    CreatorActivity.objects.create(
        type=CreatorActivity.Type.NEW_MEMBERSHIP,
        membership=membership,
        data={"tier": {"id": membership.tier.id, "name": membership.tier.name}},
        message=f"{membership.fan_user.display_name} joined {membership.tier.name}",
        creator_user=membership.creator_user,
        fan_user=membership.fan_user,
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


def notify_membership_change(membership_id):
    from memberships.subscriptions.models import Membership
    from memberships.users.models import CreatorActivity

    membership = Membership.objects.get(id=membership_id)
    old_tier = membership.tier
    new_tier = membership.scheduled_subscription.plan.tier

    notify(
        recipient=membership.creator_user,
        obj=membership,
        action="member_change",
        category="memberships",
        silent=True,
        channels=("email",),
        extra_data={
            "context": {
                "old_tier": old_tier,
                "new_tier": new_tier,
            }
        },
    )
    CreatorActivity.objects.create(
        type=CreatorActivity.Type.MEMBERSHIP_UPDATE,
        membership=membership,
        data={
            "tier": {"id": old_tier.id, "name": old_tier.name},
            "new_tier": {"id": new_tier.id, "name": new_tier.name},
        },
        message=(
            f"{membership.fan_user.display_name} updated membership from {old_tier.name} to {new_tier.name}. "
            f"The change will go live on {membership.active_subscription.cycle_end_at:%d %b %Y}"
        ),
        creator_user=membership.creator_user,
        fan_user=membership.fan_user,
    )

    notify(
        source=membership.creator_user,
        recipient=membership.fan_user,
        obj=membership,
        action="membership_change",
        category="memberships",
        silent=True,  # Don't persist to the database
        channels=("email",),
        extra_data={
            "context": {"source_as_sender_name": True},
        },
    )


def notify_membership_stop(membership_id):
    from memberships.subscriptions.models import Membership
    from memberships.users.models import CreatorActivity

    membership = Membership.objects.get(id=membership_id)

    message = f"{membership.fan_user.display_name} has cancelled {membership.tier.name} membership."
    if membership.active_subscription.cycle_end_at > timezone.now():
        message += f" The change will go live on {membership.active_subscription.cycle_end_at:%d %b %Y}."

    CreatorActivity.objects.create(
        type=CreatorActivity.Type.MEMBERSHIP_STOP,
        membership=membership,
        message=message,
        creator_user=membership.creator_user,
        fan_user=membership.fan_user,
    )

    notify(
        source=membership.creator_user,
        recipient=membership.fan_user,
        obj=membership,
        action="membership_cancellation_scheduled",
        category="memberships",
        silent=True,  # Don't persist to the database
        channels=("email",),
        extra_data={
            "context": {"source_as_sender_name": True},
        },
    )


def notify_membership_pending(membership_id):
    from memberships.subscriptions.models import Membership
    from memberships.users.models import CreatorActivity

    membership = Membership.objects.get(id=membership_id)

    CreatorActivity.objects.create(
        type=CreatorActivity.Type.MEMBERSHIP_STOP,
        membership=membership,
        message=f"{membership.fan_user.display_name}'s {membership.tier.name} membership renewal failed. It will be retried on next working day.",
        creator_user=membership.creator_user,
        fan_user=membership.fan_user,
    )

    notify(
        source=membership.creator_user,
        recipient=membership.fan_user,
        obj=membership,
        action="membership_payment_failed",
        category="memberships",
        silent=True,  # Don't persist to the database
        channels=("email",),
        extra_data={
            "context": {"source_as_sender_name": True},
        },
    )


def notify_membership_halted(membership_id):
    from memberships.subscriptions.models import Membership
    from memberships.users.models import CreatorActivity

    membership = Membership.objects.get(id=membership_id)
    CreatorActivity.objects.create(
        type=CreatorActivity.Type.MEMBERSHIP_STOP,
        membership=membership,
        message=f"{membership.fan_user.display_name}'s {membership.tier.name} membership was cancelled due to non-payment.",
        creator_user=membership.creator_user,
        fan_user=membership.fan_user,
    )

    notify(
        source=membership.creator_user,
        recipient=membership.fan_user,
        obj=membership,
        action="membership_halted",
        category="memberships",
        silent=True,  # Don't persist to the database
        channels=("email",),
        extra_data={
            "context": {"source_as_sender_name": True},
        },
    )


def notify_donation(donation_id):
    from memberships.donations.models import Donation
    from memberships.users.models import CreatorActivity

    donation = Donation.objects.get(id=donation_id)

    notify(
        recipient=donation.creator_user,
        obj=donation,
        action="donation_received",
        category="donations",
        silent=True,
        channels=("email",),
    )
    CreatorActivity.objects.create(
        type=CreatorActivity.Type.DONATION,
        donation=donation,
        message=f"{donation.fan_user.display_name} donated {donation.amount}",
        creator_user=donation.creator_user,
        fan_user=donation.fan_user,
    )

    notify(
        recipient=donation.fan_user,
        obj=donation,
        action="donation_sent",
        category="donations",
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


def notify_comment(comment_id):
    from memberships.posts.models import Comment
    from memberships.users.models import CreatorActivity

    # do not send notification if the commentor is same as post author
    comment = Comment.objects.get(id=comment_id)
    if comment.post.author_user_id == comment.author_user_id:
        return

    notify(
        recipient=comment.post.author_user,
        obj=comment,
        action="comment",
        category="post",
        silent=True,
        channels=("email",),
    )
    CreatorActivity.objects.create(
        type=CreatorActivity.Type.COMMENT,
        comment=comment,
        message=f"{comment.author_user.display_name} commmented on {comment.post.title}",
        creator_user=comment.post.author_user,
        fan_user=comment.author_user,
    )
