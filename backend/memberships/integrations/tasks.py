from memberships.integrations.models import DiscordServer, DiscordUser


def add_buyer_to_discord_server(subscription):
    buyer_discord_user = DiscordUser.objects.filter(
        social_account__user=subscription.buyer_user
    )
    if buyer_discord_user is None:
        return

    seller_discord_server = DiscordServer.objects.filter(
        social_account__user=subscription.seller_user
    )
    if seller_discord_server is None:
        return

    if subscription.tier is None or subscription.tier.discord_role is None:
        return

    tier_discord_role = subscription.tier.discord_role
    # check if user is already present in the server
    # check if the user already has role on the server
    seller_discord_server.add(buyer_discord_user, tier_discord_role)


def remove_buyer_from_discord_server(subscription):
    buyer_discord_user = DiscordUser.objects.filter(
        social_account__user=subscription.buyer_user
    )
    if buyer_discord_user is None:
        return

    seller_discord_server = DiscordServer.objects.filter(
        social_account__user=subscription.seller_user
    )
    if seller_discord_server is None:
        return

    if subscription.tier is None or subscription.tier.discord_role is None:
        return

    tier_discord_role = subscription.tier.discord_role
    seller_discord_server.remove_role(buyer_discord_user, tier_discord_role)
