from rest_framework import serializers

from memberships.donations.api.serializers import DonationSerializer
from memberships.payments.models import BankAccount, Payment, Payout
from memberships.subscriptions.api.serializers import SubscriptionSerializer
from memberships.subscriptions.models import Subscription
from memberships.users.api.serializers import UserPreviewSerializer

from memberships.utils import razorpay_client
from razorpay.errors import SignatureVerificationError


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
    seller_user = UserPreviewSerializer(read_only=True)
    donation = DonationSerializer(read_only=True)
    subscription = SubscriptionSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "amount",
            "seller_user",
            "subscription",
            "subscription_id",
            "donation",
            "created_at",
            "processor",
            "type",
            "payload",
        ]
        read_only_fields = [
            "id",
            "seller_user",
            "amount",
            "subscription",
            "donation",
            "created_at",
        ]

    def validate(self, attrs):
        if attrs["type"] == Payment.Type.DONATION:
            raise serializers.ValidationError("NOT IMPLEMENTED>")
        elif attrs["type"] == Payment.Type.SUBSCRIPTION:
            attrs = self._validate_subscription_payload(attrs)
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

        if subscription.status != Subscription.Status.CREATED:
            raise serializers.ValidationError(
                "Payment for this subscription has already been processed.",
                "payment_already_processed",
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
        # force follow the seller
        if payment.buyer_user is not None:
            payment.seller_user.follow(payment.buyer_user)
        return payment


class PaymentSerializer(serializers.ModelSerializer):
    seller_user = UserPreviewSerializer()
    donation = DonationSerializer()
    subscription = SubscriptionSerializer()

    class Meta:
        model = Payment
        fields = [
            "id",
            "type",
            "amount",
            "status",
            "method",
            "seller_user",
            "subscription",
            "donation",
            "created_at",
        ]


class PaymentPreviewSerializer(serializers.ModelSerializer):
    buyer_user = UserPreviewSerializer()

    class Meta:
        model = Payment
        fields = ["id", "amount", "method", "type", "buyer_user", "created_at"]


class PayoutSerializer(serializers.ModelSerializer):
    payment = PaymentPreviewSerializer()

    class Meta:
        model = Payout
        fields = ["id", "amount", "status", "payment", "created_at"]


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
