from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class SubscriptionsConfig(AppConfig):
    name = "fanmo.subscriptions"
    verbose_name = _("Subcriptions")

    def ready(self):
        try:
            import fanmo.subcriptions.signals  # noqa F401
        except ImportError:
            pass
