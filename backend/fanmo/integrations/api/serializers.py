from rest_framework import serializers

from fanmo.integrations.models import DiscordRole, DiscordServer, DiscordUser


class DiscordUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscordUser
        fields = ["id", "name"]


class DiscordRoleSerializer(serializers.ModelSerializer):
    class Meta:
        model = DiscordRole
        fields = ["id", "name"]


class DiscordServerSerializer(serializers.ModelSerializer):
    roles = DiscordRoleSerializer(many=True)

    class Meta:
        model = DiscordServer
        fields = ["id", "name", "roles"]


class IntegrationSerializer(serializers.Serializer):
    discord_user = DiscordUserSerializer()
    discord_server = DiscordServerSerializer()
