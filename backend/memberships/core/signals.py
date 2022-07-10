from django.dispatch import receiver
from ipware import get_client_ip
from simple_history.models import HistoricalRecords
from simple_history.signals import pre_create_historical_record


@receiver(pre_create_historical_record)
def add_history_ip_address(sender, **kwargs):
    history_instance = kwargs["history_instance"]
    history_instance.ip_address = None

    if getattr(HistoricalRecords.context, "request", None):
        history_instance.ip_address = get_client_ip(HistoricalRecords.context.request)[
            0
        ]
