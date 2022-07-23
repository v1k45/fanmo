# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import WebhookMessage


@admin.register(WebhookMessage)
class WebhookMessageAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "updated_at",
        "sender",
        "payload",
        "external_id",
    )
    list_filter = ("created_at", "updated_at", "is_processed")
    date_hierarchy = "created_at"
