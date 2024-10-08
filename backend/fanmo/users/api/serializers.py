import bleach
import django_otp
from allauth.account.adapter import get_adapter
from allauth.account.models import EmailAddress
from allauth.account.utils import filter_users_by_email
from dj_rest_auth.registration.serializers import (
    RegisterSerializer as BaseRegisterSerializer,
)
from dj_rest_auth.registration.serializers import (
    SocialLoginSerializer as BaseSocialLoginSerializer,
)
from dj_rest_auth.serializers import (
    PasswordChangeSerializer as RestAuthPasswordResetSerializer,
)
from django.contrib.auth import password_validation
from django.db.models import Value
from django.db.models.functions import Replace
from django.forms import ValidationError
from django_otp.plugins.otp_email.models import EmailDevice
from django_otp.plugins.otp_totp.models import TOTPDevice
from djmoney.contrib.django_rest_framework.fields import MoneyField
from drf_extra_fields.fields import Base64ImageField
from drf_spectacular.utils import extend_schema_field
from ipware import get_client_ip
from rest_framework import serializers
from rest_framework.exceptions import ErrorDetail

from fanmo.core.notifications import notify_password_change
from fanmo.core.tasks import async_task
from fanmo.memberships.models import Tier
from fanmo.users.models import (
    CreatorActivity,
    SocialLink,
    User,
    UserOnboarding,
    UserPreference,
)
from fanmo.utils.fields import URLField, VersatileImageFieldSerializer


class RegisterSerializer(BaseRegisterSerializer):
    name = serializers.CharField(max_length=255, required=False)
    password = serializers.CharField(write_only=True, source="password1")

    # remove the originally defined fields in the serializer
    username = None
    password1 = None
    password2 = None

    def validate(self, data):
        """Override default serializer validation to disable password comparison"""
        return data

    def get_cleaned_data(self):
        return {
            "name": self.validated_data.get("name", ""),
            **super().get_cleaned_data(),
        }


class SocialLoginSerializer(BaseSocialLoginSerializer):
    """
    Extension over default social login serializer to finish onboarding of supporters on login.
    """

    is_creator = serializers.BooleanField(required=False)

    def validate(self, attrs):
        is_creator = attrs.pop("is_creator", None)
        attrs = super().validate(attrs)

        # mark onboarding as completed if the user is not a creator
        if is_creator is not None:
            attrs["user"].is_creator = is_creator
            attrs["user"].save()

            attrs["user"].user_onboarding.status = UserOnboarding.Status.COMPLETED
            attrs["user"].user_onboarding.save()

        return attrs


class UserTierSerializer(serializers.ModelSerializer):
    cover = VersatileImageFieldSerializer("tier_cover")

    class Meta:
        model = Tier
        fields = [
            "id",
            "name",
            "description",
            "amount",
            "cover",
            "cover_background_style",
            "benefits",
            "is_recommended",
        ]


class DonationTierSerializer(serializers.Serializer):
    name = serializers.CharField()
    min_amount = MoneyField(
        max_digits=7,
        decimal_places=2,
        default_currency="INR",
    )
    max_length = serializers.IntegerField()


class SocialLinkSerializer(serializers.ModelSerializer):
    website_url = URLField(required=False, allow_blank=True)
    youtube_url = URLField(required=False, allow_blank=True)
    facebook_url = URLField(required=False, allow_blank=True)
    instagram_url = URLField(required=False, allow_blank=True)
    twitter_url = URLField(required=False, allow_blank=True)

    class Meta:
        model = SocialLink
        fields = [
            "website_url",
            "youtube_url",
            "facebook_url",
            "instagram_url",
            "twitter_url",
        ]


class PublicUserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = [
            "enable_donation_tiers",
            "default_donation_amount",
            "is_accepting_payments",
            "minimum_amount",
            "thank_you_message",
            "donation_description",
        ]


class UserPreferenceSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserPreference
        fields = [
            "enable_donation_tiers",
            "default_donation_amount",
            "is_accepting_payments",
            "minimum_amount",
            "thank_you_message",
            "donation_description",
            "notify_following_posts",
            "notify_comment_replies",
            "notify_post_comments",
            "notify_donations",
            "notify_memberships",
            "notify_marketing",
        ]


class OnboardingChecklist(serializers.Serializer):
    type_selection = serializers.BooleanField()
    email_verification = serializers.BooleanField()
    introduction = serializers.BooleanField()
    payment_setup = serializers.BooleanField()


