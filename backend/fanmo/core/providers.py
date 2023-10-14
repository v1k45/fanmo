from time import sleep
from django.core.mail import EmailMultiAlternatives
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
        send_count = 0
        for payload in payloads:
            email_message = self._get_email_message(payload)
            email_message.send()

            send_count += 1
            # sleep for 1 second after every 20 emails
            if send_count % 20 == 0:
                sleep(1)


class CreatorActivityProvider(BaseNotificationProvider):
    name = "creator_activity"

    def send(self, payload):
        payload.save()

    def send_bulk(self, payloads):
        CreatorActivity.objects.bulk_create(payloads)
