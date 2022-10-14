import requests
import structlog
from allauth.socialaccount.models import SocialAccount
from dateutil.relativedelta import relativedelta
from django.db import models
from django.utils import timezone

from fanmo.integrations.discord import discord_api
from fanmo.utils.models import BaseModel

logger = structlog.get_logger(__name__)


class DiscordServer(BaseModel):
    name = models.CharField(max_length=50)
    kick_inactive_members = models.BooleanField(default=False)
    external_id = models.CharField(max_length=50)
    social_account = models.OneToOneField(
        SocialAccount, on_delete=models.CASCADE, related_name="discord_server"
    )


class DiscordRole(BaseModel):
    name = models.CharField(max_length=50)
    external_id = models.CharField(max_length=50)
    discord_server = models.ForeignKey(
        "integrations.DiscordServer", related_name="roles", on_delete=models.CASCADE
    )

    def grant(self, discord_user):
        """Grant a discord role to a discord user"""

        try:
            discord_api.add_guild_member(
                self.discord_server.external_id,
                discord_user.external_id,
                discord_user.get_access_token(),
            )
            discord_api.add_guild_member_role(
                self.discord_server.external_id,
                discord_user.external_id,
                self.external_id,
            )
        except requests.RequestException:
            logger.exception(
                "discord_role_assignment_failure",
                discord_server_id=self.discord_server.id,
                discord_role_id=self.id,
                discord_user_id=discord_user.id,
            )
            return

        logger.info(
            "discord_role_assignment_success",
            discord_server_id=self.discord_server.id,
            discord_role_id=self.id,
            discord_user_id=discord_user.id,
        )

    def revoke(self, discord_user):
        """Revoke a discord role from a discord user, optionally kick the user."""
        try:
            discord_api.remove_guild_member_role(
                self.discord_server.external_id,
                discord_user.external_id,
                self.external_id,
            )
            if self.discord_server.kick_inactive_members:
                discord_api.remove_guild_member(
                    self.discord_server.external_id, discord_user.external_id
                )
        except requests.RequestException:
            logger.exception(
                "discord_role_revoke_failure",
                discord_server_id=self.discord_server.id,
                discord_role_id=self.id,
                discord_user_id=discord_user.id,
            )
            return

        logger.info(
            "discord_role_revoke_success",
            discord_server_id=self.discord_server.id,
            discord_role_id=self.id,
            discord_user_id=discord_user.id,
        )


class DiscordUser(BaseModel):
    name = models.CharField(max_length=50)
    social_account = models.OneToOneField(
        SocialAccount, on_delete=models.CASCADE, related_name="discord_user"
    )
    external_id = models.CharField(max_length=50)

    def get_access_token(self):
        social_token = self.social_account.socialtoken_set.first()
        if (social_token.expires_at - relativedelta(minutes=10)) < timezone.now():
            token_response = discord_api.refresh_token(social_token.token_secret)
            social_token.token = token_response["access_token"]
            social_token.token_secret = token_response["refresh_token"]
            social_token.expires_at = timezone.now() + relativedelta(
                seconds=token_response["expires_in"]
            )
            social_token.save()
        return social_token.token
