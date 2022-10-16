import pytest
from allauth.socialaccount.models import SocialAccount, SocialToken
from dateutil.relativedelta import relativedelta
from django.utils import timezone

from fanmo.integrations.models import DiscordRole, DiscordServer, DiscordUser
from fanmo.integrations.tasks import refresh_discord_membership
from fanmo.users.adapters import SocialAccountAdapter

pytestmark = pytest.mark.django_db


class TestRefreshDiscordMembership:
    def test_activate_membership(self, active_membership, mocker):
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
        SocialToken.objects.create(
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
        remove_guild_member_mock = mocker.patch(
            "fanmo.integrations.models.discord_api.remove_guild_member"
        )
        remove_guild_member_role_mock = mocker.patch(
            "fanmo.integrations.models.discord_api.remove_guild_member_role"
        )

        # setup tier
        active_membership.tier.discord_role = role_1
        active_membership.tier.save()

        refresh_discord_membership(active_membership.id)

        add_guild_member_mock.assert_called_with(
            "discord_server_1", "discord_user_2", "access_123"
        )
        add_guild_member_role_mock.assert_called_with(
            "discord_server_1", "discord_user_2", "role_1"
        )
        remove_guild_member_mock.assert_not_called()
        remove_guild_member_role_mock.assert_not_called()

        # mock membership deactivation
        active_membership.is_active = False
        active_membership.save()

        # reset mock
        add_guild_member_mock.reset_mock()
        add_guild_member_role_mock.reset_mock()

        refresh_discord_membership(active_membership.id)

        remove_guild_member_role_mock.assert_called_with(
            "discord_server_1", "discord_user_2", "role_1"
        )
        remove_guild_member_mock.assert_called_with(
            "discord_server_1", "discord_user_2"
        )
        add_guild_member_mock.assert_not_called()
        add_guild_member_role_mock.assert_not_called()
