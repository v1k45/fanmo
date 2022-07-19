from django.conf import settings
from django.db.models import prefetch_related_objects
from rest_framework import authentication, exceptions

from memberships.users.models import User


def create_auth_token(token_model, user, serializer):
    """Do not create auth token, application is supposed to used session auth."""
    return user


class UsernameAuthentication(authentication.BaseAuthentication):
    """
    Authenticate using x-username header, only available in DEBUG mode.
    """

    def authenticate(self, request):
        if not settings.DEBUG:
            return None

        username = request.META.get("HTTP_X_USERNAME")
        if not username:
            return None

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            raise exceptions.AuthenticationFailed("No such user")

        return (user, None)


class SessionAuthentication(authentication.SessionAuthentication):
    def authenticate(self, request):
        value = super().authenticate(request)
        if not value:
            return None

        user, token = value
        prefetched_users = prefetch_related_objects([user], "memberships", "followings")
        return (prefetched_users[0], token)
