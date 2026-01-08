from django.contrib import admin
from .models import CashRegister, CashMovement, CashClosure, CashCategory


@admin.register(CashCategory)
class CashCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'category_type', 'organization', 'is_active', 'created_at']
    list_filter = ['category_type', 'is_active', 'organization']
    search_fields = ['name', 'description']
    readonly_fields = ['created_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('organization', 'name', 'category_type', 'is_active')
        }),
        ('Detalles', {
            'fields': ('description',)
        }),
        ('Auditoría', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )


@admin.register(CashRegister)
class CashRegisterAdmin(admin.ModelAdmin):
    list_display = ['name', 'organization', 'status', 'current_balance', 'responsible', 'is_active']
    list_filter = ['status', 'is_active', 'organization']
    search_fields = ['name', 'location']
    readonly_fields = ['current_balance', 'opened_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('organization', 'name', 'location', 'is_active')
        }),
        ('Estado Actual', {
            'fields': ('status', 'responsible', 'current_balance', 'opened_at', 'opening_amount')
        }),
        ('Auditoría', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CashMovement)
class CashMovementAdmin(admin.ModelAdmin):
    list_display = ['created_at', 'cash_register', 'movement_type', 'category', 'amount', 'payment_method', 'created_by']
    list_filter = ['movement_type', 'category', 'payment_method', 'created_at', 'is_deleted']
    search_fields = ['description', 'reference']
    readonly_fields = ['balance_before', 'balance_after', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Movimiento', {
            'fields': ('cash_register', 'organization', 'movement_type', 'category', 'payment_method')
        }),
        ('Detalles', {
            'fields': ('amount', 'description', 'reference')
        }),
        ('Relaciones', {
            'fields': ('sale',),
            'classes': ('collapse',)
        }),
        ('Balance', {
            'fields': ('balance_before', 'balance_after'),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at', 'is_deleted'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CashClosure)
class CashClosureAdmin(admin.ModelAdmin):
    list_display = ['closure_date', 'cash_register', 'expected_amount', 'total_counted', 'difference', 'status', 'closed_by']
    list_filter = ['status', 'closure_date', 'organization']
    search_fields = ['notes']
    readonly_fields = ['total_counted', 'difference', 'created_at', 'reviewed_at']
    date_hierarchy = 'closure_date'
    
    fieldsets = (
        ('Información General', {
            'fields': ('cash_register', 'organization', 'closure_date', 'status')
        }),
        ('Montos del Sistema', {
            'fields': ('opening_amount', 'total_income', 'total_expenses', 'expected_amount')
        }),
        ('Conteo Físico', {
            'fields': ('counted_cash', 'counted_cards', 'counted_transfers', 'counted_checks', 'counted_other', 'total_counted')
        }),
        ('Resultado', {
            'fields': ('difference', 'notes')
        }),
        ('Desglose', {
            'fields': ('denomination_breakdown',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('closed_by', 'reviewed_by', 'created_at', 'reviewed_at'),
            'classes': ('collapse',)
        }),
    )
