from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class MembershipsConfig(AppConfig):
    name = "fanmo.memberships"
    verbose_name = _("Memberships")

    def ready(self):
        try:
            import fanmo.memberships.signals  # noqa F401
        except ImportError:
            pass
