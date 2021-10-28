from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class PostsConfig(AppConfig):
    name = "memberships.posts"
    verbose_name = _("Posts")

    def ready(self):
        try:
            import memberships.posts.signals  # noqa F401
        except ImportError:
            pass
