# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Donation


@admin.register(Donation)
class DonationAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "updated_at",
        "sender_user",
        "receiver_user",
        "name",
        "is_anonymous",
        "status",
        "amount",
    )
    list_filter = (
        "created_at",
        "updated_at",
        "sender_user",
        "receiver_user",
        "is_anonymous",
    )
    search_fields = ("name",)
    date_hierarchy = "created_at"
