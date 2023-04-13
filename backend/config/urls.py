from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import path, include
from django.views.generic import RedirectView
from fanmo.core.sitemaps import sitemaps


from fanmo.core.views import index_view, page_view, post_view, post_image_proxy_view

urlpatterns = [
    # Django Admin, use {% url 'admin:index' %}
    path(
        f"{settings.ADMIN_URL}login/",
        RedirectView.as_view(url="/login/"),
        name="admin:login",
    ),
    path(settings.ADMIN_URL, admin.site.urls),
    path(
        "sitemap.xml",
        sitemap,
        {"sitemaps": sitemaps},
        name="django.contrib.sitemaps.views.sitemap",
    ),
    # API
    path("api/", include("config.api_router")),
    path("imageproxy/<image_uuid>/<image_size>.jpg", post_image_proxy_view, name="post_image_proxy"),
    path("", index_view, name="home"),
    path("pricing", index_view, name="pricing"),
    path("privacy", index_view, name="privacy"),
    path("terms", index_view, name="terms"),
    path("refunds", index_view, name="refunds"),
    path("brand", index_view, name="brand"),
    # authentication
    path("login/", index_view, name="account_login"),
    path("logout/", index_view, name="account_logout"),
    path("register/", index_view, name="account_signup"),
    path("auth/", index_view, name="auth_index"),
    path("auth/callback/", index_view, name="auth_callback"),
    path("auth/callback/facebook/", index_view, name="facebook_callback"),
    path("auth/callback/google/", index_view, name="google_callback"),
    path("auth/callback/discord/", index_view, name="discord_callback"),
    path("forgot-password", index_view, name="forgot_password"),
    path("set-password/<key>/", index_view, name="password_reset"),
    path("accept-invite/<key>/", index_view, name="account_invite"),
    path("reset/confirm/<uidb36>/<token>/", index_view, name="password_reset_confirm"),
    path("confirm/<key>/", index_view, name="email_verification"),
    # user area
    path("onboarding/role", index_view, name="onboarding_role"),
    path("onboarding/verify", index_view, name="onboarding_verify"),
    path("onboarding/profile-info", index_view, name="onboarding_profile_info"),
    path("onboarding/payment-info", index_view, name="onboarding_payment_info"),
    path("dashboard", index_view, name="creator_dashboard"),
    path("feed", index_view, name="feed"),
    path("sent-tips", index_view, name="sent-tips"),
    path("received-tips", index_view, name="received-tips"),
    path("members", index_view, name="members"),
    path("members/tiers", index_view, name="manage_tiers"),
    path("memberships", index_view, name="memberships"),
    path("earnings", index_view, name="earnings"),
    path("settings", index_view, name="settings"),
    # posts
    path("p/<post_slug>/<post_id>/", post_view, name="post_detail"),
    path("posts/<post_id>/edit", index_view, name="post_edit"),
    path("<username>", page_view, name="creator_page"),
    path("<username>/", RedirectView.as_view(pattern_name="creator_page")),
    # Your stuff: custom urls includes go here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler404 = "fanmo.core.views.handle_404"
handler403 = "fanmo.core.views.handle_403"
handler400 = "fanmo.core.views.handle_404"
handler500 = "fanmo.core.views.handle_500"

if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()
