from django.apps import AppConfig


class PaymentsConfig(AppConfig):
    name = "memberships.payments"
    verbose_name = "Payments"

    def ready(self):
        try:
            import memberships.payments.signals  # noqa F401
        except ImportError:
            pass
