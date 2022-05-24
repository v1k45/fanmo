from django.apps import AppConfig


class AnalyticsConfig(AppConfig):
    name = "memberships.analytics"
    verbose_name = "Analytics"

    def ready(self):
        from .utils import register_metrics

        register_metrics()