class UserOnboardingSerializer(serializers.ModelSerializer):
    submit_for_review = serializers.BooleanField(write_only=True, required=False)
    checklist = OnboardingChecklist(source="get_checklist", read_only=True)

    class Meta:
        model = UserOnboarding
        fields = [
            "full_name",
            "introduction",
            "mobile",
            "status",
            "submit_for_review",
            "checklist",
        ]
        read_only_fields = ["status", "submit_for_review", "checklist"]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["full_name"].allow_blank = False
        self.fields["introduction"].allow_blank = False
        self.fields["mobile"].allow_blank = False

    def validate_submit_for_review(self, submit_for_review):
        if not submit_for_review:
            return submit_for_review

        if not self.instance.user.is_creator:
            raise ValidationError(
                "You need to be a creator to submit your page.", "creator_type_required"
            )

        if not self.instance.user.email_verified:
            raise ValidationError(
                "Please verify your e-mail address before submitting your page.",
                "email_verification_required",
            )

        # validate that a bank account has been added
        if not self.instance.is_bank_account_added:
            raise ValidationError(
                "Please add a bank account before submmiting your page.",
                "payment_setup_required",
            )

        return submit_for_review


class ComputedUserFieldSerializer(serializers.Serializer):
    is_following = serializers.SerializerMethodField()
    is_member = serializers.SerializerMethodField()

    @extend_schema_field(serializers.BooleanField())
    def get_is_following(self, user):
        request_user = self.context["request"].user
        if not request_user.is_authenticated:
            return False

        following_user = next(
            (user for f_user in request_user.followings.all() if f_user.id == user.id),
            None,
        )
        return following_user is not None

    @extend_schema_field(serializers.BooleanField())
    def get_is_member(self, user):
        request_user = self.context["request"].user
        if not request_user.is_authenticated:
            return False
        return request_user.get_membership(user.pk) is not None


class PublicUserSerializer(ComputedUserFieldSerializer, serializers.ModelSerializer):
    tiers = UserTierSerializer(many=True, read_only=True, source="public_tiers")
    donation_tiers = DonationTierSerializer(many=True, read_only=True)
    avatar = VersatileImageFieldSerializer("user_avatar")
    cover = VersatileImageFieldSerializer("user_cover")
    social_links = SocialLinkSerializer(read_only=True)
    preferences = PublicUserPreferenceSerializer(
        source="user_preferences", read_only=True
    )

    class Meta:
        model = User
        fields = [
            "username",
            "display_name",
            "name",
            "one_liner",
            "about",
            "avatar",
            "cover",
            "tiers",
            "donation_tiers",
            "social_links",
            "follower_count",
            "preferences",
            "is_creator",
            "is_following",
            "is_member",
        ]


class UserSerializer(ComputedUserFieldSerializer, serializers.ModelSerializer):
    tiers = UserTierSerializer(many=True, read_only=True, source="public_tiers")
    donation_tiers = DonationTierSerializer(many=True, read_only=True)
    social_links = SocialLinkSerializer()
    # TODO: ONLY EXPOSE IT TO OWN USER!!
    preferences = UserPreferenceSerializer(source="user_preferences", required=False)
    onboarding = UserOnboardingSerializer(source="user_onboarding", required=False)
    avatar = VersatileImageFieldSerializer("user_avatar")
    avatar_base64 = Base64ImageField(write_only=True, source="avatar", required=False)
    cover = VersatileImageFieldSerializer("user_cover")
    cover_base64 = Base64ImageField(write_only=True, source="cover", required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "display_name",
            "name",
            "one_liner",
            "email",
            "about",
            "avatar",
            "avatar_base64",
            "cover",
            "cover_base64",
            "tiers",
            "donation_tiers",
            "social_links",
            "preferences",
            "onboarding",
            "follower_count",
            "subscriber_count",
            "is_creator",
            "is_following",
            "is_member",
        ]
        read_only_fields = [
            "display_name",
            "email",
            "tiers",
            "donation_tiers",
            "follower_count",
            "subscriber_count",
            "preferences",
        ]
        extra_kwargs = {"name": {"allow_blank": False}}

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if isinstance(self.instance, User) and self.instance.user_onboarding:
            self.fields["onboarding"].instance = self.instance.user_onboarding
            # Set onboarding to read-only once it is submitted.
            if (
                self.instance.user_onboarding.status
                != UserOnboarding.Status.IN_PROGRESS
            ):
                self.fields["onboarding"].read_only = True

    def validate_about(self, about):
        return bleach.clean(
            about,
            tags=["p", "b", "strong", "i", "u", "strike", "em", "s", "br", "a"],
            attributes={"a": ["href", "rel", "target"]},
        )

    def validate_is_creator(self, is_creator):
        if self.instance.is_creator and not is_creator:
            # Do not let a creator to switch back to supporter once they are verified.
            if self.instance.user_onboarding.is_creator_approved:
                # TODO: Handle this automatically and contact the creator to get clarity.
                raise serializers.ValidationError(
                    "Please contact support to unpublish your page.",
                    "manual_intervention_needed",
                )

        if is_creator is None:
            raise serializers.ValidationError(
                "Please select either creator or supporter."
            )
        return is_creator

    def validate_username(self, value):
        if not self.instance.is_creator:
            raise ValidationError(
                "You need to be a creator to be change your username."
            )
        return value

    def update(self, instance, validated_data):
        user_preferences = validated_data.pop("user_preferences", {})
        user_onboarding = validated_data.pop("user_onboarding", {})
        social_links = validated_data.pop("social_links", {})

        for field_name, value in user_preferences.items():
            setattr(instance.user_preferences, field_name, value)
        instance.user_preferences.save()

        for field_name, value in social_links.items():
            setattr(instance.social_links, field_name, value)
        instance.social_links.save()

        for field_name, value in user_onboarding.items():
            setattr(instance.user_onboarding, field_name, value)
        # set onboarding status
        if user_onboarding.pop("submit_for_review", None):
            instance.user_onboarding.status = UserOnboarding.Status.SUBMITTED

        if (
            instance.is_creator is None
            and validated_data.get("is_creator") is False
            and instance.email_verified
        ):
            # if user selects account type for the first time and their email is already verified mark the onboarding as completed.
            # this can happen when user signs up using social account
            instance.user_onboarding.status = UserOnboarding.Status.COMPLETED

        if not instance.is_creator and validated_data.get(
            "is_creator", instance.is_creator
        ):
            # if a supporter becomes a creator after email verfication, move the onboarding status back to in progress.
            instance.user_onboarding.status = UserOnboarding.Status.IN_PROGRESS
        if instance.is_creator and not validated_data.get(
            "is_creator", instance.is_creator
        ):
            # if a creator becomes a supporter, move the onboarding status back to depend on email verification.
            instance.user_onboarding.status = (
                UserOnboarding.Status.COMPLETED
                if instance.email_verified
                else UserOnboarding.Status.IN_PROGRESS
            )
        instance.user_onboarding.save()

        # update activities if user changes display name
        # this is only a temporary hack
        current_name = instance.name
        new_name = validated_data.get("name", current_name)
        if current_name != new_name:
            CreatorActivity.objects.filter(fan_user=instance).update(
                message=Replace("message", Value(current_name), Value(new_name))
            )

        return super().update(instance, validated_data)


