from django.conf import settings
from django.urls.conf import include, path
from rest_framework.routers import DefaultRouter, SimpleRouter
from memberships.donations.api.views import DonationViewSet
from memberships.payments.api.views import PaymentViewSet, PayoutViewSet
from memberships.posts.api.views import PostViewSet

from memberships.users.api.views import OwnUserAPIView, UserViewSet
from memberships.subscriptions.api.views import (
    SubscriberViewSet,
    SubscriptionViewSet,
    TierViewSet,
)

from dj_rest_auth.views import (
    LoginView,
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from dj_rest_auth.registration.views import (
    RegisterView,
    VerifyEmailView,
    ResendEmailVerificationView,
)

from drf_spectacular.views import SpectacularSwaggerView, SpectacularAPIView


router = SimpleRouter()
router.register("users", UserViewSet, basename="users")
router.register("tiers", TierViewSet, basename="tiers")
router.register("posts", PostViewSet, basename="posts")
router.register("subscriptions", SubscriptionViewSet, basename="subscriptions")
router.register("subscribers", SubscriberViewSet, basename="subscribers")
router.register("donations", DonationViewSet, basename="donations")
router.register("payments", PaymentViewSet, basename="payments")
router.register("payouts", PayoutViewSet, basename="payouts")

auth_patterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("verify_email/", VerifyEmailView.as_view(), name="verify_email"),
    path("resend_email/", ResendEmailVerificationView.as_view(), name="resend_email"),
    path("login/", LoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("password/change/", PasswordChangeView.as_view(), name="password_change"),
    path("password/reset/", PasswordResetView.as_view(), name="password_reset"),
    path(
        "password/reset/confirm/",
        PasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
]

app_name = "api"
urlpatterns = router.urls + [
    path("me/", OwnUserAPIView.as_view(), name="me"),
    path("auth/", include(auth_patterns)),
    # docs
    path("", SpectacularSwaggerView.as_view(url_name="api:schema"), name="docs"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
]
