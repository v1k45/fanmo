from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    name = "fanmo.payments"
    verbose_name = "Payments"

    def ready(self):
        try:
            import fanmo.payments.signals  # noqa F401
        except ImportError:
            pass
