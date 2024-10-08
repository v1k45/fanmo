from allauth.account.adapter import get_adapter
from django.conf import settings
from djmoney.contrib.django_rest_framework import MoneyField
from drf_extra_fields.fields import Base64ImageField
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from fanmo.core.serializers import PaymentIntentSerializerMixin
from fanmo.integrations.models import DiscordRole
from fanmo.memberships.models import Membership, Plan, Subscription, Tier
from fanmo.users.api.serializers import FanUserPreviewSerializer, UserPreviewSerializer
from fanmo.users.models import User
from fanmo.utils.fields import VersatileImageFieldSerializer


class TierSerializer(serializers.ModelSerializer):
    cover = VersatileImageFieldSerializer("tier_cover", read_only=True)
    cover_base64 = Base64ImageField(write_only=True, source="cover", required=False)
    discord_role_id = serializers.PrimaryKeyRelatedField(
        queryset=DiscordRole.objects.all(),
        source="discord_role",
        required=False,
        allow_null=True,
    )

    class Meta:
        model = Tier
        fields = [
            "id",
            "name",
            "amount",
            "description",
            "cover",
            "cover_base64",
            "cover_background_style",
            "welcome_message",
            "benefits",
            "discord_role_id",
            "is_public",
            "is_recommended",
        ]
        extra_kwargs = {"benefits": {"allow_empty": True}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["discord_role_id"].queryset = self.fields[
            "discord_role_id"
        ].queryset.filter(
            discord_server__social_account__user_id=self.context["request"].user.pk
        )

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
    cover = VersatileImageFieldSerializer("tier_cover", read_only=True)

    class Meta:
        model = Tier
        fields = [
            "id",
            "name",
            "amount",
            "amount_currency",
            "cover",
            "cover_background_style",
        ]


class RazorpayPayloadSerializer(serializers.ModelSerializer):
    key = serializers.SerializerMethodField()
    subscription_id = serializers.CharField(source="external_id")
    subscription_card_change = serializers.SerializerMethodField()
    name = serializers.CharField(source="plan.name")
    prefill = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    theme = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            "key",
            "subscription_id",
            "subscription_card_change",
            "name",
            "prefill",
            "notes",
            "image",
            "theme",
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

    def get_image(self, subscription):
        serializer = VersatileImageFieldSerializer("user_avatar")
        serializer._context = self.context
        avatar_renditions = serializer.to_representation(
            subscription.creator_user.avatar
        )
        return avatar_renditions["thumbnail"] if avatar_renditions else None

    def get_theme(self, subscription):
        return {"color": "#6266f1"}


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
    fan_user = FanUserPreviewSerializer(read_only=True)
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
    period = serializers.ChoiceField(
        choices=Plan.Period.choices, default=Plan.Period.MONTHLY
    )

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
            "period",
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

        if (
            self.instance
            and self.instance.tier == attrs["tier"]
            and self.instance.is_active
        ):
            raise serializers.ValidationError(
                f"You are already a member of {self.instance.tier.name}.",
                "membership_exists",
            )

        if attrs["tier"].creator_user_id != creator_user.id:
            raise serializers.ValidationError(
                {
                    "tier_id": serializers.ErrorDetail(
                        f"{creator_user.display_name} does not have this tier."
                    )
                }
            )

        attrs["fan_user"] = fan_user
        return attrs

    def create(self, validated_data):
        tier = validated_data.pop("tier")
        period = validated_data.pop("period")
        membership, _ = Membership.objects.get_or_create(**validated_data)
        membership.start(tier, period)
        return membership

    def update(self, instance: Membership, validated_data):
        tier = validated_data.pop("tier")
        period = validated_data.pop("period", Plan.Period.MONTHLY)
        instance.update(tier, period)
        return instance


class MembershipPreviewSerializer(serializers.ModelSerializer):
    tier = TierPreviewSerializer(read_only=True)
    fan_user = FanUserPreviewSerializer(read_only=True)
    status = serializers.SerializerMethodField()

    class Meta:
        model = Membership
        fields = [
            "id",
            "tier",
            "fan_user",
            "status",
            "is_active",
            "created_at",
            "updated_at",
        ]

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


class MembershipGiveawaySerializer(serializers.ModelSerializer):
    tier_id = serializers.PrimaryKeyRelatedField(
        queryset=Tier.objects.filter(is_active=True, creator_user__is_creator=True),
        source="tier",
        write_only=True,
    )
    email = serializers.EmailField(write_only=True)
    period = serializers.ChoiceField(
        choices=Plan.Period.choices, default=Plan.Period.MONTHLY
    )

    class Meta:
        model = Membership
        fields = ["id", "tier_id", "email", "period"]

    def validate_tier(self, tier):
        if tier.creator_user_id != self.context["request"].user.pk:
            raise serializers.ValidationError("Could not find this tier.")
        return tier

    def create(self, validated_data):
        request = self.context["request"]
        email = validated_data["email"]
        fan_user = User.objects.filter(email__iexact=email).first()
        if not fan_user:
            adapter = get_adapter(request)
            fan_user = adapter.invite(request._request, email)

        membership, _ = Membership.objects.get_or_create(
            creator_user=request.user, fan_user=fan_user
        )
        membership.giveaway(validated_data["tier"], validated_data["period"])
        return membership


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


class MemebershipStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    active = serializers.IntegerField()
    inactive = serializers.IntegerField()
    total_payment = serializers.DecimalField(max_digits=9, decimal_places=2)
