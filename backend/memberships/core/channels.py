from django.conf import settings
from django.template.loader import render_to_string
from notifications.channels import BaseNotificationChannel


class EmailNotificationChannel(BaseNotificationChannel):
    name = "email"
    providers = ["console", "email"]

    def build_payload(self, provider):
        payload = {
            "to": [self.notification.recipient.email],
            "subject": self.get_subject(),
            "body": self.get_body(),
        }
        if self.context.get("source_as_sender_name"):
            email_label = self.notification.source.display_name
            email_address = settings.DEFAULT_FROM_EMAIL_ADDRESS
            payload["from_email"] = f"{email_label} {email_address}"
        return payload

    def get_subject(self):
        return render_to_string(
            f"email/{self.notification.action}_subject.txt",
            {"notification": self.notification},
        ).strip()

    def get_body(self):
        return render_to_string(
            f"email/{self.notification.action}_message.txt",
            {"notification": self.notification},
        ).strip()
