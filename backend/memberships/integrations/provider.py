from allauth.socialaccount.providers.discord.provider import DiscordProvider


class DiscordUserProvider(DiscordProvider):
    id = "discord_user"
    name = "Discord User"


class DiscordServerProvider(DiscordProvider):
    id = "discord_server"
    name = "Discord Server"


provider_classes = [DiscordUserProvider, DiscordServerProvider]
