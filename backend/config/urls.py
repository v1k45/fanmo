from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.urls import include, path
from django.views import defaults as default_views
from django.views.generic import TemplateView


index_view = TemplateView.as_view(template_name="pages/home.html")


urlpatterns = [
    # Django Admin, use {% url 'admin:index' %}
    path(settings.ADMIN_URL, admin.site.urls),
    path("", index_view, name="home"),
    path("pricing", index_view, name="pricing"),
    path("privacy", index_view, name="privacy"),
    path("terms", index_view, name="terms"),
    path("refunds", index_view, name="refunds"),
    # authentication
    path("login/", index_view, name="account_login"),
    path("logout/", index_view, name="account_logout"),
    path("register/", index_view, name="account_signup"),
    path("auth/", index_view, name="auth_index"),
    path("auth/callback/", index_view, name="auth_callback"),
    path("auth/callback/facebook/", index_view, name="facebook_callback"),
    path("auth/callback/google/", index_view, name="google_callback"),
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
    path("sent-donations", index_view, name="sent-donations"),
    path("received-donations", index_view, name="received-donations"),
    path("members", index_view, name="members"),
    path("members/tiers", index_view, name="manage_tiers"),
    path("memberships", index_view, name="memberships"),
    path("earnings", index_view, name="earnings"),
    path("settings", index_view, name="settings"),
    # posts
    path("p/<post_slug>/<post_id>/", index_view, name="post_detail"),
    path("<username>", index_view, name="creator_page"),
    # API
    path("api/", include("config.api_router")),
    # Your stuff: custom urls includes go here
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

if settings.DEBUG:
    # Static file serving when using Gunicorn + Uvicorn for local web socket development
    urlpatterns += staticfiles_urlpatterns()

    # This allows the error pages to be debugged during development, just visit
    # these url in browser to see how these error pages look like.
    urlpatterns += [
        path(
            "400/",
            default_views.bad_request,
            kwargs={"exception": Exception("Bad Request!")},
        ),
        path(
            "403/",
            default_views.permission_denied,
            kwargs={"exception": Exception("Permission Denied")},
        ),
        path(
            "404/",
            default_views.page_not_found,
            kwargs={"exception": Exception("Page not Found")},
        ),
        path("500/", default_views.server_error),
    ]
    if "debug_toolbar" in settings.INSTALLED_APPS:
        import debug_toolbar

        urlpatterns = [path("__debug__/", include(debug_toolbar.urls))] + urlpatterns
