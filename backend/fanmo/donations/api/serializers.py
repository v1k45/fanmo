from django.conf import settings
from djmoney.contrib.django_rest_framework.fields import MoneyField
from drf_spectacular.utils import extend_schema_field
from rest_framework import serializers

from fanmo.core.serializers import PaymentIntentSerializerMixin
from fanmo.donations.constants import DONATION_TIERS
from fanmo.donations.models import Donation
from fanmo.posts.api.serializers import (
    PostPreviewSerializer,
    PostReactionSummarySerializer,
)
from fanmo.posts.models import Post, Reaction
from fanmo.users.api.serializers import FanUserPreviewSerializer, UserPreviewSerializer
from fanmo.utils.fields import VersatileImageFieldSerializer


class RazorpayPayloadSerializer(serializers.ModelSerializer):
    key = serializers.SerializerMethodField()
    order_id = serializers.CharField(source="external_id")
    name = serializers.CharField(source="creator_user.display_name")
    prefill = serializers.SerializerMethodField()
    notes = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    theme = serializers.SerializerMethodField()

    class Meta:
        model = Donation
        fields = ["key", "order_id", "name", "prefill", "notes", "image", "theme"]

    def get_key(self, _):
        return settings.RAZORPAY_KEY

    def get_prefill(self, donation):
        fan_user = donation.fan_user
        return {"name": fan_user.display_name, "email": fan_user.email}

    def get_notes(self, donation):
        return {"donation_id": donation.id}

    def get_image(self, donation):
        serializer = VersatileImageFieldSerializer("user_avatar")
        serializer._context = self.context
        avatar_renditions = serializer.to_representation(donation.creator_user.avatar)
        return avatar_renditions["thumbnail"] if avatar_renditions else None

    def get_theme(self, donation):
        return {"color": "#6266f1"}


class DonationPaymentSerializer(serializers.ModelSerializer):
    processor = serializers.CharField(read_only=True, default="razorpay")
    payload = RazorpayPayloadSerializer(source="*", read_only=True)
    is_required = serializers.SerializerMethodField()

    def get_is_required(self, donation):
        return donation.status == Donation.Status.PENDING

    class Meta:
        model = Donation
        fields = ["processor", "payload", "is_required"]


class DonationReactionSerializer(serializers.ModelSerializer):
    action = serializers.ChoiceField(choices=["add", "remove"])
    emoji = serializers.ChoiceField(choices=Reaction.Emoji.choices)

    class Meta:
        model = Donation
        fields = ["action", "emoji"]

    def update(self, instance, validated_data):
        user = self.context["request"].user
        if validated_data["action"] == "add":
            Reaction.objects.update_or_create(
                donation=instance, author_user=user, emoji=validated_data["emoji"]
            )
        else:
            Reaction.objects.filter(
                donation=instance, author_user=user, emoji=validated_data["emoji"]
            ).delete()
        return instance


class DonationSocialStatsSerializer(serializers.ModelSerializer):
    reactions = serializers.SerializerMethodField()
    comment_count = serializers.SerializerMethodField()

    class Meta:
        model = Donation
        fields = ["reactions", "comment_count"]

    @extend_schema_field(PostReactionSummarySerializer(many=True))
    def get_reactions(self, post):
        reaction_summary = {}
        for reaction in post.reactions.all():
            reaction_summary.setdefault(
                reaction.emoji,
                {"count": 0, "is_reacted": False, "emoji": reaction.emoji},
            )
            reaction_summary[reaction.emoji]["count"] += 1

            if reaction.author_user_id == self.context["request"].user.pk:
                reaction_summary[reaction.emoji]["is_reacted"] = True

        return reaction_summary.values()

    @extend_schema_field(serializers.IntegerField())
    def get_comment_count(self, donation):
        return getattr(donation, "comment_count", 0)


class DonationTierSerializer(serializers.Serializer):
    name = serializers.CharField()
    min_amount = MoneyField(
        max_digits=7,
        decimal_places=2,
        default_currency="INR",
    )
    max_length = serializers.IntegerField()


