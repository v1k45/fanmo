from django.conf import settings
from django.template.loader import render_to_string
from notifications.channels import BaseNotificationChannel


class EmailNotificationChannel(BaseNotificationChannel):
    name = "email"
    providers = ["console", "rich_email"]

    def build_payload(self, provider):
        if self.context.get("bulk"):
            return [
                self._build_payload(recipient)
                for recipient in self.context["recipients"]
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
            payload["from_email"] = f"{email_label} {email_address}"
        return payload

    def render_template(self, suffix, format="txt", **context):
        return render_to_string(
            f"maizzle/{self.notification.action}_{suffix}.{format}",
            {
                "notification": self.notification,
                "obj": self.notification.obj,
                **context,
            },
        ).strip()
