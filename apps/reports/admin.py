"""
Admin para el sistema de reportes.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.http import HttpResponse

from .models import ReportTemplate, Report, ScheduledReport, ReportShare
from .services import ReportService


@admin.register(ReportTemplate)
class ReportTemplateAdmin(admin.ModelAdmin):
    """Admin para plantillas de reporte."""
    
    list_display = [
        'name', 'report_type', 'organization', 'is_public',
        'is_system', 'is_active', 'created_at'
    ]
    
    list_filter = [
        'report_type',
        'is_public',
        'is_system',
        'is_active',
        'organization'
    ]
    
    search_fields = [
        'name',
        'description'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'report_type', 'description', 'organization', 'created_by')
        }),
        ('Configuración', {
            'fields': ('columns', 'default_filters', 'grouping', 'ordering')
        }),
        ('Avanzado', {
            'fields': ('config', 'custom_query'),
            'classes': ('collapse',)
        }),
        ('Permisos', {
            'fields': ('is_public', 'is_system', 'is_active')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    actions = ['activate_templates', 'deactivate_templates']
    
    def activate_templates(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} plantillas activadas.")
    activate_templates.short_description = "Activar plantillas"
    
    def deactivate_templates(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} plantillas desactivadas.")
    deactivate_templates.short_description = "Desactivar plantillas"


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    """Admin para reportes generados."""
    
    list_display = [
        'name', 'template', 'organization', 'generated_by',
        'status_badge', 'output_format', 'total_records',
        'created_at'
    ]
    
    list_filter = [
        'status',
        'output_format',
        'template__report_type',
        'organization',
        'created_at'
    ]
    
    search_fields = [
        'name',
        'generated_by__email',
        'generated_by__first_name',
        'generated_by__last_name'
    ]
    
    readonly_fields = [
        'template', 'organization', 'generated_by', 'status',
        'total_records', 'generation_time', 'created_at',
        'completed_at', 'error_message'
    ]
    
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'template', 'organization', 'generated_by')
        }),
        ('Parámetros', {
            'fields': ('parameters', 'date_from', 'date_to', 'output_format')
        }),
        ('Estado', {
            'fields': ('status', 'error_message', 'total_records', 
                      'generation_time', 'created_at', 'completed_at')
        }),
        ('Resultados', {
            'fields': ('results', 'file', 'expires_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['download_reports', 'delete_expired']
    
    def has_add_permission(self, request):
        """No permitir creación manual."""
        return False
    
    def status_badge(self, obj):
        """Muestra badge de estado."""
        colors = {
            'pending': 'secondary',
            'processing': 'info',
            'completed': 'success',
            'failed': 'danger'
        }
        color = colors.get(obj.status, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def download_reports(self, request, queryset):
        """Descarga los reportes seleccionados."""
        # TODO: Implementar descarga
        self.message_user(request, "Función en desarrollo")
    download_reports.short_description = "Descargar reportes"
    
    def delete_expired(self, request, queryset):
        """Elimina reportes expirados."""
        expired = queryset.filter(expires_at__lte=timezone.now())
        count = expired.count()
        expired.delete()
        self.message_user(request, f"{count} reportes eliminados.")
    delete_expired.short_description = "Eliminar expirados"


@admin.register(ScheduledReport)
class ScheduledReportAdmin(admin.ModelAdmin):
    """Admin para reportes programados."""
    
    list_display = [
        'name', 'template', 'frequency', 'organization',
        'is_active', 'last_run_at', 'next_run_at'
    ]
    
    list_filter = [
        'frequency',
        'is_active',
        'organization',
        'template__report_type'
    ]
    
    search_fields = [
        'name',
        'description'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'template', 'organization', 'created_by')
        }),
        ('Programación', {
            'fields': ('frequency', 'day_of_week', 'day_of_month', 'time')
        }),
        ('Configuración', {
            'fields': ('parameters', 'output_format', 'recipients')
        }),
        ('Estado', {
            'fields': ('is_active', 'last_run_at', 'last_run_status', 'next_run_at')
        }),
    )
    
    readonly_fields = ['last_run_at', 'last_run_status', 'next_run_at']
    
    actions = ['activate_schedules', 'deactivate_schedules', 'execute_now']
    
    def activate_schedules(self, request, queryset):
        count = queryset.update(is_active=True)
        self.message_user(request, f"{count} programaciones activadas.")
    activate_schedules.short_description = "Activar programaciones"
    
    def deactivate_schedules(self, request, queryset):
        count = queryset.update(is_active=False)
        self.message_user(request, f"{count} programaciones desactivadas.")
    deactivate_schedules.short_description = "Desactivar programaciones"
    
    def execute_now(self, request, queryset):
        """Ejecuta los reportes programados ahora."""
        from .services import ScheduledReportService
        
        # TODO: Ejecutar solo los seleccionados
        result = ScheduledReportService.execute_scheduled_reports()
        self.message_user(
            request,
            f"Ejecutados: {result['executed']}, Fallidos: {result['failed']}"
        )
    execute_now.short_description = "Ejecutar ahora"


@admin.register(ReportShare)
class ReportShareAdmin(admin.ModelAdmin):
    """Admin para reportes compartidos."""
    
    list_display = [
        'report', 'shared_by', 'recipient_display',
        'created_at', 'viewed_at', 'expires_at'
    ]
    
    list_filter = [
        'created_at',
        'expires_at'
    ]
    
    search_fields = [
        'report__name',
        'shared_by__email',
        'shared_with__email',
        'shared_with_email'
    ]
    
    readonly_fields = [
        'report', 'shared_by', 'created_at', 'viewed_at'
    ]
    
    def has_add_permission(self, request):
        """No permitir creación manual."""
        return False
    
    def recipient_display(self, obj):
        """Muestra el destinatario."""
        if obj.shared_with:
            return obj.shared_with.email
        return obj.shared_with_email
    recipient_display.short_description = 'Destinatario'
