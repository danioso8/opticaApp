from django.contrib import admin
from .models import UserSubscription


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'billing_cycle', 'start_date', 'end_date', 'is_active', 'payment_status', 'days_remaining']
    list_filter = ['is_active', 'payment_status', 'billing_cycle', 'plan']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'days_remaining']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user', 'plan')
        }),
        ('Suscripción', {
            'fields': ('billing_cycle', 'start_date', 'end_date', 'is_active', 'auto_renew')
        }),
        ('Pago', {
            'fields': ('payment_status', 'amount_paid')
        }),
        ('Información', {
            'fields': ('created_at', 'updated_at', 'days_remaining')
        }),
    )
    
    def days_remaining(self, obj):
        if obj.is_expired:
            return "Expirado"
        return f"{obj.days_remaining} días"
    days_remaining.short_description = 'Días Restantes'
