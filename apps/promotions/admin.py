"""
Admin para el módulo de promociones
"""
from django.contrib import admin
from apps.promotions.models import Promotion, PromotionCampaign, PromotionMessage, PromotionUsage


@admin.register(Promotion)
class PromotionAdmin(admin.ModelAdmin):
    list_display = ['code', 'name', 'discount_percentage', 'category', 'status', 'start_date', 'end_date', 'current_uses']
    list_filter = ['status', 'category', 'organization']
    search_fields = ['code', 'name', 'description']
    readonly_fields = ['created_at', 'updated_at', 'current_uses']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('organization', 'code', 'name', 'description')
        }),
        ('Descuento', {
            'fields': ('discount_percentage', 'category')
        }),
        ('Vigencia', {
            'fields': ('start_date', 'end_date', 'status')
        }),
        ('Límites de Uso', {
            'fields': ('max_uses', 'current_uses')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PromotionCampaign)
class PromotionCampaignAdmin(admin.ModelAdmin):
    list_display = ['name', 'promotion', 'status', 'messages_sent', 'messages_pending', 'created_at']
    list_filter = ['status', 'organization']
    search_fields = ['name', 'promotion__code']
    readonly_fields = ['created_at', 'updated_at', 'started_at', 'completed_at', 'total_recipients', 'messages_sent', 'messages_failed', 'messages_pending']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('organization', 'promotion', 'name', 'message_template')
        }),
        ('Destinatarios', {
            'fields': ('recipient_filter', 'total_recipients')
        }),
        ('Configuración de Envío', {
            'fields': ('daily_limit', 'delay_seconds', 'send_hour_start', 'send_hour_end')
        }),
        ('Estado', {
            'fields': ('status', 'scheduled_date', 'started_at', 'completed_at')
        }),
        ('Estadísticas', {
            'fields': ('messages_sent', 'messages_failed', 'messages_pending')
        }),
        ('Metadatos', {
            'fields': ('created_at', 'updated_at', 'created_by'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PromotionMessage)
class PromotionMessageAdmin(admin.ModelAdmin):
    list_display = ['patient', 'campaign', 'status', 'phone_number', 'sent_at']
    list_filter = ['status', 'campaign']
    search_fields = ['patient__full_name', 'phone_number']
    readonly_fields = ['created_at', 'sent_at', 'send_attempts']
    
    fieldsets = (
        ('Información', {
            'fields': ('campaign', 'patient', 'phone_number')
        }),
        ('Mensaje', {
            'fields': ('message_text',)
        }),
        ('Estado', {
            'fields': ('status', 'error_message', 'send_attempts', 'max_attempts')
        }),
        ('Fechas', {
            'fields': ('scheduled_for', 'sent_at', 'created_at')
        }),
    )


@admin.register(PromotionUsage)
class PromotionUsageAdmin(admin.ModelAdmin):
    list_display = ['promotion', 'patient', 'discount_applied', 'used_at', 'reference']
    list_filter = ['promotion', 'used_at']
    search_fields = ['patient__full_name', 'reference', 'promotion__code']
    readonly_fields = ['used_at']
    
    fieldsets = (
        ('Información', {
            'fields': ('promotion', 'patient')
        }),
        ('Detalles', {
            'fields': ('discount_applied', 'reference', 'notes')
        }),
        ('Fecha', {
            'fields': ('used_at',)
        }),
    )
