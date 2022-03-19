from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from memberships.users.forms import UserChangeForm, UserCreationForm
from memberships.users.models import UserOnboarding

User = get_user_model()


@admin.register(User)
class UserAdmin(auth_admin.UserAdmin):

    form = UserChangeForm
    add_form = UserCreationForm
    fieldsets = (
        (None, {"fields": ("username", "email_verified", "is_creator", "password")}),
        (_("Personal info"), {"fields": ("name", "email", "avatar", "cover", "about")}),
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
            },
        ),
        (_("Important dates"), {"fields": ("last_login", "date_joined")}),
    )
    list_display = ["username", "name", "is_superuser"]
    search_fields = ["name"]
    date_hierarchy = "created_at"


@admin.register(UserOnboarding)
class UserOnboardingAdmin(admin.ModelAdmin):
    list_display = ["user", "full_name", "status", "updated_at", "created_at"]
    list_filter = ["status", "user__is_creator"]
    search_fields = [
        "user__name",
        "user__username",
        "user__email",
        "full_name",
        "introduction",
        "mobile",
    ]
    date_hierarchy = "created_at"
