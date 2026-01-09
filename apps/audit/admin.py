"""
Admin para el sistema de auditoría.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils.safestring import mark_safe
from django.http import HttpResponse
from datetime import timedelta
from django.utils import timezone

from .models import AuditLog, AuditConfig, AuditRetentionLog
from .services import AuditService


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    """Admin para registros de auditoría."""
    
    list_display = [
        'created_at', 'user_display', 'organization', 'action_badge',
        'model_display', 'object_repr_short', 'ip_address'
    ]
    
    list_filter = [
        'action',
        'created_at',
        'organization',
        ('user', admin.RelatedOnlyFieldListFilter),
        'content_type',
    ]
    
    search_fields = [
        'user__email',
        'user__first_name',
        'user__last_name',
        'object_repr',
        'description',
        'ip_address'
    ]
    
    readonly_fields = [
        'created_at', 'user', 'organization', 'action', 'content_type',
        'object_id', 'object_repr', 'changes_display', 'ip_address',
        'user_agent', 'metadata', 'description'
    ]
    
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('created_at', 'action', 'user', 'organization')
        }),
        ('Objeto Afectado', {
            'fields': ('content_type', 'object_id', 'object_repr')
        }),
        ('Cambios', {
            'fields': ('changes_display', 'description')
        }),
        ('Información de Solicitud', {
            'fields': ('ip_address', 'user_agent', 'metadata')
        }),
    )
    
    actions = ['export_csv', 'export_json', 'delete_selected_logs']
    
    def has_add_permission(self, request):
        """No permitir creación manual."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Solo lectura."""
        return False
    
    def user_display(self, obj):
        """Muestra el usuario con enlace."""
        if obj.user:
            url = reverse('admin:users_user_change', args=[obj.user.pk])
            return format_html('<a href="{}">{}</a>', url, obj.user.get_full_name())
        return 'Sistema'
    user_display.short_description = 'Usuario'
    
    def action_badge(self, obj):
        """Muestra la acción con color."""
        colors = {
            'CREATE': 'success',
            'UPDATE': 'info',
            'DELETE': 'danger',
            'VIEW': 'secondary',
            'LOGIN': 'primary',
            'LOGOUT': 'warning',
            'LOGIN_FAILED': 'danger',
        }
        color = colors.get(obj.action, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_action_display()
        )
    action_badge.short_description = 'Acción'
    
    def model_display(self, obj):
        """Muestra el modelo."""
        if obj.content_type:
            return obj.content_type.model
        return '-'
    model_display.short_description = 'Modelo'
    
    def object_repr_short(self, obj):
        """Muestra una versión corta del objeto."""
        if len(obj.object_repr) > 50:
            return obj.object_repr[:50] + '...'
        return obj.object_repr
    object_repr_short.short_description = 'Objeto'
    
    def changes_display(self, obj):
        """Muestra los cambios en formato HTML."""
        if not obj.changes:
            return "Sin cambios"
        
        html = '<table style="width:100%; border-collapse: collapse;">'
        html += '<tr><th style="border: 1px solid #ddd; padding: 8px;">Campo</th>'
        html += '<th style="border: 1px solid #ddd; padding: 8px;">Antes</th>'
        html += '<th style="border: 1px solid #ddd; padding: 8px;">Después</th></tr>'
        
        for field, values in obj.changes.items():
            if isinstance(values, dict) and 'old' in values and 'new' in values:
                html += f'<tr><td style="border: 1px solid #ddd; padding: 8px;"><strong>{field}</strong></td>'
                html += f'<td style="border: 1px solid #ddd; padding: 8px;">{values["old"] or "-"}</td>'
                html += f'<td style="border: 1px solid #ddd; padding: 8px;">{values["new"] or "-"}</td></tr>'
            else:
                html += f'<tr><td style="border: 1px solid #ddd; padding: 8px;"><strong>{field}</strong></td>'
                html += f'<td colspan="2" style="border: 1px solid #ddd; padding: 8px;">{values}</td></tr>'
        
        html += '</table>'
        return mark_safe(html)
    changes_display.short_description = 'Cambios'
    
    def export_csv(self, request, queryset):
        """Exporta los logs seleccionados a CSV."""
        output = AuditService.export_to_csv(queryset)
        
        response = HttpResponse(output.getvalue(), content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="audit_logs.csv"'
        return response
    export_csv.short_description = "Exportar a CSV"
    
    def export_json(self, request, queryset):
        """Exporta los logs seleccionados a JSON."""
        output = AuditService.export_to_json(queryset)
        
        response = HttpResponse(output, content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename="audit_logs.json"'
        return response
    export_json.short_description = "Exportar a JSON"
    
    def delete_selected_logs(self, request, queryset):
        """Elimina los logs seleccionados."""
        count = queryset.count()
        queryset.delete()
        self.message_user(request, f"{count} registros eliminados exitosamente.")
    delete_selected_logs.short_description = "Eliminar logs seleccionados"


@admin.register(AuditConfig)
class AuditConfigAdmin(admin.ModelAdmin):
    """Admin para configuración de auditoría."""
    
    list_display = [
        'model_name', 'organization', 'track_creates', 'track_updates',
        'track_deletes', 'track_reads', 'retention_days', 'is_active'
    ]
    
    list_filter = [
        'is_active',
        'track_creates',
        'track_updates',
        'track_deletes',
        'track_reads',
        'organization'
    ]
    
    search_fields = ['model_name', 'organization__name']
    
    fieldsets = (
        ('Configuración Básica', {
            'fields': ('model_name', 'organization', 'is_active')
        }),
        ('Acciones a Auditar', {
            'fields': ('track_creates', 'track_updates', 'track_deletes', 'track_reads')
        }),
        ('Retención', {
            'fields': ('retention_days',)
        }),
        ('Exclusiones', {
            'fields': ('excluded_fields',),
            'description': 'Lista de campos que no se auditarán (formato JSON)'
        }),
    )
    
    actions = ['activate_configs', 'deactivate_configs']
    
    def activate_configs(self, request, queryset):
        """Activa las configuraciones seleccionadas."""
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} configuraciones activadas.")
    activate_configs.short_description = "Activar configuraciones"
    
    def deactivate_configs(self, request, queryset):
        """Desactiva las configuraciones seleccionadas."""
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} configuraciones desactivadas.")
    deactivate_configs.short_description = "Desactivar configuraciones"


@admin.register(AuditRetentionLog)
class AuditRetentionLogAdmin(admin.ModelAdmin):
    """Admin para registros de limpieza."""
    
    list_display = [
        'executed_at', 'logs_deleted', 'oldest_date_deleted',
        'duration_seconds'
    ]
    
    readonly_fields = [
        'executed_at', 'logs_deleted', 'oldest_date_deleted',
        'duration_seconds', 'details'
    ]
    
    date_hierarchy = 'executed_at'
    
    def has_add_permission(self, request):
        """No permitir creación manual."""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Solo lectura."""
        return False
