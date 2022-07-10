# -*- coding: utf-8 -*-
from django.contrib import admin
from memberships.core.admin import SimpleHistoryAdmin

from .models import Donation


@admin.register(Donation)
class DonationAdmin(SimpleHistoryAdmin):
    list_display = (
        "id",
        "created_at",
        "updated_at",
        "creator_user",
        "fan_user",
        "is_hidden",
        "status",
        "amount",
    )
    list_filter = (
        "created_at",
        "updated_at",
        "fan_user",
        "creator_user",
        "is_hidden",
    )
    search_fields = ("name",)
    date_hierarchy = "created_at"
    history_list_display = ["ip_address"]
