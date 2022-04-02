from django.template.loader import render_to_string
from notifications.channels import BaseNotificationChannel


class EmailNotificationChannel(BaseNotificationChannel):
    name = "email"
    providers = ["console", "email"]

    def build_payload(self, provider):
        return {
            "to": [self.notification.recipient.email],
            "subject": self.get_subject(),
            "body": self.get_body(),
        }

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
