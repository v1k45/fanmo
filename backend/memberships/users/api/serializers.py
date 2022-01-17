import django_otp
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.account.utils import filter_users_by_email
from django.contrib.auth import password_validation
from django.forms import ValidationError
from django_otp.plugins.otp_email.models import EmailDevice
from django_otp.plugins.otp_totp.models import TOTPDevice
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers
from rest_framework.exceptions import ErrorDetail
from versatileimagefield.serializers import VersatileImageFieldSerializer

from memberships.subscriptions.models import Tier
from memberships.users.models import SocialLink, User, UserPreference


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


class RequestEmailVerificationSerializer(serializers.Serializer):
    def validate(self, attrs):
        email = EmailAddress.objects.get(user=self.instance)
        if email.verified:
            raise serializers.ValidationError(
                "This e-mail has been already verified.", "already_verified"
            )
        return attrs

    def save(self, *args, **kwargs):
        request = self.context["request"]
        email_device, _ = EmailDevice.objects.get_or_create(user=request.user)
        get_adapter(request).send_confirmation_mail(request, email_device, signup=False)


class VerifyEmailSerializer(serializers.Serializer):
    code = serializers.CharField()

    def validate(self, attrs):
        email = EmailAddress.objects.get(user=self.instance)
        if email.verified:
            raise serializers.ValidationError(
                "This e-mail has already been verified.", "already_verified"
            )

        device = django_otp.match_token(self.instance, attrs["code"])
        if not device:
            raise serializers.ValidationError(
                {
                    "code": ErrorDetail(
                        "Verification code is invalid or expired.", "invalid_otp"
                    )
                }
            )

        return {"email_address": email}

    def save(self, *args, **kwargs):
        request = self.context["request"]._request
        get_adapter(request).confirm_email(
            request, self.validated_data["email_address"]
        )


class TOTPDeviceSerializer(serializers.ModelSerializer):
    qrcode = serializers.HyperlinkedIdentityField("mfa-qrcode")

    class Meta:
        model = TOTPDevice
        fields = ["name", "qrcode", "confirmed"]
        read_only_fields = fields

    def validate(self, attrs):
        mfa_devices = TOTPDevice.objects.all().filter(user=self.context["request"].user)
        if not self.instance and mfa_devices.exists():
            raise serializers.ValidationError(
                "You can only have one MFA Device at a time.", "mfa_exists"
            )
        return attrs

    def create(self, validated_data):
        validated_data["name"] = "MFA Device"
        validated_data["confirmed"] = False
        return super().create(validated_data)


class PasswordResetSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, email):
        self.users = filter_users_by_email(email)
        if not self.users:
            raise serializers.ValidationError(
                "We couldn't find a user with this email."
            )
        return email

    def save(self, **kwargs):
        user = self.users[0]
        email_device, _ = EmailDevice.objects.get_or_create(user=user)
        request = self.context["request"]._request
        get_adapter(request).send_password_reset_mail(request, email_device)
        return user


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
    new_password = serializers.CharField(max_length=128)

    def validate_email(self, email):
        self.users = filter_users_by_email(email)
        if not self.users:
            raise serializers.ValidationError(
                "We couldn't find a user with this email."
            )
        return email

    def validate(self, attrs):
        user = self.users[0]
        email_device, _ = EmailDevice.objects.get_or_create(user=user)
        if not email_device.verify_token(attrs["code"]):
            raise serializers.ValidationError(
                "Verification code is invalid or expired.", "invalid_otp"
            )

        new_password = attrs["new_password"]
        try:
            password_validation.validate_password(new_password, user)
        except ValidationError as e:
            raise serializers.ValidationError({"new_password": e.error_list})
        return {"user": user, "new_password": new_password}

    def save(self, **kwargs):
        user = self.validated_data["user"]
        user.set_password(self.validated_data["new_password"])
        user.save()
        return user
