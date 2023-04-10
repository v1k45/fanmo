from django.conf import settings
from django.template.loader import render_to_string
from django.utils import timezone
from notifications.channels import BaseNotificationChannel

from fanmo.users.models import CreatorActivity


class EmailNotificationChannel(BaseNotificationChannel):
    name = "email"
    providers = ["rich_email"]

    def build_payload(self, provider):
        if self.context.get("bulk"):
            return [
                self._build_payload(recipient)
                for recipient in self.context["recipients"]
                if self.can_send(recipient)
            ]
        return self._build_payload(self.notification.recipient)

    def _build_payload(self, recipient):
        payload = {
            "to": [recipient.email],
            "subject": self.render_template("subject", recipient=recipient),
            "body": self.render_template("message", recipient=recipient),
            "body_html": self.render_template(
                "message", format="html", recipient=recipient
            ),
        }
        if self.context.get("source_as_sender_name"):
            email_label = self.notification.source.display_name
            email_address = settings.DEFAULT_FROM_EMAIL_ADDRESS
            payload["from_email"] = f'"{email_label} (via Fanmo)" {email_address}'
        return payload

    def render_template(self, suffix, format="txt", **context):
        return render_to_string(
            f"maizzle/{self.notification.action}_{suffix}.{format}",
            {
                **self.context,
                "notification": self.notification,
                "obj": self.notification.obj,
                "settings": {"BASE_URL": settings.BASE_URL},
                **context,
            },
        ).strip()

    def notify(self, countdown=0):
        # skip sending notification if we user has disabled in preferences.
        if self.notification.recipient and not self.can_send(
            self.notification.recipient
        ):
            return
        return super().notify(countdown)

    def can_send(self, recipient):
        return recipient.user_preferences.can_send_email_notification(
            self.notification.action
        )


class CreatorActivityChannel(BaseNotificationChannel):
    name = "creator_activity"
    providers = ["creator_activity"]

    def build_payload(self, provider):
        obj_type = self.notification.obj._meta.model_name
        assert obj_type in [
            "membership",
            "donation",
            "comment",
        ], "Unsupported object type."
        return getattr(self, f"build_{self.notification.action}")(self.notification.obj)

    def build_new_member(self, membership):
        return CreatorActivity(
            type=CreatorActivity.Type.NEW_MEMBERSHIP,
            membership=membership,
            data={"tier": {"id": membership.tier.id, "name": membership.tier.name}},
            message=f"{membership.fan_user.display_name} joined {membership.tier.name}.",
            creator_user=membership.creator_user,
            fan_user=membership.fan_user,
        )

    def build_member_renew(self, membership):
        return CreatorActivity(
            type=CreatorActivity.Type.MEMBERSHIP_UPDATE,
            membership=membership,
            data={"tier": {"id": membership.tier.id, "name": membership.tier.name}},
            message=f"{membership.fan_user.display_name} renewed {membership.tier.name}.",
            creator_user=membership.creator_user,
            fan_user=membership.fan_user,
        )

    def build_member_change(self, membership):
        old_tier = membership.tier
        new_tier = membership.scheduled_subscription.plan.tier
        return CreatorActivity(
            type=CreatorActivity.Type.MEMBERSHIP_UPDATE,
            membership=membership,
            data={
                "tier": {"id": old_tier.id, "name": old_tier.name},
                "new_tier": {"id": new_tier.id, "name": new_tier.name},
                "effective_at": membership.scheduled_subscription.cycle_start_at,
            },
            message=(
                f"{membership.fan_user.display_name} updated membership from {old_tier.name} to {new_tier.name}. "
                f"The change will go live on {membership.scheduled_subscription.cycle_start_at:%d %b %Y}."
            ),
            creator_user=membership.creator_user,
            fan_user=membership.fan_user,
        )

    def build_member_cancellation_scheduled(self, membership):
        message = f"{membership.fan_user.display_name} has cancelled {membership.tier.name} membership."
        if membership.active_subscription.cycle_end_at > timezone.now():
            message += f" The change will go live on {membership.active_subscription.cycle_end_at:%d %b %Y}."

        return CreatorActivity(
            type=CreatorActivity.Type.MEMBERSHIP_STOP,
            membership=membership,
            data={
                "tier": {"id": membership.tier.id, "name": membership.tier.name},
                "effective_at": membership.active_subscription.cycle_end_at,
            },
            message=message,
            creator_user=membership.creator_user,
            fan_user=membership.fan_user,
        )

    def build_member_payment_failed(self, membership):
        return CreatorActivity.objects.create(
            type=CreatorActivity.Type.MEMBERSHIP_STOP,
            membership=membership,
            data={
                "tier": {"id": membership.tier.id, "name": membership.tier.name},
            },
            message=f"{membership.fan_user.display_name}'s {membership.tier.name} membership renewal failed. It will be retried on next working day.",
            creator_user=membership.creator_user,
            fan_user=membership.fan_user,
        )

    def build_member_halted(self, membership):
        return CreatorActivity(
            type=CreatorActivity.Type.MEMBERSHIP_STOP,
            membership=membership,
            data={
                "tier": {"id": membership.tier.id, "name": membership.tier.name},
            },
            message=f"{membership.fan_user.display_name}'s {membership.tier.name} membership was cancelled due to non-payment.",
            creator_user=membership.creator_user,
            fan_user=membership.fan_user,
        )

    def build_donation_received(self, donation):
        return CreatorActivity(
            type=CreatorActivity.Type.DONATION,
            donation=donation,
            message=f"{donation.fan_user.display_name} tipped {donation.amount}.",
            creator_user=donation.creator_user,
            fan_user=donation.fan_user,
        )

    def build_comment(self, comment):
        if comment.post:
            message = f"{comment.author_user.display_name} commmented on {comment.post.title}."
        else:
            message = f"{comment.author_user.display_name} commmented on their {comment.donation.amount} tip."

        return CreatorActivity(
            type=CreatorActivity.Type.COMMENT,
            comment=comment,
            message=message,
            creator_user=comment.creator_user,
            fan_user=comment.author_user,
        )
