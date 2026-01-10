"""
Admin para el sistema de configuraciones.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe

from .models import AppSetting, IntegrationConfig, SettingCategory
from .services import SettingsService


@admin.register(AppSetting)
class AppSettingAdmin(admin.ModelAdmin):
    """Admin para configuraciones de aplicación."""
    
    list_display = [
        'key', 'value_display', 'value_type', 'organization',
        'module', 'is_active', 'is_sensitive_badge'
    ]
    
    list_filter = [
        'value_type',
        'module',
        'is_active',
        'is_sensitive',
        'organization'
    ]
    
    search_fields = [
        'key',
        'description',
        'value'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('key', 'description', 'module', 'organization')
        }),
        ('Valor', {
            'fields': ('value', 'value_type', 'default_value')
        }),
        ('Validación', {
            'fields': ('validation_rule', 'is_sensitive', 'is_active')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['activate_settings', 'deactivate_settings', 'clear_cache']
    
    def value_display(self, obj):
        """Muestra el valor (oculto si es sensible)."""
        if obj.is_sensitive:
            return '••••••••'
        
        value = str(obj.value)
        if len(value) > 50:
            return value[:50] + '...'
        return value
    value_display.short_description = 'Valor'
    
    def is_sensitive_badge(self, obj):
        """Muestra badge si es dato sensible."""
        if obj.is_sensitive:
            return format_html(
                '<span class="badge badge-warning">Sensible</span>'
            )
        return ''
    is_sensitive_badge.short_description = 'Sensible'
    
    def activate_settings(self, request, queryset):
        """Activa las configuraciones seleccionadas."""
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} configuraciones activadas.")
    activate_settings.short_description = "Activar configuraciones"
    
    def deactivate_settings(self, request, queryset):
        """Desactiva las configuraciones seleccionadas."""
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} configuraciones desactivadas.")
    deactivate_settings.short_description = "Desactivar configuraciones"
    
    def clear_cache(self, request, queryset):
        """Limpia el cache de las configuraciones seleccionadas."""
        for setting in queryset:
            SettingsService.clear_cache(setting.organization)
        self.message_user(request, "Cache limpiado exitosamente.")
    clear_cache.short_description = "Limpiar cache"


@admin.register(IntegrationConfig)
class IntegrationConfigAdmin(admin.ModelAdmin):
    """Admin para configuraciones de integración."""
    
    list_display = [
        'name', 'integration_type', 'organization',
        'is_active', 'is_test_mode', 'is_verified_badge',
        'last_verified_at'
    ]
    
    list_filter = [
        'integration_type',
        'is_active',
        'is_test_mode',
        'is_verified',
        'organization'
    ]
    
    search_fields = [
        'name',
        'organization__name'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('integration_type', 'name', 'organization')
        }),
        ('Configuración', {
            'fields': ('config', 'credentials')
        }),
        ('Estado', {
            'fields': ('is_active', 'is_test_mode', 'is_verified', 
                      'last_verified_at', 'verification_error')
        }),
        ('Metadatos', {
            'fields': ('metadata',),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['last_verified_at', 'is_verified', 'verification_error']
    
    actions = ['activate_integrations', 'deactivate_integrations', 'verify_integrations']
    
    def is_verified_badge(self, obj):
        """Muestra badge de verificación."""
        if obj.is_verified:
            return format_html(
                '<span class="badge badge-success">Verificado</span>'
            )
        elif obj.last_verified_at:
            return format_html(
                '<span class="badge badge-danger">Error</span>'
            )
        return format_html(
            '<span class="badge badge-secondary">No verificado</span>'
        )
    is_verified_badge.short_description = 'Verificación'
    
    def activate_integrations(self, request, queryset):
        """Activa las integraciones seleccionadas."""
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} integraciones activadas.")
    activate_integrations.short_description = "Activar integraciones"
    
    def deactivate_integrations(self, request, queryset):
        """Desactiva las integraciones seleccionadas."""
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} integraciones desactivadas.")
    deactivate_integrations.short_description = "Desactivar integraciones"
    
    def verify_integrations(self, request, queryset):
        """Verifica las integraciones seleccionadas."""
        from .services import IntegrationService
        
        success = 0
        failed = 0
        
        for integration in queryset:
            if IntegrationService.verify_integration(integration.id):
                success += 1
            else:
                failed += 1
        
        self.message_user(
            request,
            f"Verificación completada: {success} exitosas, {failed} fallidas."
        )
    verify_integrations.short_description = "Verificar conexiones"


@admin.register(SettingCategory)
class SettingCategoryAdmin(admin.ModelAdmin):
    """Admin para categorías de configuración."""
    
    list_display = [
        'name', 'slug', 'icon', 'order', 'settings_count'
    ]
    
    search_fields = ['name', 'description']
    
    prepopulated_fields = {'slug': ('name',)}
    
    filter_horizontal = ['settings']
    
    def settings_count(self, obj):
        """Muestra el número de configuraciones."""
        return obj.settings.count()
    settings_count.short_description = 'Configuraciones'
