# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import ApplicationEvent, StatisticByDateAndObject


@admin.register(ApplicationEvent)
class ApplicationEventAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "name",
        "payload",
        "donation",
        "subscription",
        "created_at",
        "updated_at",
    )
    list_filter = (
        "created_at",
        "updated_at",
    )
    date_hierarchy = "created_at"


@admin.register(StatisticByDateAndObject)
class StatisticByDateAndObjectAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "date",
        "period",
        "object",
        "metric",
        "value",
        "created_at",
        "updated_at",
    )
    list_filter = ("created_at", "updated_at")
    date_hierarchy = "created_at"
