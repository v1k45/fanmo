from django.conf import settings
from djmoney.contrib.django_rest_framework.fields import MoneyField
from rest_framework import serializers

from memberships.donations.models import Donation
from memberships.users.api.serializers import UserPreviewSerializer
from memberships.users.models import User


class DonationPaymentSerializer(serializers.ModelSerializer):
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

    def get_prefill(self, _):
        sender = self.context["request"].user
        if sender.is_authenticated:
            return {"name": sender.display_name, "email": sender.email}
        return dict()

    def get_notes(self, donation):
        return {"donation_id": donation.id}


class DonationCreateSerializer(serializers.ModelSerializer):
    username = serializers.SlugRelatedField(
        slug_field="username",
        queryset=User.objects.filter(is_active=True),
        source="creator_user",
        write_only=True,
    )
    amount = MoneyField(
        max_digits=7,
        decimal_places=2,
        default_currency="INR",
    )
    payment_processor = serializers.CharField(read_only=True, default="razorpay")
    payment_payload = DonationPaymentSerializer(source="*", read_only=True)
    fan_user = UserPreviewSerializer(read_only=True)

    class Meta:
        model = Donation
        fields = [
            "id",
            "username",
            "fan_user",
            "amount",
            "name",
            "message",
            "is_anonymous",
            "payment_processor",
            "payment_payload",
            "created_at",
        ]
        read_only_fields = ["id", "fan_user", "created_at"]

    def validate(self, attrs):
        creator_user = attrs["creator_user"]
        if not creator_user.can_accept_payments():
            raise serializers.ValidationError(
                f"{creator_user.display_name} is currently not accepting payments.",
                "cannot_accept_payments",
            )

        min_amount = creator_user.user_preferences.minimum_amount
        if min_amount > attrs["amount"]:
            raise serializers.ValidationError(
                f"Amount cannot be lower than {min_amount.amount}",
                "min_payment_account",
            )
        return attrs

    def create(self, validated_data):
        user = self.context["request"].user
        if user.is_authenticated:
            validated_data["fan_user"] = user
        donation = super().create(validated_data)
        donation.create_external()
        return donation


class DonationSerializer(serializers.ModelSerializer):
    fan_user = serializers.SerializerMethodField()

    class Meta:
        model = Donation
        fields = [
            "id",
            "fan_user",
            "name",
            "message",
            "amount",
            "is_anonymous",
            "status",
            "created_at",
        ]

    def get_fan_user(self, donation):
        if donation.is_anonymous or donation.fan_user_id is None:
            return None
        return UserPreviewSerializer(donation.fan_user, context=self.context).data
