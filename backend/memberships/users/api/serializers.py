from rest_framework import serializers

from memberships.subscriptions.models import Tier
from memberships.users.models import SocialLink, User, UserPreference

from versatileimagefield.serializers import VersatileImageFieldSerializer
from drf_extra_fields.fields import Base64ImageField


class UserTierSerializer(serializers.ModelSerializer):
    # amount = MoneyField(max_digits=7, decimal_places=2, source="plan.amount")

    class Meta:
        model = Tier
        fields = ["id", "name", "description", "amount", "cover", "benefits"]


class SocialLinkSerializer(serializers.ModelSerializer):
    class Meta:
        model = SocialLink
        fields = [
            "website_url",
            "youtube_url",
            "facebook_url",
            "instagram_url",
            "twitter_url",
        ]


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = ["is_accepting_payments", "minimum_amount"]


class UserSerializer(serializers.ModelSerializer):
    tiers = UserTierSerializer(many=True, read_only=True, source="public_tiers")
    social_links = SocialLinkSerializer()
    user_preferences = UserPreferenceSerializer()
    avatar = VersatileImageFieldSerializer("user_avatar")
    avatar_base64 = Base64ImageField(write_only=True, source="avatar", required=False)
    cover = VersatileImageFieldSerializer("user_cover")
    cover_base64 = Base64ImageField(write_only=True, source="cover", required=False)
    is_following = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = [
            "username",
            "name",
            "about",
            "avatar",
            "avatar_base64",
            "cover",
            "cover_base64",
            "tiers",
            "social_links",
            "user_preferences",
            "follower_count",
            "subscriber_count",
            "is_following",
        ]
        read_only_fields = ["tiers", "follower_count", "subscriber_count"]

    def update(self, instance, validated_data):
        user_preferences = validated_data.pop("user_preferences", {})
        social_links = validated_data.pop("social_links", {})

        for field_name, value in user_preferences.items():
            setattr(instance.user_preferences, field_name, value)
        instance.user_preferences.save()

        for field_name, value in social_links.items():
            setattr(instance.social_links, field_name, value)
        instance.social_links.save()

        return super().update(instance, validated_data)

    def get_is_following(self, user):
        request = self.context["request"]
        return user.followers.all().filter(id=request.user.id).exists()


class UserPreviewSerializer(serializers.ModelSerializer):
    avatar = VersatileImageFieldSerializer("user_avatar")

    class Meta:
        model = User
        fields = ["display_name", "username", "name", "avatar"]
