from django.contrib import admin

from memberships.subscriptions.models import Plan, Tier


@admin.register(Tier)
class TierAdmin(admin.ModelAdmin):
    list_display = ["name", "seller", "is_public", "created_at"]


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = [
        "name",
        "amount",
        "tier",
        "seller",
        "buyer",
        "is_active",
        "created_at",
    ]
