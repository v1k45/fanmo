from django.conf import settings
from django.http.request import validate_host
from memberships.subscriptions.models import Plan, Subscription, Tier
from memberships.users.api.serializers import UserPreviewSerializer
from memberships.users.models import User
from rest_framework import serializers
from djmoney.contrib.django_rest_framework import MoneyField


class TierSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tier
        fields = [
            "id",
            "name",
            "amount",
            "description",
            "cover",
            "welcome_message",
            "benefits",
            "is_public",
        ]
        extra_kwargs = {"cover": {"required": False}}

    def validate(self, attrs):
        attrs["seller_user"] = self.context["request"].user
        return super().validate(attrs)


class TierPreviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tier
        fields = ["id", "name", "amount"]


class SubscriptionSerializer(serializers.ModelSerializer):
    seller_user = UserPreviewSerializer()
    amount = MoneyField(max_digits=7, decimal_places=2, source="plan.amount")
    tier = TierPreviewSerializer(source="plan.tier")

    class Meta:
        model = Subscription
        fields = [
            "id",
            "seller_user",
            "amount",
            "tier",
            "status",
            "cycle_end_at",
            "is_active",
        ]


class SubscriberSerializer(serializers.ModelSerializer):
    buyer_user = UserPreviewSerializer()
    amount = MoneyField(max_digits=7, decimal_places=2, source="plan.amount")
    tier = TierPreviewSerializer(source="plan.tier")

    class Meta:
        model = Subscription
        fields = [
            "id",
            "buyer_user",
            "amount",
            "tier",
            "status",
            "cycle_end_at",
            "is_active",
        ]


class SubscriptionPaymentSerializer(serializers.ModelSerializer):
    key = serializers.SerializerMethodField()
    subscription_id = serializers.CharField(source="external_id")
    name = serializers.CharField(source="plan.name")
    prefill = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = ["key", "subscription_id", "name", "prefill", "notes"]

    def get_key(self, _):
        return settings.RAZORPAY_KEY

    def get_prefill(self, _):
        buyer = self.context["request"].user
        return {"name": buyer.display_name, "email": buyer.email}

    def get_notes(self, subscription):
        return {"external_id": subscription.id}


class SubscriptionCreateSerializer(serializers.ModelSerializer):
    username = serializers.SlugRelatedField(
        slug_field="username",
        queryset=User.objects.filter(is_active=True),
        source="seller_user",
        write_only=True,
    )
    amount = MoneyField(
        max_digits=7,
        decimal_places=2,
        source="plan.amount",
        default_currency="INR",
    )

    seller_user = UserPreviewSerializer(read_only=True)
    tier = TierPreviewSerializer(source="plan.tier", read_only=True)

    payment_processor = serializers.CharField(read_only=True, default="razorpay")
    payment_payload = SubscriptionPaymentSerializer(source="*", read_only=True)

    requires_payment = serializers.SerializerMethodField()

    class Meta:
        model = Subscription
        fields = [
            "id",
            "username",
            "amount",
            "status",
            "seller_user",
            "tier",
            "payment_processor",
            "payment_payload",
            "cycle_end_at",
            "requires_payment",
        ]
        read_only_fields = [
            "status",
            "seller_user",
            "tier",
            "payment_processor",
            "payment_payload",
            "cycle_end_at",
            "requires_payment",
        ]

    def get_requires_payment(self, subscription):
        return subscription.status == Subscription.Status.CREATED

    def validate(self, attrs):
        seller_user = attrs["seller_user"]
        if not seller_user.can_accept_payments():
            raise serializers.ValidationError(
                f"{seller_user.display_name} is currently not accepting payments.",
                "cannot_accept_payments",
            )

        amount = attrs["plan"]["amount"]
        min_amount = seller_user.user_preferences.minimum_amount
        if amount < min_amount:
            raise serializers.ValidationError(
                f"Amount cannot be lower than {min_amount.amount}",
                "min_payment_account",
            )

        try:
            existing_subscription = Subscription.get_current(
                seller_user, self.context["request"].user
            )
            if existing_subscription.plan.amount == amount:
                raise serializers.ValidationError(
                    f"You are already subscribed to {seller_user.display_name} using this amount.",
                    "already_subscribed",
                )
        except Subscription.DoesNotExist:
            print("new sub")
            pass

        # todo: prevent recent reordering?
        return attrs

    def create(self, validated_data):
        buyer = self.context["request"].user
        payment_plan = Plan.for_subscription(
            validated_data["plan"]["amount"],
            validated_data["seller_user"],
            buyer,
        )
        # upgrade to another active plan?
        return payment_plan.subscribe()
