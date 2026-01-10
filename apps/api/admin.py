"""
Admin para API
"""
from django.contrib import admin
from apps.api.models import APIKey, APILog, RateLimitRecord, APIWebhook


@admin.register(APIKey)
class APIKeyAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'key_prefix', 'user', 'organization', 'scope',
        'status', 'total_requests', 'last_used_at', 'created_at'
    ]
    list_filter = ['status', 'scope', 'created_at', 'organization']
    search_fields = ['name', 'key_prefix', 'user__email', 'user__username']
    readonly_fields = [
        'key', 'key_prefix', 'key_hash',
        'last_used_at', 'last_used_ip', 'total_requests',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'user', 'organization', 'scope', 'status')
        }),
        ('API Key', {
            'fields': ('key', 'key_prefix', 'key_hash'),
            'classes': ('collapse',)
        }),
        ('Restricciones', {
            'fields': ('allowed_ips', 'allowed_endpoints', 'rate_limit', 'expires_at')
        }),
        ('Uso', {
            'fields': ('last_used_at', 'last_used_ip', 'total_requests'),
            'classes': ('collapse',)
        }),
        ('Notas', {
            'fields': ('notes',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['revoke_keys', 'activate_keys']
    
    def revoke_keys(self, request, queryset):
        """Revoca las API keys seleccionadas"""
        updated = queryset.update(status='revoked')
        self.message_user(request, f'{updated} API keys revocadas')
    revoke_keys.short_description = 'Revocar API keys seleccionadas'
    
    def activate_keys(self, request, queryset):
        """Activa las API keys seleccionadas"""
        updated = queryset.update(status='active')
        self.message_user(request, f'{updated} API keys activadas')
    activate_keys.short_description = 'Activar API keys seleccionadas'


@admin.register(APILog)
class APILogAdmin(admin.ModelAdmin):
    list_display = [
        'created_at', 'method', 'endpoint', 'response_status',
        'response_time', 'api_key', 'user', 'ip_address'
    ]
    list_filter = [
        'method', 'response_status', 'created_at', 'organization'
    ]
    search_fields = [
        'endpoint', 'ip_address', 'user__email',
        'api_key__name', 'api_key__key_prefix'
    ]
    readonly_fields = [
        'api_key', 'user', 'organization', 'method', 'endpoint',
        'full_path', 'request_headers', 'request_body', 'request_params',
        'response_status', 'response_body', 'response_time',
        'ip_address', 'user_agent', 'error_message', 'stack_trace',
        'created_at'
    ]
    
    fieldsets = (
        ('Request', {
            'fields': (
                'method', 'endpoint', 'full_path', 'request_params',
                'request_headers', 'request_body'
            )
        }),
        ('Response', {
            'fields': ('response_status', 'response_body', 'response_time')
        }),
        ('Autenticación', {
            'fields': ('api_key', 'user', 'organization')
        }),
        ('Cliente', {
            'fields': ('ip_address', 'user_agent')
        }),
        ('Error', {
            'fields': ('error_message', 'stack_trace'),
            'classes': ('collapse',)
        }),
        ('Fecha', {
            'fields': ('created_at',)
        }),
    )
    
    def has_add_permission(self, request):
        """No permitir crear logs manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir editar logs"""
        return False


@admin.register(RateLimitRecord)
class RateLimitRecordAdmin(admin.ModelAdmin):
    list_display = [
        'limit_type', 'identifier', 'endpoint', 'request_count',
        'limit', 'is_blocked', 'window_end'
    ]
    list_filter = ['limit_type', 'is_blocked', 'created_at', 'organization']
    search_fields = ['identifier', 'endpoint']
    readonly_fields = [
        'limit_type', 'identifier', 'api_key', 'user', 'organization',
        'endpoint', 'request_count', 'window_start', 'window_end',
        'limit', 'is_blocked', 'blocked_until', 'created_at', 'updated_at'
    ]
    
    def has_add_permission(self, request):
        """No permitir crear registros manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir editar registros"""
        return False


@admin.register(APIWebhook)
class APIWebhookAdmin(admin.ModelAdmin):
    list_display = [
        'name', 'url', 'api_key', 'status', 'is_active',
        'total_triggers', 'total_successes', 'total_failures',
        'success_rate', 'last_triggered_at'
    ]
    list_filter = ['status', 'is_active', 'created_at', 'organization']
    search_fields = ['name', 'url', 'api_key__name']
    readonly_fields = [
        'secret', 'last_triggered_at', 'last_success_at', 'last_failure_at',
        'total_triggers', 'total_successes', 'total_failures',
        'created_at', 'updated_at'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'url', 'api_key', 'organization')
        }),
        ('Configuración', {
            'fields': ('events', 'status', 'is_active', 'headers', 'secret')
        }),
        ('Reintentos', {
            'fields': ('retry_on_failure', 'max_retries')
        }),
        ('Estadísticas', {
            'fields': (
                'last_triggered_at', 'last_success_at', 'last_failure_at',
                'total_triggers', 'total_successes', 'total_failures'
            ),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['test_webhooks', 'activate_webhooks', 'deactivate_webhooks']
    
    def success_rate(self, obj):
        """Calcula el porcentaje de éxito"""
        if obj.total_triggers == 0:
            return '100%'
        rate = (obj.total_successes / obj.total_triggers) * 100
        return f'{rate:.1f}%'
    success_rate.short_description = 'Tasa Éxito'
    
    def test_webhooks(self, request, queryset):
        """Prueba los webhooks seleccionados"""
        from apps.api.services import WebhookService
        from django.utils import timezone
        
        tested = 0
        for webhook in queryset:
            test_payload = {
                'event': 'test',
                'data': {'message': 'Test from admin'},
                'timestamp': timezone.now().isoformat()
            }
            WebhookService.trigger_webhook(webhook, test_payload)
            tested += 1
        
        self.message_user(request, f'{tested} webhooks probados')
    test_webhooks.short_description = 'Probar webhooks seleccionados'
    
    def activate_webhooks(self, request, queryset):
        """Activa los webhooks seleccionados"""
        updated = queryset.update(is_active=True, status='active')
        self.message_user(request, f'{updated} webhooks activados')
    activate_webhooks.short_description = 'Activar webhooks'
    
    def deactivate_webhooks(self, request, queryset):
        """Desactiva los webhooks seleccionados"""
        updated = queryset.update(is_active=False, status='inactive')
        self.message_user(request, f'{updated} webhooks desactivados')
    deactivate_webhooks.short_description = 'Desactivar webhooks'
