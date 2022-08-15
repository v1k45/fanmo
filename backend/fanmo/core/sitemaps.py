from django.contrib.sitemaps import Sitemap
from django.urls import reverse

from fanmo.posts.models import Post
from fanmo.users.models import User


class StaticViewSitemap(Sitemap):
    priority = 0.5
    changefreq = "weekly"

    def items(self):
        return [
            "home",
            "pricing",
            "terms",
            "privacy",
            "refunds",
            "account_login",
            "account_signup",
            "forgot_password",
        ]

    def location(self, item):
        return reverse(item)


class CreatorSitemap(Sitemap):
    changefreq = "daily"
    priority = 1.0

    def items(self):
        return User.objects.filter(is_active=True, is_creator=True)

    def lastmod(self, obj):
        return obj.updated_at


class PostSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.7

    def items(self):
        return Post.objects.filter(is_published=True)

    def lastmod(self, obj):
        return obj.updated_at


sitemaps = {
    "static": StaticViewSitemap,
    "users": CreatorSitemap,
    "posts": PostSitemap,
}
