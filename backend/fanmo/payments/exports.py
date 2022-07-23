from import_export import resources

from fanmo.payments.models import Payment
from fanmo.utils.resources import ModelResource


class PaymentExportResource(ModelResource):
    fan_id = resources.Field("fan_user__id", "fan_id")
    fan_name = resources.Field("fan_user__display_name", "fan_name")
    fan_email = resources.Field("fan_user__email", "fan_email")
    amount = resources.Field("amount__amount", "amount")
    payout_amount = resources.Field("payout__amount__amount", "payout_amount")
    payout_status = resources.Field("payout__status", "payout_status")

    class Meta:
        model = Payment
        fields = [
            "id",
            "fan_id",
            "fan_name",
            "fan_email",
            "amount",
            "amount_currency",
            "status",
            "type",
            "external_id",
            "payout_amount",
            "payout_status",
            "created_at",
            "updated_at",
        ]
        export_order = fields
