from django.conf import settings
from django.shortcuts import get_object_or_404
from django.urls import reverse
from rest_framework import generics

from fanmo.core.tasks import async_task
from fanmo.integrations.api.serializers import (
    DiscordServerConnectSerializer,
    DiscordServerSerializer,
    DiscordUserConnectSerializer,
    DiscordUserSerializer,
    IntegrationSerializer,
)
from fanmo.integrations.models import DiscordServer, DiscordUser
from fanmo.integrations.tasks import join_creator_servers, leave_creator_servers


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
    generics.CreateAPIView, generics.RetrieveAPIView, generics.DestroyAPIView
):
    """Discord User Integration"""

    def get_serializer_class(self):
        self.set_callback_url()
        if self.request.method.lower() == "post":
            return DiscordUserConnectSerializer
        return DiscordUserSerializer

    def set_callback_url(self):
        """allow social auth to be used from wildcard origins in dev mode"""
        if settings.DEBUG and "redirect_uri" in self.request.data:
            self.callback_url = self.request.data.get("redirect_uri")
        else:
            self.callback_url = settings.BASE_URL + reverse("discord_callback")

    def get_object(self):
        return get_object_or_404(DiscordUser, social_account__user=self.request.user)

    def perform_destroy(self, instance):
        leave_creator_servers(self.request.user.pk)
        instance.social_account.delete()

    def perform_create(self, serializer):
        super().perform_create(serializer)
        # add user to all creator discord server
        # todo: think about the usecase when user connects and disconnects discord account quickly
        async_task(join_creator_servers, self.request.user.pk)


class DiscordServerConnectView(
    generics.CreateAPIView,
    generics.UpdateAPIView,
    generics.RetrieveAPIView,
    generics.DestroyAPIView,
):
    """Discord Server Integration"""

    def get_serializer_class(self):
        self.set_callback_url()
        if self.request.method.lower() == "post":
            return DiscordServerConnectSerializer
        return DiscordServerSerializer

    def set_callback_url(self):
        """allow social auth to be used from wildcard origins in dev mode"""
        if settings.DEBUG and "redirect_uri" in self.request.data:
            self.callback_url = self.request.data.get("redirect_uri")
        else:
            self.callback_url = settings.BASE_URL + reverse("discord_callback")

    def get_object(self):
        return get_object_or_404(
            DiscordServer.objects.prefetch_related("roles"),
            social_account__user=self.request.user,
        )

    def perform_destroy(self, instance):
        # todo: remove all users from the server
        instance.social_account.delete()
