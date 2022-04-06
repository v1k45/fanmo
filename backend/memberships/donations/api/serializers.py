from django.conf import settings
from djmoney.contrib.django_rest_framework.fields import MoneyField
from rest_framework import serializers

from memberships.donations.models import Donation
from memberships.users.api.serializers import UserPreviewSerializer
from memberships.core.serializers import PaymentIntentSerializerMixin


class RazorpayPayloadSerializer(serializers.ModelSerializer):
    key = serializers.SerializerMethodField()
    order_id = serializers.CharField(source="external_id")
    name = serializers.CharField(source="creator_user.display_name")
    prefill = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()

    class Meta:
        model = Donation
        fields = ["key", "order_id", "name", "prefill", "notes"]

    def get_key(self, _):
        return settings.RAZORPAY_KEY

    def get_prefill(self, donation):
        fan_user = donation.fan_user
        return {"name": fan_user.display_name, "email": fan_user.email}

    def get_notes(self, donation):
        return {"donation_id": donation.id}


class DonationPaymentSerializer(serializers.ModelSerializer):
    processor = serializers.CharField(read_only=True, default="razorpay")
    payload = RazorpayPayloadSerializer(source="*", read_only=True)
    is_required = serializers.SerializerMethodField()

    def get_is_required(self, donation):
        return donation.status == Donation.Status.PENDING

    class Meta:
        model = Donation
        fields = ["processor", "payload", "is_required"]


class DonationCreateSerializer(
    PaymentIntentSerializerMixin, serializers.ModelSerializer
):
    amount = MoneyField(
        max_digits=7,
        decimal_places=2,
        default_currency="INR",
    )
    payment = DonationPaymentSerializer(source="*", read_only=True)
    fan_user = UserPreviewSerializer(read_only=True)
    creator_user = UserPreviewSerializer(read_only=True)

    class Meta:
        model = Donation
        fields = [
            "id",
            "creator_username",
            "email",
            "fan_user",
            "creator_user",
            "amount",
            "message",
            "is_hidden",
            "payment",
            "created_at",
        ]
        read_only_fields = ["id", "fan_user", "creator_user", "created_at"]

    def validate(self, attrs):
        attrs["fan_user"] = self.get_fan_user(attrs.pop("email", None))
        return attrs

    def create(self, validated_data):
        donation = super().create(validated_data)
        donation.create_external()
        return donation


class DonationSerializer(serializers.ModelSerializer):
    fan_user = UserPreviewSerializer()
    message = serializers.SerializerMethodField()

    class Meta:
        model = Donation
        fields = [
            "id",
            "fan_user",
            "message",
            "amount",
            "is_hidden",
            "status",
            "created_at",
        ]

    def get_message(self, donation):
        request = self.context["request"]
        if donation.is_hidden and request.user.pk not in (
            donation.creator_user_id,
            donation.fan_user_id,
        ):
            return None
        return donation.message


class DonationUpdateSerializer(DonationSerializer):
    class Meta:
        model = Donation
        fields = [
            "id",
            "fan_user",
            "message",
            "amount",
            "is_hidden",
            "status",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "fan_user",
            "message",
            "amount",
            "status",
            "created_at",
        ]

    def validate(self, attrs):
        if self.context["request"].user != self.instance.creator_user:
            raise serializers.ValidationError(
                "You do not have permissions to perform this action.",
                "permission_denied",
            )
        return attrs
