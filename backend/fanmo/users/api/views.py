import qrcode
import qrcode.image.svg
from allauth.socialaccount.providers.facebook.views import FacebookOAuth2Adapter
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import RegisterView as BaseRegisterView
from dj_rest_auth.registration.views import SocialLoginView
from dj_rest_auth.views import LoginView as BaseLoginView
from dj_rest_auth.views import PasswordResetView as BasePasswordResetView
from django.conf import settings
from django.http.response import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from django_otp.plugins.otp_totp.models import TOTPDevice
from drf_spectacular.utils import extend_schema
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import PermissionDenied
from rest_framework.generics import GenericAPIView, RetrieveUpdateAPIView
from rest_framework.parsers import FormParser, JSONParser
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ReadOnlyModelViewSet

from fanmo.users.api.filters import UserFilter
from fanmo.users.models import User
from fanmo.utils.throttling import Throttle

from .serializers import (
    CreatorActivitySerializer,
    PublicUserSerializer,
    RequestEmailVerificationSerializer,
    TOTPDeviceSerializer,
    UserSerializer,
    VerifyEmailSerializer,
)


class UserViewSet(ReadOnlyModelViewSet):
    """
    TODO: Remove list API?
    TODO: Add is_creator and is_following filter?
    """

    serializer_class = PublicUserSerializer
    queryset = User.objects.filter(is_active=True)
    lookup_field = "username"
    filter_backends = (DjangoFilterBackend,)
    filterset_class = UserFilter

    @extend_schema(request=None)
    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated])
    def follow(self, request, *args, **kwargs):
        user: User = self.get_object()
        user.follow(self.request.user)
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(request=None)
    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated])
    def unfollow(self, request, *args, **kwargs):
        user: User = self.get_object()
        user.unfollow(self.request.user)
        return self.retrieve(request, *args, **kwargs)


class OwnUserAPIView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class CreatorActivityViewSet(ReadOnlyModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = CreatorActivitySerializer

    def get_queryset(self):
        return self.request.user.activities.all().select_related(
            "membership__tier",
            "membership__fan_user",
            "membership__active_subscription",
            "membership__scheduled_subscription",
        )


class RegisterView(BaseRegisterView):
    throttle_classes = [Throttle("register_hour")]

    def get_response_data(self, user):
        return UserSerializer(user, context=self.get_serializer_context()).data


class LoginViewMixin:
    # nuxt-auth sends oauth2 token request as form data
    parser_classes = [JSONParser, FormParser]

    def get_serializer(self, *args, **kwargs):
        self.set_callback_url()
        return super().get_serializer(*args, **kwargs)

    def set_callback_url(self):
        """allow social auth to be used from wildcard origins in dev mode"""
        if settings.DEBUG and "redirect_uri" in self.request.data:
            self.callback_url = self.request.data.get("redirect_uri")
        else:
            self.callback_url = f"https://{settings.DOMAIN_NAME}/auth/callback"

    def get_response_serializer(self):
        return UserSerializer


class RequestEmailVerificationView(GenericAPIView):
    """
    Send verification code to logged-in user's email.
    """

    serializer_class = RequestEmailVerificationSerializer
    permission_classes = [IsAuthenticated]
    throttle_classes = [Throttle("otp_minute"), Throttle("otp_hour")]

    @extend_schema(responses={204: None})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            instance=self.request.user, data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class VerifyEmailView(GenericAPIView):
    """
    Verify user suppplied code to confirm logged-in user's email.
    """

    serializer_class = VerifyEmailSerializer
    permission_classes = [IsAuthenticated]

    @extend_schema(responses={204: None})
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(
            instance=self.request.user, data=self.request.data
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_204_NO_CONTENT)


class TOTPDeviceViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    serializer_class = TOTPDeviceSerializer

    def get_queryset(self):
        return TOTPDevice.objects.all().filter(user=self.request.user)

    @action(detail=True)
    def qrcode(self, request, *args, **kwargs):
        device = self.get_object()
        if device.confirmed:
            raise PermissionDenied("MFA QR code cannot be accessed after confirmation.")

        svg_image = qrcode.make(
            device.config_url, image_factory=qrcode.image.svg.SvgImage
        )
        response = HttpResponse(content_type="image/svg+xml")
        svg_image.save(response)
        return response


class LoginView(LoginViewMixin, BaseLoginView):
    """Login using email/username and password"""

    throttle_classes = [Throttle("login_hour")]


class GoogleLoginView(LoginViewMixin, SocialLoginView):
    """Login using google"""

    adapter_class = GoogleOAuth2Adapter
    client_class = OAuth2Client


class FacebookLoginView(LoginViewMixin, SocialLoginView):
    """Login using facebook"""

    adapter_class = FacebookOAuth2Adapter
    client_class = OAuth2Client


class PasswordResetView(BasePasswordResetView):
    throttle_classes = [
        Throttle("otp_minute"),
        Throttle("otp_hour"),
    ]
