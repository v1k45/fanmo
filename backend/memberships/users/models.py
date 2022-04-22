import base64
from functools import cached_property, lru_cache
from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from versatileimagefield.fields import VersatileImageField
from simple_history.models import HistoricalRecords

from memberships.payments.models import BankAccount
from memberships.utils.models import BaseModel


class User(BaseModel, AbstractUser):
    # First and last name do not cover name patterns around the globe
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    one_liner = models.CharField(max_length=150, blank=True)
    first_name = None
    last_name = None

    avatar = VersatileImageField(
        upload_to="profiles/avatars/",
        blank=True,
    )
    cover = VersatileImageField(
        upload_to="profiles/covers/",
        blank=True,
    )
    about = models.TextField(blank=True)

    email_verified = models.BooleanField(default=False)
    is_creator = models.BooleanField(null=True)

    followers = models.ManyToManyField(
        "self",
        through="users.Following",
        through_fields=("from_user", "to_user"),
        symmetrical=False,
        related_name="followings",
    )
    subscriber_count = models.PositiveSmallIntegerField(default=0)
    follower_count = models.PositiveSmallIntegerField(default=0)

    def get_absolute_url(self):
        return reverse("users:detail", kwargs={"username": self.username})

    def public_tiers(self):
        return self.tiers.filter(is_public=True)

    @property
    def display_name(self):
        return self.name or self.username

    @cached_property
    def can_accept_payments(self):
        return (
            self.is_creator
            and self.user_onboarding.is_creator_approved
            and self.user_preferences.is_accepting_payments
            and self.bank_accounts.filter(status=BankAccount.Status.LINKED).exists()
        )

    def will_accept(self, amount):
        return (
            self.can_accept_payments()
            and self.user_preferences.minimum_amount <= amount
        )

    def follow(self, follower_user):
        self.followers.add(follower_user)
        self.follower_count = self.followers.count()
        self.save()

    def unfollow(self, follower_user):
        self.followers.remove(follower_user)
        self.follower_count = self.followers.count()
        self.save()

    def email_base64(self):
        return base64.urlsafe_b64encode(self.email.encode()).decode("utf-8")

    @lru_cache
    def get_membership(self, creator_user_id):
        # PERF: assumes memberships are prefetched!
        return next(
            (
                membership
                for membership in self.memberships.all()
                if membership.is_active
                and membership.creator_user_id == creator_user_id
            ),
            None,
        )


class SocialLink(models.Model):
    user = models.OneToOneField(
        "users.User", on_delete=models.CASCADE, related_name="social_links"
    )

    website_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)
    facebook_url = models.URLField(blank=True)
    instagram_url = models.URLField(blank=True)
    twitter_url = models.URLField(blank=True)


class Following(BaseModel):
    from_user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="from_followings"
    )
    to_user = models.ForeignKey(
        "users.User", on_delete=models.CASCADE, related_name="to_followings"
    )

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=["from_user", "to_user"], name="following")
        ]


class UserPreference(BaseModel):
    user = models.OneToOneField(
        "users.User", on_delete=models.CASCADE, related_name="user_preferences"
    )

    is_accepting_payments = models.BooleanField(default=True)
    donation_description = models.TextField(blank=True)
    thank_you_message = models.TextField(default=settings.DEFAULT_THANK_YOU_MESSAGE)
    minimum_amount = MoneyField(
        max_digits=7, decimal_places=2, default=settings.MINIMUM_PAYMENT_AMOUNT
    )

    platform_fee_percent = models.DecimalField(
        decimal_places=2, max_digits=3, default=settings.DEFAULT_PLATFORM_FEE_PERCENT
    )

    history = HistoricalRecords()


class UserOnboarding(BaseModel):
    class Status(models.TextChoices):
        IN_PROGRESS = "in_progress"
        SUBMITTED = "submitted"
        ON_HOLD = "on_hold"
        COMPLETED = "completed"

    user = models.OneToOneField(
        "users.User", on_delete=models.CASCADE, related_name="user_onboarding"
    )
    full_name = models.CharField(max_length=255, blank=True)
    introduction = models.TextField(blank=True)
    mobile = models.CharField(max_length=10, blank=True)
    status = models.CharField(
        max_length=30, choices=Status.choices, default=Status.IN_PROGRESS
    )
    is_bank_account_added = models.BooleanField(default=False)
    is_creator_approved = models.BooleanField(default=False)
    notes = models.TextField(blank=True)

    def get_checklist(self):
        return {
            "type_selection": self.user.is_creator is not None,
            "email_verification": self.user.email_verified,
            "introduction": bool(self.full_name and self.introduction),
            "payment_setup": bool(self.is_bank_account_added),
        }
