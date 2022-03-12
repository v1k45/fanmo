# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Plan, Subscription, Tier


@admin.register(Tier)
class TierAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "description",
        "amount",
        "is_active",
        "is_public",
        "creator_user",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "created_at",
        "updated_at",
        "is_active",
        "is_public",
    )
    search_fields = ("name",)
    date_hierarchy = "created_at"


@admin.register(Plan)
class PlanAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "updated_at",
        "name",
        "tier",
        "amount_currency",
        "amount",
        "external_id",
        "seller_user",
        "buyer_user",
        "is_active",
    )
    list_filter = (
        "created_at",
        "updated_at",
        "tier",
        "seller_user",
        "buyer_user",
        "is_active",
    )
    search_fields = ("name",)
    date_hierarchy = "created_at"


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "updated_at",
        "plan",
        "status",
        "external_id",
        "cycle_start_at",
        "cycle_end_at",
        "is_active",
        "seller_user",
        "buyer_user",
        "scheduled_to_cancel",
        "scheduled_to_change",
    )
    list_filter = (
        "created_at",
        "updated_at",
        "plan",
        "cycle_start_at",
        "cycle_end_at",
        "is_active",
        "seller_user",
        "buyer_user",
        "scheduled_to_cancel",
        "scheduled_to_change",
    )
    date_hierarchy = "created_at"
