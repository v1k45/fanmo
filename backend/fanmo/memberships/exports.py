from import_export import resources

from fanmo.memberships.models import Membership
from fanmo.utils.resources import ModelResource


class MembershipExportResource(ModelResource):
    fan_id = resources.Field("fan_user__id", "fan_id")
    fan_name = resources.Field("fan_user__display_name", "fan_name")
    fan_email = resources.Field("fan_user__email", "fan_email")

    tier_id = resources.Field("tier__id", "tier_id")
    tier_name = resources.Field("tier__name", "tier_name")

    active_subscription_id = resources.Field(
        "active_subscription_id", "active_subscription_id"
    )
    active_subscription_status = resources.Field(
        "active_subscription__status", "active_subscription_status"
    )
    active_subscription_cycle_start_at = resources.Field(
        "active_subscription__cycle_start_at", "active_subscription_cycle_start_at"
    )
    active_subscription_cycle_end_at = resources.Field(
        "active_subscription__cycle_end_at", "active_subscription_cycle_end_at"
    )
    active_subscription_tier_id = resources.Field(
        "active_subscription__plan__tier_id", "active_subscription_tier_id"
    )
    active_subscription_tier_name = resources.Field(
        "active_subscription__plan__tier__name", "active_subscription_tier_name"
    )
    active_subscription_amount = resources.Field(
        "active_subscription__plan__amount__amount", "active_subscription_amount"
    )
    active_subscription_amount_currency = resources.Field(
        "active_subscription__plan__amount_currency",
        "active_subscription_amount_currency",
    )

    scheduled_subscription_id = resources.Field(
        "scheduled_subscription_id", "scheduled_subscription_id"
    )
    scheduled_subscription_status = resources.Field(
        "scheduled_subscription__status", "scheduled_subscription_status"
    )
    scheduled_subscription_cycle_start_at = resources.Field(
        "scheduled_subscription__cycle_start_at",
        "scheduled_subscription_cycle_start_at",
    )
    scheduled_subscription_cycle_end_at = resources.Field(
        "scheduled_subscription__cycle_end_at", "scheduled_subscription_cycle_end_at"
    )
    scheduled_subscription_tier_id = resources.Field(
        "scheduled_subscription__plan__tier_id", "scheduled_subscription_tier_id"
    )
    scheduled_subscription_tier_name = resources.Field(
        "scheduled_subscription__plan__tier__name", "scheduled_subscription_tier_name"
    )
    scheduled_subscription_amount = resources.Field(
        "scheduled_subscription__plan__amount__amount", "scheduled_subscription_amount"
    )
    scheduled_subscription_amount_currency = resources.Field(
        "scheduled_subscription__plan__amount_currency",
        "scheduled_subscription_amount_currency",
    )

    class Meta:
        model = Membership
        fields = [
            "id",
            "fan_id",
            "fan_name",
            "fan_email",
            "tier_id",
            "tier_name",
            "is_active",
            "active_subscription_id",
            "active_subscription_status",
            "active_subscription_cycle_start_at",
            "active_subscription_cycle_end_at",
            "active_subscription_tier_id",
            "active_subscription_tier_name",
            "active_subscription_amount",
            "active_subscription_amount_currency",
            "scheduled_subscription_id",
            "scheduled_subscription_status",
            "scheduled_subscription_cycle_start_at",
            "scheduled_subscription_cycle_end_at",
            "scheduled_subscription_tier_id",
            "scheduled_subscription_tier_name",
            "scheduled_subscription_amount",
            "scheduled_subscription_amount_currency",
            "created_at",
            "updated_at",
        ]
        export_order = fields
