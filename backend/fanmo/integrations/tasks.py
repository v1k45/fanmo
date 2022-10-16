import structlog

from fanmo.integrations.models import DiscordUser

logger = structlog.get_logger(__name__)


def invite_members_to_discord_server(creator_user_id, tier_id=None):
    from fanmo.memberships.models import Membership

    active_discord_memberships = Membership.objects.filter(
        creator_user_id=creator_user_id,
        is_active=True,
        fan_user__socialaccount__discord_user__isnull=False,
        tier__discord_role__isnull=False,
    ).select_related(
        "fan_user",
        "tier__discord_role__discord_server",
        "active_subscription",
    )

    if tier_id:
        active_discord_memberships = active_discord_memberships.filter(tier_id=tier_id)

    logger.info(
        "invite_members_to_discord_server",
        creator_user_id=creator_user_id,
        tier_id=tier_id,
        membership_ids=list(active_discord_memberships.values_list("id", flat=True)),
    )
    for membership in active_discord_memberships:
        add_fan_to_discord_server(membership)


def join_creator_servers(fan_user_id):
    from fanmo.memberships.models import Membership

    active_discord_memberships = Membership.objects.filter(
        fan_user=fan_user_id,
        is_active=True,
        fan_user__socialaccount__discord_user__isnull=False,
        tier__discord_role__isnull=False,
    ).select_related(
        "fan_user",
        "tier__discord_role__discord_server",
        "active_subscription",
    )

    logger.info(
        "join_creator_servers",
        fan_user_id=fan_user_id,
        membership_ids=list(active_discord_memberships.values_list("id", flat=True)),
    )
    for membership in active_discord_memberships:
        add_fan_to_discord_server(membership)


def leave_creator_servers(fan_user_id):
    from fanmo.memberships.models import Membership

    active_discord_memberships = Membership.objects.filter(
        fan_user=fan_user_id,
        is_active=True,
        fan_user__socialaccount__discord_user__isnull=False,
        tier__discord_role__isnull=False,
    ).select_related(
        "fan_user",
        "tier__discord_role__discord_server",
        "active_subscription",
    )

    logger.info(
        "leave_creator_servers",
        fan_user_id=fan_user_id,
        membership_ids=list(active_discord_memberships.values_list("id", flat=True)),
    )
    for membership in active_discord_memberships:
        remove_fan_from_discord_server(membership)


def refresh_discord_membership(membership_id):
    from fanmo.memberships.models import Membership

    membership = Membership.objects.select_related(
        "fan_user",
        "tier__discord_role__discord_server",
        "active_subscription",
    ).get(id=membership_id)

    logger.info("refresh_discord_membership", membership_id=membership_id)
    if membership.is_active:
        add_fan_to_discord_server(membership)
    else:
        remove_fan_from_discord_server(membership)


def add_fan_to_discord_server(membership):
    fan_discord_user = DiscordUser.objects.filter(
        social_account__user=membership.fan_user_id
    ).first()
    if fan_discord_user is None:
        logger.info("discord_user_connection_not_found", membership_id=membership.id)
        return

    if not membership.tier.discord_role:
        logger.info("discord_tier_connection_not_found", membership_id=membership.id)
        return

    membership.tier.discord_role.grant(fan_discord_user)


def remove_fan_from_discord_server(membership):
    fan_discord_user = DiscordUser.objects.filter(
        social_account__user=membership.fan_user_id
    ).first()
    if fan_discord_user is None:
        logger.info("discord_user_connection_not_found", membership_id=membership.id)
        return

    if not membership.tier.discord_role:
        logger.info("discord_tier_connection_not_found", membership_id=membership.id)
        return

    membership.tier.discord_role.revoke(fan_discord_user)
