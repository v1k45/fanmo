from django.conf import settings

from djmoney.contrib.django_rest_framework.fields import MoneyField
from rest_framework import serializers

from memberships.donations.models import Donation
from memberships.users.api.serializers import UserPreviewSerializer
from memberships.users.models import User


class DonationPaymentSerializer(serializers.ModelSerializer):
    key = serializers.SerializerMethodField()
    order_id = serializers.CharField(source="external_id")
    name = serializers.CharField(source="receiver_user.display_name")
    prefill = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()

    class Meta:
        model = Donation
        fields = ["key", "order_id", "name", "prefill", "notes"]

    def get_key(self, _):
        return settings.RAZORPAY_KEY

    def get_prefill(self, _):
        sender = self.context["request"].user
        if sender.is_authenticated:
            return {"name": sender.display_name, "email": sender.email}
        return dict()

    def get_notes(self, donation):
        return {"external_id": donation.id}


class DonationCreateSerializer(serializers.ModelSerializer):
    username = serializers.SlugRelatedField(
        slug_field="username",
        queryset=User.objects.filter(is_active=True),
        source="receiver",
        write_only=True,
    )
    payment_processor = serializers.CharField(read_only=True, default="razorpay")
    payment_payload = DonationPaymentSerializer(source="*", read_only=True)

    class Meta:
        model = Donation
        fields = [
            "id",
            "username",
            "amount",
            "name",
            "message",
            "is_anonymous",
            "payment_processor",
            "payment_payload",
        ]

    def validate(self, attrs):
        receiver = attrs["receiver"]
        if not receiver.can_accept_payments():
            raise serializers.ValidationError(
                f"{receiver.name} is currently not accepting payments.",
                "cannot_accept_payments",
            )

        min_amount = receiver.user_preferences.minimum_amount
        if min_amount > attrs["amount"]:
            raise serializers.ValidationError(
                f"Amount cannot be lower than {min_amount.amount}",
                "min_payment_account",
            )
        return attrs

    def create(self, validated_data):
        validated_data["buyer"] = self.context["request"].user
        donation = super().create(validated_data)
        donation.create_external()
        return donation


class DonationSerializer(serializers.ModelSerializer):
    receiver = UserPreviewSerializer()

    class Meta:
        model = Donation
        fields = [
            "id",
            "receiver",
            "name",
            "message",
            "is_anonymous",
            "status",
            "created_at",
        ]
