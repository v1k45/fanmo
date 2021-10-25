from django.conf import settings
from hashid_field.rest import HashidSerializerCharField
from memberships.subscriptions.models import Plan, Subscription, Tier
from memberships.users.api.serializers import UserPreviewSerializer
from memberships.users.models import User
from rest_framework import serializers
from djmoney.contrib.django_rest_framework import MoneyField


class TierSerializer(serializers.ModelSerializer):
    id = HashidSerializerCharField(read_only=True)

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

    def create(self, validated_data):
        user = self.context["request"].user

        payment_plan_data = {
            "name": f"{validated_data['name']} ({validated_data['amount']}) - {user.display_name}",
            "amount": validated_data["amount"],
            "owner": user,
            "created_by": user,
        }
        payment_plan = Plan.objects.create(**payment_plan_data)

        tier = super().create(
            {**validated_data, "owner": user, "payment_plan": payment_plan}
        )

        payment_plan.tier = tier
        payment_plan.create_external()

        return tier


class TierPreviewSerializer(serializers.ModelSerializer):
    id = HashidSerializerCharField(read_only=True)

    class Meta:
        model = Tier
        fields = ["id", "name", "amount"]


class SubscriptionSerializer(serializers.ModelSerializer):
    id = HashidSerializerCharField(read_only=True)
    seller = UserPreviewSerializer()
    amount = MoneyField(max_digits=7, decimal_places=2, source="plan.amount")
    tier = TierPreviewSerializer(source="plan.tier")

    class Meta:
        model = Subscription
        fields = ["id", "seller", "amount", "tier", "status", "expires_at", "is_active"]


class SubscriberSerializer(serializers.ModelSerializer):
    id = HashidSerializerCharField(read_only=True)
    buyer = UserPreviewSerializer()
    amount = MoneyField(max_digits=7, decimal_places=2, source="plan.amount")
    tier = TierPreviewSerializer(source="plan.tier")

    class Meta:
        model = Subscription
        fields = ["id", "buyer", "amount", "tier", "status", "expires_at", "is_active"]


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
    id = HashidSerializerCharField(read_only=True)
    username = serializers.SlugRelatedField(
        slug_field="username",
        queryset=User.objects.filter(is_active=True),
        source="seller",
        write_only=True,
    )
    amount = MoneyField(max_digits=7, decimal_places=2, source="plan.amount")

    seller = UserPreviewSerializer(read_only=True)
    tier = TierPreviewSerializer(source="plan.tier", read_only=True)

    payment_processor = serializers.CharField(read_only=True, default="razorpay")
    payment_payload = SubscriptionPaymentSerializer(source="*", read_only=True)

    class Meta:
        model = Subscription
        fields = [
            "id",
            "username",
            "amount",
            "seller",
            "tier",
            "payment_processor",
            "payment_payload",
            "expires_at",
        ]
        read_only_fields = [
            "seller",
            "tier",
            "payment_processor",
            "payment_payload",
            "expires_at",
        ]

    def validate(self, attrs):
        seller = attrs["seller"]
        if not seller.can_accept_payments():
            raise serializers.ValidationError(
                f"{seller.name} is currently not accepting payments.",
                "cannot_accept_payments",
            )

        min_amount = seller.user_preferences.minimum_amount
        if min_amount > attrs["amount"]:
            raise serializers.ValidationError(
                f"Amount cannot be lower than {min_amount.amount}",
                "min_payment_account",
            )
        return attrs

    def create(self, validated_data):
        buyer = self.context["request"].user
        payment_plan = Plan.for_subscription(
            validated_data["plan"]["amount"],
            validated_data["seller"],
            buyer,
        )
        subscription = payment_plan.subscribe(buyer)
        return subscription
