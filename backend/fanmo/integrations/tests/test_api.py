import pytest
from allauth.socialaccount.models import SocialAccount, SocialToken
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from fanmo.integrations.models import DiscordRole, DiscordServer, DiscordUser
from fanmo.users.adapters import SocialAccountAdapter

pytestmark = pytest.mark.django_db


class TestDiscordServerAPI:
    def test_connect(self, api_client, creator_user, mocker):
        get_token_mock = mocker.patch(
            "fanmo.integrations.api.serializers.discord_api.get_token",
            return_value={
                "guild": {
                    "id": "guild_123",
                    "name": "fancy server",
                    "roles": [
                        {"id": "role_1", "name": "gold", "managed": False},
                        {"id": "role_2", "name": "silver", "managed": False},
                        {
                            "id": "role_3",
                            "name": "kaagaz_bot",
                            "managed": True,
                            "tags": {"bot_id": "client_123"},
                            "permissions": "123",
                        },
                        {
                            "id": "role_4",
                            "name": "gold",
                            "managed": True,
                            "tags": {"bot_id": "discord_client"},
                            "permissions": "268435459",
                        },
                    ],
                },
                "access_token": "access_123",
                "refresh_token": "refresh_123",
                "expires_in": 3600,
            },
        )
        get_user_mock = mocker.patch(
            "fanmo.integrations.api.serializers.discord_api.get_user",
            return_value={
                "id": "discord_user_1",
                "name": "booboo",
            },
        )

        api_client.force_authenticate(creator_user)
        response = api_client.post(
            "/api/integrations/discord_server/", {"code": "foobar_123"}
        )
        assert response.status_code == 201

        response_data = response.json()
        assert response_data["name"] == "fancy server"
        assert sorted([r["name"] for r in response_data["roles"]]) == ["gold", "silver"]

        get_token_mock.assert_called_with(
            "foobar_123", "https://localhost/auth/callback/discord/"
        )
        get_user_mock.assert_called_with("access_123")

    def test_update(self, api_client, creator_user, mocker):
        # setup mock discord server
        discord_server = DiscordServer.objects.create(
            name="fancy server",
            external_id="discord_server_1",
            social_account=SocialAccount.objects.create(
                user=creator_user,
                provider="discord_server",
                uid="discord_user_1",
            ),
        )
        role_1 = DiscordRole.objects.create(
            name="role 1", external_id="role_1", discord_server=discord_server
        )
        role_2 = DiscordRole.objects.create(
            name="role 2", external_id="role_2", discord_server=discord_server
        )
        role_3 = DiscordRole.objects.create(
            name="role 3", external_id="role_3", discord_server=discord_server
        )

        # mock refresh call
        get_guild_mock = mocker.patch(
            "fanmo.integrations.api.serializers.discord_api.get_guild",
            return_value={
                "name": "fanciest server",
                "roles": [
                    {"id": "role_1", "name": "gold", "managed": False},
                    {"id": "role_2", "name": "silver", "managed": False},
                    {
                        "id": "role_5",
                        "name": "kaagaz_bot",
                        "managed": True,
                        "tags": {"bot_id": "client_123"},
                        "permissions": "123",
                    },
                    {
                        "id": "role_6",
                        "name": "gold",
                        "managed": True,
                        "tags": {"bot_id": "discord_client"},
                        "permissions": "268435459",
                    },
                    {"id": "role_7", "name": "bronze", "managed": False},
                ],
            },
        )

        api_client.force_authenticate(creator_user)

        response = api_client.patch(
            "/api/integrations/discord_server/",
            {"kick_inactive_members": True, "refresh": True},
        )

        assert response.status_code == 200
        response_data = response.json()
        assert response_data["name"] == "fanciest server"
        assert response_data["kick_inactive_members"]
        assert sorted([r["name"] for r in response_data["roles"]]) == [
            "bronze",
            "gold",
            "silver",
        ]

        assert DiscordRole.objects.filter(id=role_1.pk).exists()
        assert DiscordRole.objects.filter(id=role_2.pk).exists()
        assert not DiscordRole.objects.filter(id=role_3.pk).exists()

        get_guild_mock.called

    def test_disconnect(self, api_client, creator_user, mocker):
        # setup mock discord server
        discord_server = DiscordServer.objects.create(
            name="fancy server",
            external_id="discord_server_1",
            social_account=SocialAccount.objects.create(
                user=creator_user,
                provider="discord_server",
                uid="discord_user_1",
            ),
        )
        DiscordRole.objects.create(
            name="role 1", external_id="role_1", discord_server=discord_server
        )
        DiscordRole.objects.create(
            name="role 2", external_id="role_2", discord_server=discord_server
        )

        api_client.force_authenticate(creator_user)

        response = api_client.delete("/api/integrations/discord_server/")
        assert response.status_code == 204
        assert not DiscordServer.objects.filter(id=discord_server.id).exists()