class DonationCreateSerializer(
    PaymentIntentSerializerMixin, serializers.ModelSerializer
):
    amount = MoneyField(
        max_digits=7,
        decimal_places=2,
        default_currency="INR",
    )
    post_id = serializers.PrimaryKeyRelatedField(
        source="post",
        queryset=Post.objects.filter(is_published=True, is_purchaseable=True),
        required=False,
        allow_null=True,
    )
    payment = DonationPaymentSerializer(source="*", read_only=True)
    fan_user = FanUserPreviewSerializer(read_only=True)
    creator_user = UserPreviewSerializer(read_only=True)
    stats = DonationSocialStatsSerializer(source="*", read_only=True)
    can_comment = serializers.SerializerMethodField()
    tier = DonationTierSerializer(read_only=True)

    class Meta:
        model = Donation
        fields = [
            "id",
            "creator_username",
            "email",
            "fan_user",
            "creator_user",
            "post_id",
            "amount",
            "message",
            "is_hidden",
            "stats",
            "can_comment",
            "tier",
            "payment",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "fan_user",
            "creator_user",
            "stats",
            "can_comment",
            "tier",
            "created_at",
        ]

    def validate(self, attrs):
        attrs["fan_user"] = self.get_fan_user(attrs.pop("email", None))
        user_preferences = attrs["creator_user"].user_preferences

        post = attrs.get("post", None)
        if post is not None:
            if attrs["creator_user"].pk != post.author_user_id:
                raise serializers.ValidationError(
                    f"This post does not belong to {attrs['creator_user'].display_name}.",
                    "invalid",
                )
            if attrs["amount"] < post.minimum_amount:
                raise serializers.ValidationError(
                    f"Please tip at least {post.minimum_amount} to unlock this post.",
                    "min_amount",
                )

        # validate min amount
        if attrs["amount"] < user_preferences.minimum_amount:
            raise serializers.ValidationError(
                f"Please tip at least {user_preferences.minimum_amount} to support {attrs['creator_user'].display_name}.",
                "min_amount",
            )

        # validate message length
        if user_preferences.enable_donation_tiers and attrs["message"]:
            donation_tier = Donation(
                creator_user=attrs["creator_user"], amount=attrs["amount"]
            ).tier()
            if not donation_tier:
                raise serializers.ValidationError(
                    f"Please tip at least {DONATION_TIERS[0]['min_amount']} to include a message.",
                    "min_tier",
                )
            elif len(attrs["message"]) > donation_tier["max_length"]:
                raise serializers.ValidationError(
                    "Message is too long, increase tip amount to send a larger message.",
                    "invalid_tier",
                )
        return attrs

    def get_can_comment(self, donation):
        return self.context["request"].user.pk in [
            donation.creator_user_id,
            donation.fan_user_id,
        ]

    def create(self, validated_data):
        donation = super().create(validated_data)
        donation.create_external()
        return donation


class DonationSerializer(serializers.ModelSerializer):
    fan_user = FanUserPreviewSerializer()
    creator_user = UserPreviewSerializer()
    post = PostPreviewSerializer(read_only=True)
    message = serializers.SerializerMethodField()
    lifetime_amount = serializers.SerializerMethodField()
    stats = DonationSocialStatsSerializer(source="*", read_only=True)
    can_comment = serializers.SerializerMethodField()
    tier = DonationTierSerializer(read_only=True)

    class Meta:
        model = Donation
        fields = [
            "id",
            "fan_user",
            "creator_user",
            "post",
            "message",
            "amount",
            "is_hidden",
            "lifetime_amount",
            "status",
            "stats",
            "can_comment",
            "tier",
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

    def get_can_comment(self, donation):
        return self.context["request"].user.pk in [
            donation.creator_user_id,
            donation.fan_user_id,
        ]

    @extend_schema_field(serializers.DecimalField(max_digits=7, decimal_places=2))
    def get_lifetime_amount(self, donation):
        return serializers.DecimalField(
            max_digits=7, decimal_places=2
        ).to_representation(getattr(donation, "lifetime_amount", 0))


class PublicDonationSerializer(DonationSerializer):
    fan_user = UserPreviewSerializer()


class DonationUpdateSerializer(DonationSerializer):
    class Meta:
        model = Donation
        fields = [
            "id",
            "fan_user",
            "creator_user",
            "message",
            "amount",
            "is_hidden",
            "status",
            "stats",
            "can_comment",
            "tier",
            "created_at",
        ]
        read_only_fields = [
            "id",
            "fan_user",
            "creator_user",
            "message",
            "amount",
            "status",
            "stats",
            "can_comment",
            "tier",
            "created_at",
        ]


class DonationStatsSerializer(serializers.Serializer):
    total = serializers.IntegerField()
    total_with_message = serializers.IntegerField()
    total_without_message = serializers.IntegerField()
    total_payment = serializers.DecimalField(max_digits=9, decimal_places=2)
