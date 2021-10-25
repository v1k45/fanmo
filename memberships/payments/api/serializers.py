from hashid_field.rest import HashidSerializerCharField
from rest_framework import serializers
from memberships.donations.api.serializers import DonationSerializer

from memberships.payments.models import Payment, Payout
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
    id = HashidSerializerCharField(read_only=True)
    processor = serializers.ChoiceField(
        choices=["razorpay"], default="razorpay", write_only=True
    )
    type = serializers.ChoiceField(choices=["donation", "subscription"])
    payload = RazorpayResponseSerializer(write_only=True)

    seller = UserPreviewSerializer(read_only=True)
    donation = DonationSerializer(read_only=True)
    subscription = SubscriptionSerializer(read_only=True)

    class Meta:
        model = Payment
        fields = [
            "id",
            "amount",
            "seller",
            "subscription",
            "donation",
            "created_at",
            "processor",
            "type",
            "payload",
        ]
        read_only_fields = [
            "id",
            "seller",
            "amount",
            "subscription",
            "donation",
            "created_at",
        ]

    def create(self, validated_data):
        if validated_data["type"] == "donation":
            return Payment.capture_donation(validated_data["payload"])
        return Payment.capture_subscription(validated_data["payload"])


class PaymentSerializer(serializers.ModelSerializer):
    id = HashidSerializerCharField(read_only=True)
    seller = UserPreviewSerializer()
    donation = DonationSerializer()
    subscription = SubscriptionSerializer()

    class Meta:
        model = Payment
        fields = [
            "id",
            "type",
            "amount",
            "seller",
            "subscription",
            "donation",
            "created_at",
        ]


class PaymentPreviewSerializer(serializers.ModelSerializer):
    id = HashidSerializerCharField(read_only=True)
    buyer = UserPreviewSerializer()

    class Meta:
        model = Payment
        fields = ["id", "amount", "type", "buyer", "created_at"]


class PayoutSerializer(serializers.ModelSerializer):
    id = HashidSerializerCharField(read_only=True)
    payment = PaymentPreviewSerializer()

    class Meta:
        model = Payout
        fields = ["id", "amount", "status", "payment", "created_at"]