class UserPreviewSerializer(ComputedUserFieldSerializer, serializers.ModelSerializer):
    avatar = VersatileImageFieldSerializer("user_avatar")
    cover = VersatileImageFieldSerializer("user_cover")

    class Meta:
        model = User
        fields = [
            "display_name",
            "username",
            "name",
            "avatar",
            "cover",
            "one_liner",
            "is_creator",
            "is_following",
            "is_member",
        ]


class FanUserPreviewSerializer(serializers.ModelSerializer):
    avatar = VersatileImageFieldSerializer("user_avatar")

    class Meta:
        model = User
        fields = [
            "display_name",
            "username",
            "name",
            "avatar",
            "email",
        ]


class RequestEmailVerificationSerializer(serializers.Serializer):
    def validate(self, attrs):
        # get or create is used so that the endpoint handles users created through system
        email, _ = EmailAddress.objects.get_or_create(
            user=self.instance,
            email=self.instance.email,
            defaults={"verified": False, "primary": True},
        )
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
        # get or create is used so that the endpoint handles users created through system
        email, _ = EmailAddress.objects.get_or_create(
            user=self.instance,
            email=self.instance.email,
            defaults={"verified": False, "primary": True},
        )
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
        request = self.context["request"]._request
        email, _ = EmailAddress.objects.get_or_create(
            user=user,
            email=user.email,
            defaults={"verified": False, "primary": True},
        )
        if not email.verified:
            get_adapter(request).confirm_email(request, email)
        async_task(notify_password_change, user.pk, get_client_ip(request)[0])
        return user


class PasswordChangeSerializer(RestAuthPasswordResetSerializer):
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        request = self.context["request"]._request
        async_task(notify_password_change, request.user.pk, get_client_ip(request)[0])


class CreatorActivitySerializer(serializers.ModelSerializer):
    fan_user = FanUserPreviewSerializer(read_only=True)

    class Meta:
        model = CreatorActivity
        fields = [
            "id",
            "type",
            "message",
            "data",
            "fan_user",
            "membership",
            "donation",
            "comment",
            "created_at",
        ]

    def get_fields(self):
        from fanmo.donations.api.serializers import DonationSerializer
        from fanmo.memberships.api.serializers import MembershipPreviewSerializer
        from fanmo.posts.api.serializers import CommentPreviewSerializer

        fields = super().get_fields()
        fields["membership"] = MembershipPreviewSerializer(read_only=True)
        fields["donation"] = DonationSerializer(read_only=True)
        fields["comment"] = CommentPreviewSerializer(read_only=True)

        return fields
