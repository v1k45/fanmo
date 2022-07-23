from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from fanmo.payments.models import BankAccount
from fanmo.users.forms import UserChangeForm, UserCreationForm
from fanmo.users.models import UserOnboarding, UserPreference

User = get_user_model()


class UserOnboardingAdmin(admin.StackedInline):
    model = UserOnboarding
    classes = ["collapse"]


class BankAccountAdmin(admin.StackedInline):
    model = BankAccount
    max_num = 1
    classes = ["collapse"]


class UserPreferenceAdmin(admin.StackedInline):
    model = UserPreference
    classes = ["collapse"]


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
        (None, {"fields": ("username", "password")}),
        (
            _("Personal info"),
            {
                "fields": (
                    "name",
                    "is_creator",
                    "email",
                    "email_verified",
                    "avatar",
                    "cover",
                    "about",
                )
            },
        ),
        (
            _("Permissions"),
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                ),
                "classes": ["collapse"],
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["username", "name", "is_creator", "is_staff", "created_at"]
    list_filter = ["is_creator", "is_staff", "is_superuser", "is_active"]
    search_fields = ["name", "username", "email"]
    inlines = [UserOnboardingAdmin, BankAccountAdmin, UserPreferenceAdmin]
    date_hierarchy = "created_at"
