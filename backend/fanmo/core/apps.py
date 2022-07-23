from django.apps import AppConfig


class CoreConfig(AppConfig):
    name = "fanmo.core"
    verbose_name = "Core"

    def ready(self):
        import fanmo.core.channels  # noqa
        import fanmo.core.providers  # noqa
        import fanmo.core.signals  # noqa
