from fanmo.integrations.models import DiscordServer, DiscordUser


def add_fan_to_discord_server(subscription):
    fan_discord_user = DiscordUser.objects.filter(
        social_account__user=subscription.fan_user
    )
    if fan_discord_user is None:
        return

    creator_discord_server = DiscordServer.objects.filter(
        social_account__user=subscription.creator_user
    )
    if creator_discord_server is None:
        return

    if subscription.tier is None or subscription.tier.discord_role is None:
        return

    tier_discord_role = subscription.tier.discord_role
    # check if user is already present in the server
    # check if the user already has role on the server
    creator_discord_server.add(fan_discord_user, tier_discord_role)


def remove_fan_from_discord_server(subscription):
    fan_discord_user = DiscordUser.objects.filter(
        social_account__user=subscription.fan_user
    )
    if fan_discord_user is None:
        return

    creator_discord_server = DiscordServer.objects.filter(
        social_account__user=subscription.creator_user
    )
    if creator_discord_server is None:
        return

    if subscription.tier is None or subscription.tier.discord_role is None:
        return

    tier_discord_role = subscription.tier.discord_role
    creator_discord_server.remove_role(fan_discord_user, tier_discord_role)
