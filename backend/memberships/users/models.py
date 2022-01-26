from django.conf import settings
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models import CharField
from django.urls import reverse
from django.utils.translation import gettext_lazy as _
from djmoney.models.fields import MoneyField
from versatileimagefield.fields import VersatileImageField
from versatileimagefield.placeholder import OnDiscPlaceholderImage

from memberships.payments.models import BankAccount
from memberships.utils.models import BaseModel


class User(BaseModel, AbstractUser):
    # First and last name do not cover name patterns around the globe
    name = CharField(_("Name of User"), blank=True, max_length=255)
    first_name = None
    last_name = None

    avatar = VersatileImageField(
        upload_to="profiles/avatars/",
        blank=True,
        placeholder_image=OnDiscPlaceholderImage(
            path=settings.PLACEHOLDERS_DIR / "avatar.jpg"
        ),
    )
    cover = VersatileImageField(
        upload_to="profiles/covers/",
        blank=True,
        placeholder_image=OnDiscPlaceholderImage(
            path=settings.PLACEHOLDERS_DIR / "cover.jpg"
        ),
    )
    about = models.TextField(blank=True)

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

    def can_accept_payments(self):
        return (
            self.user_preferences.is_accepting_payments
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
    minimum_amount = MoneyField(
        max_digits=7, decimal_places=2, default=settings.MINIMUM_PAYMENT_AMOUNT
    )

    platform_fee_percent = models.DecimalField(
        decimal_places=2, max_digits=3, default=settings.DEFAULT_PLATFORM_FEE_PERCENT
    )
