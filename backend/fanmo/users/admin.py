from django.contrib import admin, messages
from django.contrib.auth import admin as auth_admin
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _

from fanmo.core.notifications import notify_creator_approved
from fanmo.core.tasks import async_task
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


class CreatorUser(User):
    class Meta:
        proxy = True


@admin.register(CreatorUser)
class OnboardingAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            _("Personal info"),
            {
                "fields": (
                    "name",
                    "username",
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
            _("Important dates"),
            {"fields": ("last_login", "date_joined"), "classes": ["collapse"]},
        ),
    )
    list_display = [
        "display_name",
        "is_bank_account_added",
        "is_creator_approved",
        "onboarding_status",
        "updated_at",
        "created_at",
    ]
    list_filter = [
        "user_onboarding__is_bank_account_added",
        "user_onboarding__is_creator_approved",
        "user_onboarding__status",
        "is_active",
    ]
    search_fields = ["name", "username", "email"]
    inlines = [UserOnboardingAdmin, BankAccountAdmin, UserPreferenceAdmin]
    date_hierarchy = "created_at"

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_creator=True)

    def is_bank_account_added(self, user):
        return user.user_onboarding.is_bank_account_added

    is_bank_account_added.boolean = True

    def is_creator_approved(self, user):
        return user.user_onboarding.is_creator_approved

    is_creator_approved.boolean = True

    def onboarding_status(self, user):
        return user.user_onboarding.get_status_display()

    def save_model(self, request, obj, form, change):
        send_approval = False
        # if approval is happening for the first time.
        if obj.user_onboarding.status == UserOnboarding.Status.COMPLETED:
            if (
                not obj.user_onboarding.is_bank_account_added
                or not obj.user_onboarding.is_creator_approved
            ):
                messages.add_message(
                    request,
                    messages.ERROR,
                    "Approval email not sent because of incomplete data.",
                )
            else:
                send_approval = (
                    UserOnboarding.objects.filter(id=obj.user_onboarding.id)
                    .exclude(status=UserOnboarding.Status.COMPLETED)
                    .exists()
                )

        super().save_model(request, obj, form, change)
        if send_approval:
            async_task(notify_creator_approved, obj.id)
            messages.add_message(request, messages.INFO, "Sent creator approval email.")

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
