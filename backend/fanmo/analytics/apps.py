from django.apps import AppConfig
from django.db.models.signals import post_migrate
from django.db.utils import ProgrammingError


class AnalyticsConfig(AppConfig):
    name = "fanmo.analytics"
    verbose_name = "Analytics"

    def ready(self):
        from fanmo.core.tasks import register_scheduled_tasks

        from .utils import register_metrics

        try:
            register_metrics()
            register_scheduled_tasks()
        except ProgrammingError:
            print(
                "Skipped metrics registration due to inconsitent DB state. "
                "This could likely happen during initial setup. The metrics will be registed post miration."
            )
            post_migrate.connect(lambda *_, **__: register_metrics(), sender=self)
            post_migrate.connect(
                lambda *_, **__: register_scheduled_tasks(), sender=self
            )
