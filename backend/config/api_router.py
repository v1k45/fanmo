import socket
import os
from ipware import get_client_ip
from dj_rest_auth.views import (
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
)
from django.http import JsonResponse
from django.urls.conf import include, path
from django.contrib.sites.models import Site
from django.core.cache import cache
from django.utils import timezone
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_extensions.routers import ExtendedSimpleRouter

from fanmo.donations.api.views import DonationViewSet
from fanmo.integrations.api.views import (
    IntegrationView,
    DiscordServerConnectView,
    DiscordUserConnectView,
)
from fanmo.payments.api.views import (
    BankAccountViewSet,
    PaymentViewSet,
    PayoutViewSet,
    BankAccountViewSet,
)

from fanmo.users.api.views import (
    FacebookLoginView,
    GoogleLoginView,
    OwnUserAPIView,
    UserViewSet,
    RegisterView,
    LoginView,
)
from fanmo.posts.api.views import CommentViewSet, PostViewSet
from fanmo.analytics.api.views import AnalyticsAPIView
from fanmo.memberships.api.views import (
    MembershipViewSet,
    SubscriptionViewSet,
    TierViewSet,
)
from fanmo.users.api.views import (
    CreatorActivityViewSet,
    LoginView,
    OwnUserAPIView,
    RegisterView,
    RequestEmailVerificationView,
    TOTPDeviceViewSet,
    UserViewSet,
    VerifyEmailView,
    PasswordResetView,
)
from fanmo.webhooks.views import razorpay_webhook


def api_meta(request):
    """
    API to return meta stuff, to be used for healthchecks and version indentification.
    """
    return JsonResponse({
        "host": socket.gethostname(),
        "time": timezone.now().isoformat(),
        "cache": cache.get("dummy", 1),
        "db": Site.objects.count(),
        "ip": get_client_ip(request)[0],
        "env": os.environ.get("BUILD_ENV", "UNKNOWN"),
        "build": {
            "version": os.environ.get("BUILD_VERSION", "UNKNOWN"),
            "time": os.environ.get("BUILD_TIMESTAMP", "UNKNOWN")
        }
    })


router = ExtendedSimpleRouter()
router.register("users", UserViewSet, basename="users")
router.register("activities", CreatorActivityViewSet, basename="activities")
router.register("tiers", TierViewSet, basename="tiers")
router.register("posts", PostViewSet, basename="posts")
router.register("comments", CommentViewSet, basename="comments")
router.register("memberships", MembershipViewSet, basename="memberships")
# TODO: Remove subscriptions API
router.register("subscriptions", SubscriptionViewSet, basename="subscriptions")
router.register("donations", DonationViewSet, basename="donations")
router.register("payments", PaymentViewSet, basename="payments")
router.register("payouts", PayoutViewSet, basename="payouts")
router.register("accounts", BankAccountViewSet, basename="bank_accounts")
router.register("mfa", TOTPDeviceViewSet, basename="mfa")

auth_patterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
    path("login/google/", GoogleLoginView.as_view(), name="google_login"),
    path("login/facebook/", FacebookLoginView.as_view(), name="facebook_login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("email/verify/", RequestEmailVerificationView.as_view(), name="email_verify"),
    path(
        "email/verify/confirm/", VerifyEmailView.as_view(), name="email_verify_confirm"
    ),
    path("password/change/", PasswordChangeView.as_view(), name="password_change"),
    path("password/reset/", PasswordResetView.as_view(), name="password_reset"),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]

integration_patterns = [
    path("", IntegrationView.as_view()),
    path("discord_server/", DiscordServerConnectView.as_view()),
    path("discord_user/", DiscordUserConnectView.as_view()),
]

app_name = "api"
urlpatterns = router.urls + [
    path("meta/", api_meta),
    path("me/", OwnUserAPIView.as_view(), name="me"),
    path("auth/", include(auth_patterns)),
    path("integrations/", include(integration_patterns)),
    path("webhooks/razorpay/", razorpay_webhook),
    path("stats/", AnalyticsAPIView.as_view(), name="analytics"),
    # docs
    path("", SpectacularSwaggerView.as_view(url_name="api:schema"), name="docs"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
]
