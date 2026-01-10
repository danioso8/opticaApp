from django.contrib import admin
from .models import (
    Notification, NotificationChannel, NotificationPreference,
    NotificationTemplate, NotificationBatch
)


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ['title', 'user', 'notification_type', 'priority', 'is_read', 'created_at']
    list_filter = ['notification_type', 'priority', 'is_read', 'created_at']
    search_fields = ['title', 'message', 'user__username', 'user__email']
    readonly_fields = ['created_at', 'read_at', 'created_by']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('user', 'organization', 'title', 'message')
        }),
        ('Configuración', {
            'fields': ('notification_type', 'priority', 'action_url', 'action_label')
        }),
        ('Estado', {
            'fields': ('is_read', 'read_at', 'expires_at')
        }),
        ('Metadatos', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_unread']
    
    def mark_as_read(self, request, queryset):
        from django.utils import timezone
        count = queryset.update(is_read=True, read_at=timezone.now())
        self.message_user(request, f'{count} notificaciones marcadas como leídas')
    mark_as_read.short_description = 'Marcar como leídas'
    
    def mark_as_unread(self, request, queryset):
        count = queryset.update(is_read=False, read_at=None)
        self.message_user(request, f'{count} notificaciones marcadas como no leídas')
    mark_as_unread.short_description = 'Marcar como no leídas'


@admin.register(NotificationChannel)
class NotificationChannelAdmin(admin.ModelAdmin):
    list_display = ['notification', 'channel', 'recipient', 'status', 'sent_at', 'retry_count']
    list_filter = ['channel', 'status', 'sent_at']
    search_fields = ['recipient', 'notification__title']
    readonly_fields = ['sent_at', 'delivered_at', 'read_at', 'created_at', 'updated_at']
    
    fieldsets = (
        ('Canal', {
            'fields': ('notification', 'organization', 'channel', 'recipient')
        }),
        ('Estado', {
            'fields': ('status', 'error_message', 'response_data')
        }),
        ('Timestamps', {
            'fields': ('sent_at', 'delivered_at', 'read_at')
        }),
        ('Reintentos', {
            'fields': ('retry_count', 'max_retries')
        }),
    )
    
    actions = ['retry_failed']
    
    def retry_failed(self, request, queryset):
        retried = 0
        for channel in queryset.filter(status='failed'):
            if channel.can_retry():
                # Aquí iría la lógica de reenvío
                channel.retry_count += 1
                channel.save()
                retried += 1
        self.message_user(request, f'{retried} envíos reintentados')
    retry_failed.short_description = 'Reintentar envíos fallidos'


@admin.register(NotificationPreference)
class NotificationPreferenceAdmin(admin.ModelAdmin):
    list_display = ['user', 'notification_type', 'is_enabled', 'organization']
    list_filter = ['is_enabled', 'notification_type']
    search_fields = ['user__username', 'user__email', 'notification_type']
    
    fieldsets = (
        ('Usuario', {
            'fields': ('user', 'organization')
        }),
        ('Preferencia', {
            'fields': ('notification_type', 'is_enabled')
        }),
        ('Canales', {
            'fields': ('enabled_channels', 'channel_config')
        }),
    )


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'default_type', 'is_active', 'organization']
    list_filter = ['default_type', 'is_active']
    search_fields = ['name', 'code', 'description']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('code', 'name', 'description', 'organization')
        }),
        ('Plantilla', {
            'fields': ('title_template', 'message_template')
        }),
        ('Configuración', {
            'fields': ('default_type', 'default_channels', 'expected_variables')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
    )


@admin.register(NotificationBatch)
class NotificationBatchAdmin(admin.ModelAdmin):
    list_display = ['name', 'status', 'total_recipients', 'sent_count', 'failed_count', 'success_rate', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['name', 'description']
    readonly_fields = ['total_recipients', 'sent_count', 'failed_count', 'started_at', 'completed_at', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información', {
            'fields': ('name', 'description', 'organization', 'template')
        }),
        ('Estado', {
            'fields': ('status', 'scheduled_at', 'started_at', 'completed_at')
        }),
        ('Estadísticas', {
            'fields': ('total_recipients', 'sent_count', 'failed_count')
        }),
        ('Auditoría', {
            'fields': ('created_by', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def success_rate(self, obj):
        return f"{obj.success_rate:.1f}%"
    success_rate.short_description = 'Tasa de Éxito'
