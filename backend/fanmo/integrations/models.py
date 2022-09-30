from allauth.socialaccount.models import SocialAccount
from django.db import models

from fanmo.utils.models import BaseModel


class DiscordServer(BaseModel):
    name = models.CharField(max_length=50)
    external_id = models.CharField(max_length=50)
    social_account = models.OneToOneField(SocialAccount, on_delete=models.CASCADE)


class DiscordRole(BaseModel):
    name = models.CharField(max_length=50)
    external_id = models.CharField(max_length=50)
    discord_server = models.ForeignKey(
        "integrations.DiscordServer", related_name="roles", on_delete=models.CASCADE
    )


class DiscordUser(BaseModel):
    name = models.CharField(max_length=50)
    social_account = models.OneToOneField(SocialAccount, on_delete=models.CASCADE)
    external_id = models.CharField(max_length=50)
