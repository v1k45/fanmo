from django.conf import settings
from djmoney.contrib.django_rest_framework import MoneyField
from rest_framework import serializers

from allauth.account.adapter import get_adapter
from memberships.subscriptions.models import Membership, Plan, Subscription, Tier
from memberships.users.api.serializers import UserPreviewSerializer
from memberships.users.models import User

from drf_extra_fields.fields import Base64ImageField
from versatileimagefield.serializers import VersatileImageFieldSerializer


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
    class Meta:
        model = Tier
        fields = ["id", "name", "amount", "amount_currency"]


class SubscriberSerializer(serializers.ModelSerializer):
    fan_user = UserPreviewSerializer()
    amount = MoneyField(max_digits=7, decimal_places=2, source="plan.amount")
    tier = TierPreviewSerializer(source="plan.tier")

    class Meta:
        model = Subscription
        fields = [
            "id",
            "fan_user",
            "amount",
            "tier",
            "status",
            "cycle_end_at",
            "is_active",
        ]


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
    creator_user = UserPreviewSerializer()
    amount = MoneyField(max_digits=7, decimal_places=2, source="plan.amount")
    tier = TierPreviewSerializer(source="plan.tier")
    payment = SubscriptionPaymentSerializer(source="*")

    class Meta:
        model = Subscription
        fields = [
            "id",
            "creator_user",
            "amount",
            "tier",
            "payment",
            "status",
            "cycle_end_at",
            "is_active",
        ]


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    username = serializers.SlugRelatedField(
        slug_field="username",
        queryset=User.objects.filter(is_active=True),
        source="creator_user",
        write_only=True,
    )
    amount = MoneyField(
        max_digits=7,
        decimal_places=2,
        source="plan.amount",
        default_currency="INR",
    )

    creator_user = UserPreviewSerializer(read_only=True)
    tier = TierPreviewSerializer(source="plan.tier", read_only=True)

    processor = serializers.CharField(read_only=True, default="razorpay")
    payload = RazorpayPayloadSerializer(source="*", read_only=True)

    is_required = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            "id",
            "username",
            "amount",
            "status",
            "creator_user",
            "tier",
            "processor",
            "payload",
            "cycle_end_at",
            "is_required",
        ]
        read_only_fields = [
            "status",
            "creator_user",
            "tier",
            "processor",
            "payload",
            "cycle_end_at",
            "is_required",
        ]

    def get_is_required(self, subscription):
        return subscription.status == Subscription.Status.CREATED

    def validate(self, attrs):
        creator_user = attrs["creator_user"]
        if not creator_user.can_accept_payments():
            raise serializers.ValidationError(
                f"{creator_user.display_name} is currently not accepting payments.",
                "cannot_accept_payments",
            )

        amount = attrs["plan"]["amount"]
        min_amount = creator_user.user_preferences.minimum_amount
        if amount < min_amount:
            raise serializers.ValidationError(
                f"Amount cannot be lower than {min_amount.amount}",
                "min_payment_account",
            )

        try:
            existing_subscription = Subscription.objects.active(
                creator_user, self.context["request"].user
            )
            if existing_subscription.plan.amount == amount:
                raise serializers.ValidationError(
                    f"You are already subscribed to {creator_user.display_name} using this amount.",
                    "already_subscribed",
                )
        except Subscription.DoesNotExist:
            pass

        # todo: prevent subscription if an update is scheduled for next cycle.
        return attrs

    def create(self, validated_data):
        fan_user = self.context["request"].user
        payment_plan = Plan.for_subscription(
            validated_data["plan"]["amount"],
            validated_data["creator_user"],
            fan_user,
        )
        # upgrade to another active plan?
        return payment_plan.subscribe(fan_user)


class MembershipSerializer(serializers.ModelSerializer):
    tier = TierPreviewSerializer(read_only=True)
    creator_user = UserPreviewSerializer(read_only=True)
    active_subscription = SubscriptionSerializer(read_only=True)
    scheduled_subscription = SubscriptionSerializer(read_only=True)

    # input fields
    tier_id = serializers.PrimaryKeyRelatedField(
        queryset=Tier.objects.filter(is_active=True, creator_user__is_creator=True),
        source="tier",
        write_only=True,
    )
    creator_username = serializers.SlugRelatedField(
        slug_field="username",
        queryset=User.objects.filter(is_active=True, is_creator=True),
        source="creator_user",
        write_only=True,
    )
    email = serializers.EmailField(required=False, allow_blank=True, write_only=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        request = self.context.get("request")
        if request and not request.user.is_authenticated:
            self.fields["email"].allow_blank = False
            self.fields["email"].required = True

    class Meta:
        model = Membership
        fields = [
            "id",
            "tier",
            "creator_user",
            "tier_id",
            "creator_username",
            "active_subscription",
            "scheduled_subscription",
            "email",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["tier", "creator_user", "is_active"]

    def get_fan_user(self, email=None):
        request = self.context["request"]
        if request.user.is_authenticated:
            return request.user

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            return existing_user

        adapter = get_adapter(request)
        return adapter.invite(request._request, email)

    def validate(self, attrs):
        fan_user = self.get_fan_user(attrs.pop("email", None))

        if self.instance:
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

    def validate_email(self, email):
        user = self.context["request"].user
        if user.is_authenticated:
            return

        # TODO: Figure out guest checkout flow for memberships and donations.
        # For now, allow emails of users who haven't logged in.
        user = User.objects.filter(email=email).first()
        if user and user.last_login:
            raise serializers.ValidationError(
                "An account with this email already exists. Please login to continue.",
                "user_exists",
            )
        return email

    def validate_creator_user(self, creator_user):
        if self.instance and self.instance.creator_user != creator_user:
            raise serializers.ValidationError(
                "Creator cannot be changed. Please create a separate membership.",
            )
        return creator_user

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
    tier = TierPreviewSerializer()
    fan_user = UserPreviewSerializer()

    class Meta:
        model = Membership
        fields = ["id", "tier", "fan_user", "is_active", "created_at", "updated_at"]
