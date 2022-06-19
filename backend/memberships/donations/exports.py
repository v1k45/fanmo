from memberships.donations.models import Donation
from import_export import resources
from memberships.utils.resources import ModelResource


class DonationExportResource(ModelResource):
    fan_id = resources.Field("fan_user__id", "fan_id")
    fan_name = resources.Field("fan_user__display_name", "fan_name")
    fan_email = resources.Field("fan_user__email", "fan_email")
    amount = resources.Field("amount__amount", "amount")

    class Meta:
        model = Donation
        fields = [
            "id",
            "fan_id",
            "fan_name",
            "fan_email",
            "amount",
            "amount_currency",
            "status",
            "message",
            "is_hidden",
            "external_id",
            "created_at",
            "updated_at",
        ]
        export_order = fields
