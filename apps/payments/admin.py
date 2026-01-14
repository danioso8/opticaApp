# -*- coding: utf-8 -*-
from django.contrib import admin
from apps.payments.models import (
    PaymentMethod,
    Transaction,
    Invoice,
    InvoiceItem,
    PaymentPlan
)


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['organization', 'payment_type', 'last_four', 'is_default', 'is_active', 'created_at']
    list_filter = ['payment_type', 'is_default', 'is_active']
    search_fields = ['organization__name', 'last_four']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_number', 'organization', 'transaction_type', 'amount', 'status', 'payment_gateway', 'created_at']
    list_filter = ['status', 'transaction_type', 'payment_gateway', 'created_at']
    search_fields = ['transaction_number', 'organization__name', 'gateway_transaction_id']
    readonly_fields = ['id', 'transaction_number', 'created_at', 'completed_at']
    filter_horizontal = ['modules']


class InvoiceItemInline(admin.TabularInline):
    model = InvoiceItem
    extra = 0
    readonly_fields = ['total_price']


@admin.register(Invoice)
class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['invoice_number', 'organization', 'total', 'status', 'issue_date', 'due_date', 'paid_at']
    list_filter = ['status', 'issue_date', 'due_date']
    search_fields = ['invoice_number', 'organization__name']
    readonly_fields = ['id', 'invoice_number', 'created_at', 'updated_at']
    inlines = [InvoiceItemInline]


@admin.register(PaymentPlan)
class PaymentPlanAdmin(admin.ModelAdmin):
    list_display = ['organization', 'billing_cycle', 'estimated_monthly_amount', 'status', 'next_billing_date']
    list_filter = ['status', 'billing_cycle']
    search_fields = ['organization__name']
    readonly_fields = ['created_at', 'updated_at']
