from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "memberships.core"
    verbose_name = "Core"

    def ready(self):
        import memberships.core.channels  # noqa
        import memberships.core.providers  # noqa
        import memberships.core.signals  # noqa
