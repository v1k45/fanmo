from dj_rest_auth.views import (
    LogoutView,
    PasswordChangeView,
    PasswordResetConfirmView,
    PasswordResetView,
)
from django.urls.conf import include, path
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from rest_framework_extensions.routers import ExtendedSimpleRouter

from memberships.donations.api.views import DonationViewSet
from memberships.payments.api.views import (
    BankAccountViewSet,
    PaymentViewSet,
    PayoutViewSet,
)
from memberships.posts.api.views import CommentViewSet, PostViewSet
from memberships.subscriptions.api.views import (
    SubscriberViewSet,
    SubscriptionViewSet,
    TierViewSet,
)
from memberships.users.api.views import (
    LoginView,
    OwnUserAPIView,
    RegisterView,
    RequestEmailVerificationView,
    TOTPDeviceViewSet,
    UserViewSet,
    VerifyEmailView,
)
from memberships.webhooks.views import razorpay_webhook

router = ExtendedSimpleRouter()
router.register("users", UserViewSet, basename="users")
router.register("tiers", TierViewSet, basename="tiers")
router.register("posts", PostViewSet, basename="posts")
router.register("comments", CommentViewSet, basename="comments")
router.register("subscriptions", SubscriptionViewSet, basename="subscriptions")
router.register("subscribers", SubscriberViewSet, basename="subscribers")
router.register("donations", DonationViewSet, basename="donations")
router.register("payments", PaymentViewSet, basename="payments")
router.register("payouts", PayoutViewSet, basename="payouts")
router.register("accounts", BankAccountViewSet, basename="bank_accounts")
router.register("auth/mfa", TOTPDeviceViewSet, basename="mfa")

auth_patterns = [
    path("register/", RegisterView.as_view(), name="register"),
    path("login/", LoginView.as_view(), name="login"),
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

app_name = "api"
urlpatterns = router.urls + [
    path("me/", OwnUserAPIView.as_view(), name="me"),
    path("auth/", include(auth_patterns)),
    path("webhooks/razorpay/", razorpay_webhook),
    # docs
    path("", SpectacularSwaggerView.as_view(url_name="api:schema"), name="docs"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
]