class TestDiscordUserAPI:
    def test_connect(self, api_client, active_membership, mocker):
        # setup mock discord server
        discord_server = DiscordServer.objects.create(
            name="fancy server",
            external_id="discord_server_1",
            social_account=SocialAccount.objects.create(
                user=active_membership.creator_user,
                provider="discord_server",
                uid="discord_server_1",
            ),
        )
        role_1 = DiscordRole.objects.create(
            name="role 1", external_id="role_1", discord_server=discord_server
        )
        role_2 = DiscordRole.objects.create(
            name="role 2", external_id="role_2", discord_server=discord_server
        )

        active_membership.tier.discord_role = role_1
        active_membership.tier.save()

        get_token_mock = mocker.patch(
            "fanmo.integrations.api.serializers.discord_api.get_token",
            return_value={
                "scope": "email guilds.join identify",
                "access_token": "access_123",
                "refresh_token": "refresh_123",
                "expires_in": 0,
            },
        )
        get_user_mock = mocker.patch(
            "fanmo.integrations.api.serializers.discord_api.get_user",
            return_value={
                "id": "discord_user_2",
                "username": "booboo",
                "discriminator": "2160",
            },
        )
        refresh_token_mock = mocker.patch(
            "fanmo.integrations.models.discord_api.refresh_token",
            return_value={
                "access_token": "access_123_new",
                "refresh_token": "refresh_123",
                "expires_in": 3600,
            },
        )
        add_guild_member_mock = mocker.patch(
            "fanmo.integrations.models.discord_api.add_guild_member"
        )
        add_guild_member_role_mock = mocker.patch(
            "fanmo.integrations.models.discord_api.add_guild_member_role"
        )

        api_client.force_authenticate(active_membership.fan_user)
        response = api_client.post(
            "/api/integrations/discord_user/", {"code": "code_123"}
        )

        assert response.status_code == 201
        response_data = response.json()
        assert response_data["name"] == "booboo#2160"

        get_token_mock.assert_called_with(
            "code_123", "https://localhost/auth/callback/discord/"
        )
        get_user_mock.assert_called_with("access_123")
        refresh_token_mock.assert_called_with("refresh_123")
        add_guild_member_mock.assert_called_with(
            "discord_server_1", "discord_user_2", "access_123_new"
        )
        add_guild_member_role_mock.assert_called_with(
            "discord_server_1", "discord_user_2", "role_1"
        )

    def test_disconnect(self, api_client, active_membership, mocker):
        # setup mock discord server
        discord_server = DiscordServer.objects.create(
            name="fancy server",
            kick_inactive_members=True,
            external_id="discord_server_1",
            social_account=SocialAccount.objects.create(
                user=active_membership.creator_user,
                provider="discord_server",
                uid="discord_user_1",
            ),
        )
        role_1 = DiscordRole.objects.create(
            name="role 1", external_id="role_1", discord_server=discord_server
        )

        # setup mock discord user
        discord_user = DiscordUser.objects.create(
            name="booboo#2160",
            external_id="discord_user_2",
            social_account=SocialAccount.objects.create(
                user=active_membership.fan_user,
                provider="discord_user",
                uid="discord_user_2",
            ),
        )

        # set discord role to membership
        active_membership.tier.discord_role = role_1
        active_membership.tier.save()

        api_client.force_authenticate(active_membership.fan_user)

        remove_guild_member_role_mock = mocker.patch(
            "fanmo.integrations.models.discord_api.remove_guild_member_role"
        )
        remove_guild_member_mock = mocker.patch(
            "fanmo.integrations.models.discord_api.remove_guild_member"
        )

        response = api_client.delete("/api/integrations/discord_user/")
        assert response.status_code == 204

        assert not DiscordUser.objects.filter(id=discord_user.id).exists()

        remove_guild_member_role_mock.assert_called_once_with(
            "discord_server_1", "discord_user_2", "role_1"
        )
        remove_guild_member_mock.assert_called_once_with(
            "discord_server_1", "discord_user_2"
        )


class TestTierAPIDiscordIntegration:
    def test_update(self, api_client, active_membership, mocker):
        # setup mock discord server
        discord_server = DiscordServer.objects.create(
            name="fancy server",
            kick_inactive_members=True,
            external_id="discord_server_1",
            social_account=SocialAccount.objects.create(
                user=active_membership.creator_user,
                provider="discord_server",
                uid="discord_user_1",
            ),
        )
        role_1 = DiscordRole.objects.create(
            name="role 1", external_id="role_1", discord_server=discord_server
        )

        # setup mock discord user
        discord_user = DiscordUser.objects.create(
            name="booboo#2160",
            external_id="discord_user_2",
            social_account=SocialAccount.objects.create(
                user=active_membership.fan_user,
                provider="discord_user",
                uid="discord_user_2",
            ),
        )
        social_token = SocialToken.objects.create(
            app=SocialAccountAdapter().get_app(None, "discord_user"),
            account=discord_user.social_account,
            token="access_123",
            token_secret="refresh_123",
            expires_at=timezone.now() + relativedelta(days=1),
        )

        # setup api mocks
        add_guild_member_mock = mocker.patch(
            "fanmo.integrations.models.discord_api.add_guild_member"
        )
        add_guild_member_role_mock = mocker.patch(
            "fanmo.integrations.models.discord_api.add_guild_member_role"
        )

        api_client.force_authenticate(active_membership.creator_user)
        response = api_client.patch(
            f"/api/tiers/{active_membership.tier_id}/", {"discord_role_id": role_1.id}
        )

        assert response.status_code == 200
        assert response.json()["discord_role_id"] == role_1.id

        add_guild_member_mock.assert_called_once_with(
            "discord_server_1", "discord_user_2", "access_123"
        )
        add_guild_member_role_mock.assert_called_once_with(
            "discord_server_1", "discord_user_2", "role_1"
        )
