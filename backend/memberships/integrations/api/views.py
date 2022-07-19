from allauth.socialaccount.providers.oauth2.client import OAuth2Client
from dj_rest_auth.registration.views import SocialConnectView
from django.shortcuts import get_object_or_404
from rest_framework import generics

from memberships.integrations.api.serializers import (
    DiscordServerSerializer,
    DiscordUserSerializer,
    IntegrationSerializer,
)
from memberships.integrations.models import DiscordServer, DiscordUser
from memberships.integrations.oauth_adapters import (
    DiscordServerOAuth2Adapter,
    DiscordUserOAuth2Adapter,
)


class IntegrationView(generics.RetrieveAPIView):
    serializer_class = IntegrationSerializer

    def get_object(self):
        discord_user = DiscordUser.objects.filter(
            social_account__user=self.request.user
        ).first()
        discord_server = DiscordServer.objects.filter(
            social_account__user=self.request.user
        ).first()
        return {"discord_user": discord_user, "discord_server": discord_server}


class DiscordUserConnectView(
    generics.RetrieveAPIView, generics.DestroyAPIView, SocialConnectView
):
    """Discord User Integration"""

    adapter_class = DiscordUserOAuth2Adapter
    client_class = OAuth2Client

    def get_response_serializer(self):
        return DiscordUserSerializer

    def get_serializer_class(self):
        if self.request.method == "GET":
            return self.get_response_serializer()
        return super().get_serializer_class()

    def get_object(self):
        return get_object_or_404(DiscordUser, social_account__user=self.request.user)

    def perform_destroy(self, instance):
        # todo: remove user from all servers
        instance.social_account.delete()


class DiscordServerConnectView(
    generics.RetrieveAPIView, generics.DestroyAPIView, SocialConnectView
):
    """Discord Server Integration"""

    adapter_class = DiscordServerOAuth2Adapter
    client_class = OAuth2Client

    def get_response_serializer(self):
        return DiscordServerSerializer

    def get_object(self):
        return get_object_or_404(DiscordServer, social_account__user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == "GET":
            return self.get_response_serializer()
        return super().get_serializer_class()

    def perform_destroy(self, instance):
        # todo: remove all users from the server
        instance.social_account.delete()
