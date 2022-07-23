from allauth.socialaccount.providers.discord.views import DiscordOAuth2Adapter

from fanmo.integrations.provider import DiscordServerProvider, DiscordUserProvider


class DiscordUserOAuth2Adapter(DiscordOAuth2Adapter):
    provider_id = DiscordUserProvider.id


class DiscordServerOAuth2Adapter(DiscordOAuth2Adapter):
    provider_id = DiscordServerProvider.id
