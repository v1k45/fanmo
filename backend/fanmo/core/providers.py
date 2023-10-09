from time import sleep
from django.core.mail import EmailMultiAlternatives, get_connection
from notifications.providers import BaseNotificationProvider

from fanmo.users.models import CreatorActivity


class EmailNotificationProvider(BaseNotificationProvider):
    name = "rich_email"

    @staticmethod
    def _get_email_message(payload):
        message = EmailMultiAlternatives()
        for key, value in payload.items():
            if key == "body_html":
                message.attach_alternative(value, "text/html")
            else:
                setattr(message, key, value)
        return message

    def send(self, payload):
        email_message = self._get_email_message(payload)
        email_message.send()

    def send_bulk(self, payloads):
        # split payloads into chunks of 10 and they send delay each chunk by 2 second
        chunks = [payloads[x : x + 10] for x in range(0, len(payloads), 10)]
        for chunk in chunks:
            conn = get_connection()
            conn.send_messages(
                [self._get_email_message(payload) for payload in chunk]
            )
            # this is to avoid hitting the rate limit
            sleep(2)


class CreatorActivityProvider(BaseNotificationProvider):
    name = "creator_activity"

    def send(self, payload):
        payload.save()

    def send_bulk(self, payloads):
        CreatorActivity.objects.bulk_create(payloads)
