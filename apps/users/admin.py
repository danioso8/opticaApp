from django.contrib import admin
from .models import UserSubscription, PaymentMethod, Transaction, SubscriptionRenewalLog
from .email_verification_models import EmailVerificationToken, UserProfile


@admin.register(UserSubscription)
class UserSubscriptionAdmin(admin.ModelAdmin):
    list_display = ['user', 'plan', 'billing_cycle', 'start_date', 'end_date', 'is_active', 'payment_status', 'auto_renew', 'days_remaining']
    list_filter = ['is_active', 'payment_status', 'billing_cycle', 'plan', 'auto_renew']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['created_at', 'updated_at', 'days_remaining']
    date_hierarchy = 'start_date'
    
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


@admin.register(PaymentMethod)
class PaymentMethodAdmin(admin.ModelAdmin):
    list_display = ['user', 'card_brand', 'card_last_four', 'card_type', 'is_default', 'is_active', 'created_at']
    list_filter = ['card_brand', 'card_type', 'is_default', 'is_active']
    search_fields = ['user__username', 'user__email', 'card_holder_name', 'card_last_four']
    readonly_fields = ['wompi_token_id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Información de la Tarjeta', {
            'fields': ('card_brand', 'card_last_four', 'card_type', 'card_holder_name')
        }),
        ('Token de Wompi', {
            'fields': ('wompi_token_id',),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('is_default', 'is_active')
        }),
        ('Información del Sistema', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'transaction_type', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['status', 'transaction_type', 'currency', 'created_at']
    search_fields = ['user__username', 'user__email', 'wompi_transaction_id', 'wompi_reference']
    readonly_fields = ['id', 'wompi_transaction_id', 'created_at', 'updated_at', 'processed_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Identificadores', {
            'fields': ('id', 'wompi_transaction_id', 'wompi_reference')
        }),
        ('Usuario y Relaciones', {
            'fields': ('user', 'subscription', 'payment_method')
        }),
        ('Información de la Transacción', {
            'fields': ('transaction_type', 'amount', 'currency', 'status', 'status_message')
        }),
        ('Información de Wompi', {
            'fields': ('wompi_payment_method_type', 'wompi_payment_link_id'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at', 'processed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        return False


@admin.register(SubscriptionRenewalLog)
class SubscriptionRenewalLogAdmin(admin.ModelAdmin):
    list_display = ['subscription', 'status', 'amount_attempted', 'email_sent', 'attempted_at', 'completed_at']
    list_filter = ['status', 'email_sent', 'attempted_at']
    search_fields = ['subscription__user__username', 'subscription__user__email', 'error_message']
    readonly_fields = ['attempted_at', 'completed_at']
    date_hierarchy = 'attempted_at'
    
    fieldsets = (
        ('Suscripción', {
            'fields': ('subscription', 'transaction')
        }),
        ('Resultado', {
            'fields': ('status', 'amount_attempted', 'error_message')
        }),
        ('Notificación', {
            'fields': ('email_sent',)
        }),
        ('Fechas', {
            'fields': ('attempted_at', 'completed_at')
        }),
    )
    
    def has_add_permission(self, request):
        return False


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'is_email_verified', 'email_verified_at', 'created_at']
    list_filter = ['is_email_verified', 'created_at']
    search_fields = ['user__username', 'user__email', 'user__first_name', 'user__last_name', 'phone']
    readonly_fields = ['created_at', 'updated_at', 'email_verified_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Verificación de Email', {
            'fields': ('is_email_verified', 'email_verified_at')
        }),
        ('Información Adicional', {
            'fields': ('phone',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(EmailVerificationToken)
class EmailVerificationTokenAdmin(admin.ModelAdmin):
    list_display = ['user', 'token', 'is_used', 'is_expired_status', 'created_at']
    list_filter = ['is_used', 'created_at']
    search_fields = ['user__username', 'user__email', 'token']
    readonly_fields = ['token', 'created_at', 'expires_at', 'is_expired_status', 'is_valid_status']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user',)
        }),
        ('Token', {
            'fields': ('token', 'is_used')
        }),
        ('Validez', {
            'fields': ('created_at', 'expires_at', 'is_expired_status', 'is_valid_status')
        }),
    )
    
    def is_expired_status(self, obj):
        return obj.is_expired
    is_expired_status.short_description = '¿Expirado?'
    is_expired_status.boolean = True
    
    def is_valid_status(self, obj):
        return obj.is_valid
    is_valid_status.short_description = '¿Válido?'
    is_valid_status.boolean = True
    
    def has_add_permission(self, request):
        return False
