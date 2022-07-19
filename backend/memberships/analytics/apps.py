from django.apps import AppConfig
from django.db.utils import ProgrammingError
from django.db.models.signals import post_migrate


class AnalyticsConfig(AppConfig):
    name = "memberships.analytics"
    verbose_name = "Analytics"

    def ready(self):
        from .utils import register_metrics
        from memberships.core.tasks import register_scheduled_tasks

        try:
            register_metrics()
            register_scheduled_tasks()
        except ProgrammingError:
            print(
                "Skipped metrics registration due to inconsitent DB state. "
                "This could likely happen during initial setup. The metrics will be registed post miration."
            )
            post_migrate.connect(lambda *_, **__: register_metrics(), sender=self)
            post_migrate.connect(lambda *_, **__: register_scheduled_tasks(), sender=self)
