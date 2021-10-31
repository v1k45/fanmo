# -*- coding: utf-8 -*-
from django.contrib import admin

from .models import Payment, Payout, BankAccount


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "updated_at",
        "subscription",
        "donation",
        "seller_user",
        "buyer_user",
        "status",
        "type",
        "amount_currency",
        "amount",
        "external_id",
    )
    list_filter = (
        "created_at",
        "updated_at",
        "subscription",
        "donation",
        "seller_user",
        "buyer_user",
    )
    date_hierarchy = "created_at"


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "updated_at",
        "payment",
        "status",
        "amount_currency",
        "amount",
        "bank_account",
        "external_id",
    )
    list_filter = ("created_at", "updated_at", "payment", "bank_account")
    date_hierarchy = "created_at"


@admin.register(BankAccount)
class BankAccountAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "created_at",
        "updated_at",
        "beneficiary_user",
        "status",
        "account_name",
        "mobile_number",
        "account_number",
        "account_type",
        "beneficiary_name",
        "ifsc",
        "is_active",
        "external_id",
    )
    list_filter = (
        "created_at",
        "updated_at",
        "beneficiary_user",
        "is_active",
    )
    date_hierarchy = "created_at"
