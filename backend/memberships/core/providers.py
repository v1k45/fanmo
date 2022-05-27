from django.core.mail import get_connection, EmailMultiAlternatives

from notifications.providers import BaseNotificationProvider


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
        messages = (self._get_email_message(payload) for payload in payloads)
        connection = get_connection()
        connection.send_messages(messages)