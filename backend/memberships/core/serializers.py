from rest_framework import serializers
from memberships.users.models import User
from allauth.account.adapter import get_adapter


class PaymentIntentSerializerMixin(serializers.ModelSerializer):
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

    def validate_creator_username(self, creator_user):
        if self.instance and self.instance.creator_user != creator_user:
            raise serializers.ValidationError(
                "Creator cannot be changed. Please create a separate membership.",
            )

        if not creator_user.can_accept_payments:
            raise serializers.ValidationError(
                f"{creator_user.name} is currently not accepting payments.",
                "creator_not_approved",
            )
        return creator_user

    def get_fan_user(self, email=None):
        request = self.context["request"]
        if request.user.is_authenticated:
            return request.user

        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            return existing_user

        adapter = get_adapter(request)
        return adapter.invite(request._request, email)
