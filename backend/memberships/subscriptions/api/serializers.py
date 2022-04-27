from django.conf import settings
from djmoney.contrib.django_rest_framework import MoneyField
from rest_framework import serializers

from allauth.account.adapter import get_adapter
from memberships.subscriptions.models import Membership, Plan, Subscription, Tier
from memberships.users.api.serializers import UserPreviewSerializer
from memberships.users.models import User
from memberships.core.serializers import PaymentIntentSerializerMixin

from drf_spectacular.utils import extend_schema_field
from drf_extra_fields.fields import Base64ImageField
from memberships.utils.fields import VersatileImageFieldSerializer


class TierSerializer(serializers.ModelSerializer):
    cover = VersatileImageFieldSerializer("user_cover", read_only=True)
    cover_base64 = Base64ImageField(write_only=True, source="cover", required=False)

    class Meta:
        model = Tier
        fields = [
            "id",
            "name",
            "amount",
            "description",
            "cover",
            "cover_base64",
            "welcome_message",
            "benefits",
            "is_public",
            "is_recommended",
        ]

    def validate_is_recommended(self, is_recommended):
        if not is_recommended:
            return is_recommended

        recommended_tiers = (
            self.context["request"].user.public_tiers().filter(is_recommended=True)
        )
        if self.instance:
            recommended_tiers = recommended_tiers.exclude(id=self.instance.id)
        if recommended_tier := recommended_tiers.first():
            raise serializers.ValidationError(
                f'Only one tier can be recommended at a time. Update "{recommended_tier.name}" and try again.',
                "recommended_tier_exists",
            )
        return is_recommended

    def validate(self, attrs):
        attrs["creator_user"] = self.context["request"].user
        return super().validate(attrs)


class TierPreviewSerializer(serializers.ModelSerializer):
    cover = VersatileImageFieldSerializer("user_cover", read_only=True)

    class Meta:
        model = Tier
        fields = ["id", "name", "amount", "amount_currency", "cover"]


class RazorpayPayloadSerializer(serializers.ModelSerializer):
    key = serializers.SerializerMethodField()
    subscription_id = serializers.CharField(source="external_id")
    subscription_card_change = serializers.SerializerMethodField()
    name = serializers.CharField(source="plan.name")
    prefill = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            "key",
            "subscription_id",
            "subscription_card_change",
            "name",
            "prefill",
            "notes",
        ]

    def get_key(self, _):
        return settings.RAZORPAY_KEY

    def get_prefill(self, subscription):
        fan_user = subscription.fan_user
        return {"name": fan_user.display_name, "email": fan_user.email}

    def get_notes(self, subscription):
        return {"subscription_id": subscription.id}

    def get_subscription_card_change(self, subscription):
        return 1 if subscription.status == Subscription.Status.HALTED else 0


class SubscriptionPaymentSerializer(serializers.ModelSerializer):
    processor = serializers.CharField(read_only=True, default="razorpay")
    payload = RazorpayPayloadSerializer(source="*", read_only=True)
    is_required = serializers.SerializerMethodField()

    def get_is_required(self, subscription):
        return subscription.status == Subscription.Status.CREATED

    class Meta:
        model = Subscription
        fields = ["processor", "payload", "is_required"]


class SubscriptionSerializer(serializers.ModelSerializer):
    amount = MoneyField(max_digits=7, decimal_places=2, source="plan.amount")
    tier = TierPreviewSerializer(source="plan.tier")
    payment = SubscriptionPaymentSerializer(source="*")

    class Meta:
        model = Subscription
        fields = [
            "id",
            "amount",
            "tier",
            "payment",
            "payment_method",
            "status",
            "cycle_start_at",
            "cycle_end_at",
            "is_active",
        ]


class MembershipSerializer(PaymentIntentSerializerMixin, serializers.ModelSerializer):
    tier = TierPreviewSerializer(read_only=True)
    fan_user = UserPreviewSerializer(read_only=True)
    creator_user = UserPreviewSerializer(read_only=True)
    active_subscription = SubscriptionSerializer(read_only=True)
    scheduled_subscription = SubscriptionSerializer(read_only=True)

    # input fields
    tier_id = serializers.PrimaryKeyRelatedField(
        queryset=Tier.objects.filter(is_active=True, creator_user__is_creator=True),
        source="tier",
        write_only=True,
    )
    lifetime_amount = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = [
            "id",
            "tier",
            "fan_user",
            "creator_user",
            "tier_id",
            "creator_username",
            "active_subscription",
            "scheduled_subscription",
            "lifetime_amount",
            "status",
            "email",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["tier", "creator_user", "fan_user", "is_active"]

    @extend_schema_field(serializers.DecimalField(max_digits=7, decimal_places=2))
    def get_lifetime_amount(self, membership):
        return serializers.DecimalField(
            max_digits=7, decimal_places=2
        ).to_representation(getattr(membership, "lifetime_amount", 0))

    @extend_schema_field(
        serializers.ChoiceField(
            choices=Subscription.Status.values + ["scheduled_to_update"]
        )
    )
    def get_status(self, membership):
        if membership.scheduled_subscription and membership.active_subscription:
            if (
                membership.active_subscription.status
                == Subscription.Status.SCHEDULED_TO_CANCEL
                and membership.scheduled_subscription.status
                == Subscription.Status.SCHEDULED_TO_ACTIVATE
            ):
                return "scheduled_to_update"
        if membership.active_subscription:
            return membership.active_subscription.status

    def validate(self, attrs):
        fan_user = self.get_fan_user(attrs.pop("email", None))

        if (
            self.instance
            and self.instance.fan_user_id != self.context["request"].user.pk
        ):
            raise serializers.ValidationError(
                "You do not have permissions to perform this action.",
                "permission_denied",
            )
        elif self.instance:
            creator_user = self.instance.creator_user
        else:
            creator_user = attrs["creator_user"]

        existing_membership = Membership.objects.filter(
            creator_user=creator_user, fan_user=fan_user
        ).first()

        # do not allow creating a new membership if one already exists.
        if (
            not self.instance
            and existing_membership
            and existing_membership.is_active is not None
        ):
            raise serializers.ValidationError(
                f"You already have a membership with {creator_user.username}. Please login to continue.",
                "membership_exists",
            )

        if self.instance and self.instance.tier == attrs["tier"]:
            raise serializers.ValidationError(
                f"You are already a member of {self.instance.tier.name}.",
                "membership_exists",
            )

        attrs["fan_user"] = fan_user
        return attrs

    def create(self, validated_data):
        tier = validated_data.pop("tier")
        membership, _ = Membership.objects.get_or_create(**validated_data)
        membership.start(tier)
        return membership

    def update(self, instance: Membership, validated_data):
        tier = validated_data.pop("tier")
        instance.update(tier)
        return instance


class MemberSerializer(serializers.ModelSerializer):
    tier = TierPreviewSerializer(read_only=True)
    fan_user = UserPreviewSerializer(read_only=True)
    active_subscription = SubscriptionSerializer(read_only=True)
    scheduled_subscription = SubscriptionSerializer(read_only=True)
    lifetime_amount = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = [
            "id",
            "tier",
            "fan_user",
            "active_subscription",
            "scheduled_subscription",
            "lifetime_amount",
            "is_active",
            "created_at",
            "updated_at",
        ]

    @extend_schema_field(serializers.DecimalField(max_digits=7, decimal_places=2))
    def get_lifetime_amount(self, membership):
        return getattr(membership, "lifetime_amount", 0)
