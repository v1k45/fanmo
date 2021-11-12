from rest_framework import serializers
from memberships.donations.api.serializers import DonationSerializer

from memberships.payments.models import Payment, Payout, BankAccount
from memberships.subscriptions.api.serializers import SubscriptionSerializer
from memberships.users.api.serializers import UserPreviewSerializer


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

    def create(self, validated_data):
        if validated_data["type"] == Payment.Type.DONATION:
            return Payment.capture_donation(validated_data["payload"])
        return Payment.authenticate_subscription(validated_data["payload"])


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
            "mobile_number",
            "account_type",
            "beneficiary_name",
            "ifsc",
            "created_at",
        ]
        read_only_fields = ["status", "created_at"]

    def create(self, validated_data):
        validated_data["beneficiary_user"] = self.context["request"].user
        return super().create(validated_data)
