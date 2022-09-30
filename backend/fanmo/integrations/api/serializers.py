import requests
import structlog
from allauth.socialaccount.models import SocialAccount, SocialToken
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from rest_framework import serializers

from fanmo.integrations.discord import discord_api
from fanmo.integrations.models import DiscordRole, DiscordServer, DiscordUser
from fanmo.users.adapters import SocialAccountAdapter

logger = structlog.get_logger(__name__)


class DiscordUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscordUser
        fields = ["id", "name"]


class DiscordRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscordRole
        fields = ["id", "name"]


class DiscordServerSerializer(serializers.ModelSerializer):
    refresh = serializers.BooleanField(write_only=True)
    roles = DiscordRoleSerializer(many=True, read_only=True)

    class Meta:
        model = DiscordServer
        fields = ["id", "name", "roles", "refresh"]
        read_only_fields = ["id", "name", "roles"]

    def validate(self, attrs):
        try:
            return discord_api.get_guild(self.instance.external_id)
        except requests.RequestException:
            logger.exception("discord_guild_reponse_failed")
            raise serializers.ValidationError(
                "Failed to retrieve discord server information. Please try again after some time."
            )

    def update(self, instance, validated_data):
        instance.name = validated_data["name"]
        instance.save()

        roles = [role for role in validated_data["roles"] if not role["managed"]]

        # delete local roles which are no longer present in the guild
        DiscordRole.objects.filter(discord_server=instance).exclude(
            external_id__in=[role["id"] for role in roles]
        ).delete()

        for role in roles:
            DiscordRole.objects.update_or_create(
                discord_server=instance,
                external_id=role["id"],
                defaults={"name": role["name"]},
            )

        return instance


class IntegrationSerializer(serializers.Serializer):
    discord_user = DiscordUserSerializer()
    discord_server = DiscordServerSerializer()


class DiscordServerConnectSerializer(serializers.ModelSerializer):
    code = serializers.CharField(write_only=True)
    roles = DiscordRoleSerializer(many=True, read_only=True)

    class Meta:
        model = DiscordServer
        fields = ["id", "name", "roles", "code"]
        read_only_fields = ["id", "name", "roles"]

    def validate(self, attrs):
        if DiscordServer.objects.filter(
            social_account__user=self.context["request"].user
        ).exists():
            raise serializers.ValidationError(
                "You already have a discord connection. Disconnect to connect a new one."
            )

        try:
            token_response = discord_api.get_token(
                attrs["code"], self.context["view"].callback_url
            )
        except requests.RequestException:
            logger.exception("discord_token_response_failed")
            raise serializers.ValidationError(
                "Error validating the connection request. Please try again."
            )

        if "guild" not in token_response:
            raise serializers.ValidationError(
                "Unable to find server information from your connection. Please try again.",
                "tampered_request",
            )

        bot_role = next(
            filter(
                lambda role: role["managed"]
                and role["tags"]["bot_id"] == discord_api.client_id,
                token_response["guild"]["roles"],
            ),
            {"permissions": 0},
        )
        if bot_role["permissions"] != discord_api.server_permissions:
            raise serializers.ValidationError(
                "Some required permissions are missing from your connection. Please grant requested permissions.",
                "missing_permissions",
            )

        try:
            user_response = discord_api.get_user(token_response["access_token"])
        except requests.RequestException:
            logger.exception("discord_user_response_failed")
            raise serializers.ValidationError(
                "Error retrieving your discord user information. Please try again.",
                "discord_error",
            )

        return {**token_response, **user_response}

    def create(self, validated_data):
        provider = "discord_server"
        user = self.context["request"].user
        social_account, _ = SocialAccount.objects.get_or_create(
            user=user,
            provider=provider,
            uid=validated_data["id"],
            defaults={
                "extra_data": {
                    **validated_data,
                    "access_token": None,
                    "refresh_token": None,
                }
            },
        )
        SocialToken.objects.update_or_create(
            app=SocialAccountAdapter().get_app(None, provider),
            account=social_account,
            defaults={
                "token": validated_data["access_token"],
                "token_secret": validated_data["refresh_token"],
                "expires_at": timezone.now()
                + relativedelta(seconds=validated_data["expires_in"]),
            },
        )

        discord_server, _ = DiscordServer.objects.get_or_create(
            social_account=social_account,
            external_id=validated_data["guild"]["id"],
            defaults={"name": validated_data["guild"]["name"]},
        )
        DiscordRole.objects.bulk_create(
            [
                DiscordRole(
                    name=role["name"],
                    external_id=role["id"],
                    discord_server=discord_server,
                )
                for role in validated_data["guild"]["roles"]
                if not role["managed"]
            ]
        )
        return discord_server


class DiscordUserConnectSerializer(serializers.ModelSerializer):
    code = serializers.CharField(write_only=True)

    class Meta:
        model = DiscordUser
        fields = ["id", "name", "code"]
        read_only_fields = ["id", "name"]

    def validate(self, attrs):
        if DiscordUser.objects.filter(
            social_account__user=self.context["request"].user
        ).exists():
            raise serializers.ValidationError(
                "You already have a discord connection. Disconnect to connect a new one."
            )

        try:
            token_response = discord_api.get_token(
                attrs["code"], self.context["view"].callback_url
            )
        except requests.RequestException:
            logger.exception("discord_token_response_failed")
            raise serializers.ValidationError(
                "Error validating the connection request. Please try again."
            )

        if sorted(token_response["scope"].split()) != sorted(
            ["email", "identify", "guilds.join"]
        ):
            raise serializers.ValidationError(
                "Some required permissions are missing from your connection. Please grant requested permissions.",
                "missing_permissions",
            )

        try:
            user_response = discord_api.get_user(token_response["access_token"])
        except requests.RequestException:
            logger.exception("discord_user_response_failed")
            raise serializers.ValidationError(
                "Error retrieving your discord user information. Please try again.",
                "discord_error",
            )

        return {**token_response, **user_response}

    def create(self, validated_data):
        provider = "discord_user"
        user = self.context["request"].user
        social_account, _ = SocialAccount.objects.get_or_create(
            user=user,
            provider=provider,
            uid=validated_data["id"],
            defaults={
                "extra_data": {
                    **validated_data,
                    "access_token": None,
                    "refresh_token": None,
                }
            },
        )
        SocialToken.objects.update_or_create(
            app=SocialAccountAdapter().get_app(None, provider),
            account=social_account,
            defaults={
                "token": validated_data["access_token"],
                "token_secret": validated_data["refresh_token"],
                "expires_at": timezone.now()
                + relativedelta(seconds=validated_data["expires_in"]),
            },
        )

        discord_user, _ = DiscordUser.objects.get_or_create(
            social_account=social_account,
            external_id=validated_data["id"],
            defaults={
                "name": f"{validated_data['username']}#{validated_data['discriminator']}"
            },
        )
        return discord_user
