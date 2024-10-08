from drf_spectacular.utils import extend_schema_field
from razorpay.errors import SignatureVerificationError
from rest_framework import serializers

from fanmo.donations.api.serializers import DonationSerializer
from fanmo.donations.models import Donation
from fanmo.memberships.api.serializers import SubscriptionSerializer
from fanmo.memberships.models import Subscription
from fanmo.payments.models import BankAccount, Payment, Payout
from fanmo.users.api.serializers import FanUserPreviewSerializer, UserPreviewSerializer
from fanmo.utils import razorpay_client


class RazorpayResponseSerializer(serializers.Serializer):
    razorpay_order_id = serializers.CharField(required=False)
    razorpay_subscription_id = serializers.CharField(required=False)
    razorpay_payment_id = serializers.CharField()
    razorpay_signature = serializers.CharField()

    def validate(self, attrs):
        if "razorpay_order_id" in attrs and "razorpay_subscription_id" in attrs:
            raise serializers.ValidationError("Invalid payment response.")
        return super().validate(attrs)


class PaymentProcessingSerializer(serializers.ModelSerializer):
    processor = serializers.ChoiceField(
        choices=["razorpay"], default="razorpay", write_only=True
    )
    payload = RazorpayResponseSerializer(write_only=True)

    subscription_id = serializers.PrimaryKeyRelatedField(
        source="subscription",
        write_only=True,
        required=False,
        queryset=Subscription.objects.all(),
    )
    donation_id = serializers.PrimaryKeyRelatedField(
        source="donation",
        write_only=True,
        required=False,
        queryset=Donation.objects.all(),
    )
    creator_user = UserPreviewSerializer(read_only=True)
    donation = DonationSerializer(read_only=True)
    subscription = SubscriptionSerializer(read_only=True)
    message = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "amount",
            "creator_user",
            "subscription",
            "subscription_id",
            "donation",
            "donation_id",
            "message",
            "created_at",
            "processor",
            "type",
            "payload",
        ]
        read_only_fields = [
            "id",
            "creator_user",
            "amount",
            "subscription",
            "donation",
            "created_at",
        ]

    def get_message(self, payment):
        if (
            payment.type == Payment.Type.SUBSCRIPTION
            and payment.subscription.status == Subscription.Status.ACTIVE
        ):
            return payment.subscription.plan.tier.welcome_message
        return payment.creator_user.user_preferences.thank_you_message

    def validate(self, attrs):
        if attrs["type"] == Payment.Type.DONATION:
            attrs = self._validate_donation_payload(attrs)
        elif attrs["type"] == Payment.Type.SUBSCRIPTION:
            attrs = self._validate_subscription_payload(attrs)
        return attrs

    def _validate_donation_payload(self, attrs):
        donation = attrs.get("donation")
        if not donation:
            raise serializers.ValidationError(
                "donation_id field is required.", "required"
            )

        if donation.external_id != attrs["payload"]["razorpay_order_id"]:
            raise serializers.ValidationError(
                "Incorrect payload for given donation.", "donation_mismatch"
            )

        # payment should not be reprocessed.
        if Payment.objects.filter(
            external_id=attrs["payload"]["razorpay_payment_id"]
        ).exists():
            raise serializers.ValidationError(
                "Payment for this donation has already been processed.",
                "payment_already_processed",
            )

        # only draft and halted subscription can process payments.
        if donation.status != Donation.Status.PENDING:
            raise serializers.ValidationError(
                "Payment for this donation cannot be processed in its current state.",
                "invalid_donation_state",
            )

        try:
            razorpay_client.utility.verify_payment_signature(attrs["payload"])
        except SignatureVerificationError:
            raise serializers.ValidationError(
                "Invalid payload signature", "signature_mismatch"
            )

        return attrs

    def _validate_subscription_payload(self, attrs):
        subscription = attrs.get("subscription")
        if not subscription:
            raise serializers.ValidationError(
                "subscription_id field is required.", "required"
            )

        if subscription.external_id != attrs["payload"]["razorpay_subscription_id"]:
            raise serializers.ValidationError(
                "Incorrect payload for given subscription.", "subscription_mismatch"
            )

        # payment should not be reprocessed.
        if Payment.objects.filter(
            external_id=attrs["payload"]["razorpay_payment_id"]
        ).exists():
            raise serializers.ValidationError(
                "Payment for this subscription has already been processed.",
                "payment_already_processed",
            )

        # only draft and halted subscription can process payments.
        if subscription.status not in [
            Subscription.Status.CREATED,
            Subscription.Status.HALTED,
        ]:
            raise serializers.ValidationError(
                "Payment for this subscription cannot be processed in its current state.",
                "invalid_subscription_state",
            )

        # Mould the payload to work with razorpay's signature verifier.
        payload = attrs["payload"]
        payload.update(
            {
                "razorpay_order_id": payload["razorpay_payment_id"],
                "razorpay_payment_id": payload["razorpay_subscription_id"],
                "rzp_payment_id": payload["razorpay_payment_id"],
            }
        )
        try:
            razorpay_client.utility.verify_payment_signature(payload)
        except SignatureVerificationError:
            raise serializers.ValidationError(
                "Invalid payload signature", "signature_mismatch"
            )

        attrs["payload"] = payload
        return attrs

    def create(self, validated_data):
        # save payment metadata
        if validated_data["type"] == Payment.Type.DONATION:
            payment = Payment.capture_donation(validated_data["payload"])
        else:
            payment = Payment.authenticate_subscription(validated_data["payload"])
        # force follow the creator
        if payment.fan_user is not None:
            payment.creator_user.follow(payment.fan_user)
        return payment


class PayoutSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payout
        fields = [
            "id",
            "amount",
            "amount_currency",
            "status",
            "external_id",
            "created_at",
        ]


class PaymentSerializer(serializers.ModelSerializer):
    fan_user = FanUserPreviewSerializer()
    payout = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "type",
            "fan_user",
            "amount",
            "amount_currency",
            "status",
            "method",
            "payout",
            "external_id",
            "created_at",
        ]

    @extend_schema_field(PayoutSerializer())
    def get_payout(self, payment):
        if payment.creator_user_id == self.context["request"].user.id and hasattr(
            payment, "payout"
        ):
            return PayoutSerializer(payment.payout, context=self.context).data


class PaymentPreviewSerializer(serializers.ModelSerializer):
    fan_user = UserPreviewSerializer()

    class Meta:
        model = Payment
        fields = ["id", "amount", "method", "type", "fan_user", "created_at"]


class BankAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = BankAccount
        fields = [
            "id",
            "status",
            "account_name",
            "account_number",
            "account_type",
            "ifsc",
        ]
        read_only_fields = ["status"]

    def validate(self, attrs):
        if self.instance and self.instance.status != BankAccount.Status.CREATED:
            raise serializers.ValidationError(
                "You cannot make changes to a linked account. Please contact support.",
                "permission_denied",
            )

        if not self.instance and self.context["request"].user.bank_accounts.exists():
            raise serializers.ValidationError(
                "Multiple bank accounts are not supported. Please contact support.",
                "permission_denied",
            )

        return attrs

    def create(self, validated_data):
        validated_data["beneficiary_user"] = self.context["request"].user
        return super().create(validated_data)


class PaymentStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=9, decimal_places=2)
    total_payout_scheduled = serializers.DecimalField(max_digits=9, decimal_places=2)
    total_payout_processed = serializers.DecimalField(max_digits=9, decimal_places=2)
