from rest_framework.decorators import action
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.viewsets import ReadOnlyModelViewSet

from memberships.users.models import User

from .serializers import UserSerializer

from drf_spectacular.utils import extend_schema
from dj_rest_auth.registration.views import RegisterView as BaseRegisterView
from dj_rest_auth.views import LoginView as BaseLoginView


class UserViewSet(ReadOnlyModelViewSet):
    serializer_class = UserSerializer
    queryset = User.objects.filter(is_active=True)
    lookup_field = "username"

    def get_queryset(self):
        base_qs = super().get_queryset()
        following_username = self.request.query_params.get("following_username")
        if following_username:
            return base_qs.filter(followings__username=following_username)
        if self.request.query_params.get("creator"):
            return base_qs.filter(
                user_preferences__is_accepting_payments=True
            ).order_by("-follower_count")
        return base_qs

    @extend_schema(request=None)
    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated])
    def follow(self, request, *args, **kwargs):
        user = self.get_object()
        user.follow(self.request.user)
        return self.retrieve(request, *args, **kwargs)

    @extend_schema(request=None)
    @action(detail=True, methods=["POST"], permission_classes=[IsAuthenticated])
    def unfollow(self, request, *args, **kwargs):
        user = self.get_object()
        user.unfollow(self.request.user)
        return self.retrieve(request, *args, **kwargs)


class OwnUserAPIView(RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return self.request.user


class RegisterView(BaseRegisterView):
    def get_response_data(self, user):
        return UserSerializer(user, context=self.get_serializer_context()).data


class LoginView(BaseLoginView):
    """Login using email/username and password"""

    def get_response_serializer(self):
        return UserSerializer
