"""
Admin para workflows
"""
from django.contrib import admin
from django.utils.html import format_html
from apps.workflows.models import (
    WorkflowDefinition, WorkflowTransition, WorkflowAction,
    WorkflowInstance, WorkflowHistory, WorkflowApproval
)


class WorkflowTransitionInline(admin.TabularInline):
    model = WorkflowTransition
    extra = 0
    fields = ['name', 'from_state', 'to_state', 'require_approval', 'order', 'is_active']


class WorkflowActionInline(admin.TabularInline):
    model = WorkflowAction
    extra = 0
    fields = ['name', 'action_type', 'trigger', 'order', 'is_active']


@admin.register(WorkflowDefinition)
class WorkflowDefinitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'organization', 'content_type', 'is_active', 'created_at']
    list_filter = ['is_active', 'organization', 'content_type', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'description', 'organization')
        }),
        ('Configuración', {
            'fields': ('content_type', 'initial_state', 'states', 'final_states')
        }),
        ('Opciones', {
            'fields': ('is_active', 'auto_start', 'require_approval')
        }),
        ('Metadata', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [WorkflowTransitionInline, WorkflowActionInline]


@admin.register(WorkflowTransition)
class WorkflowTransitionAdmin(admin.ModelAdmin):
    list_display = ['name', 'workflow', 'from_to_badge', 'require_approval', 'order', 'is_active']
    list_filter = ['workflow', 'require_approval', 'is_active', 'organization']
    search_fields = ['name', 'workflow__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información', {
            'fields': ('workflow', 'organization', 'name')
        }),
        ('Transición', {
            'fields': ('from_state', 'to_state', 'order')
        }),
        ('Condiciones y Permisos', {
            'fields': ('conditions', 'required_permission')
        }),
        ('Aprobación', {
            'fields': ('require_approval', 'approval_roles')
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def from_to_badge(self, obj):
        """Muestra la transición con flecha"""
        return format_html(
            '<span style="background-color: #0d6efd; padding: 3px 8px; border-radius: 3px; color: white; font-size: 11px;">'
            '{} → {}'
            '</span>',
            obj.from_state,
            obj.to_state
        )
    from_to_badge.short_description = 'Transición'


@admin.register(WorkflowAction)
class WorkflowActionAdmin(admin.ModelAdmin):
    list_display = ['name', 'workflow', 'action_type', 'trigger', 'order', 'is_active']
    list_filter = ['action_type', 'trigger', 'is_active', 'workflow']
    search_fields = ['name', 'workflow__name']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información', {
            'fields': ('workflow', 'organization', 'name')
        }),
        ('Acción', {
            'fields': ('action_type', 'trigger', 'parameters', 'order')
        }),
        ('Relación', {
            'fields': ('transition', 'state'),
            'classes': ('collapse',)
        }),
        ('Estado', {
            'fields': ('is_active',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(WorkflowInstance)
class WorkflowInstanceAdmin(admin.ModelAdmin):
    list_display = ['workflow', 'current_state_badge', 'status_badge', 'started_by', 'started_at']
    list_filter = ['workflow', 'status', 'current_state', 'organization', 'started_at']
    search_fields = ['workflow__name']
    readonly_fields = ['started_at', 'completed_at', 'content_type', 'object_id']
    
    fieldsets = (
        ('Workflow', {
            'fields': ('workflow', 'organization')
        }),
        ('Objeto', {
            'fields': ('content_type', 'object_id')
        }),
        ('Estado', {
            'fields': ('current_state', 'status', 'data')
        }),
        ('Info', {
            'fields': ('started_by', 'started_at', 'completed_at', 'error_message')
        }),
    )
    
    actions = ['complete_instances', 'cancel_instances']
    
    def current_state_badge(self, obj):
        """Muestra badge con el estado actual"""
        return format_html(
            '<span style="background-color: #0d6efd; padding: 3px 8px; border-radius: 3px; color: white; font-size: 11px;">{}</span>',
            obj.current_state
        )
    current_state_badge.short_description = 'Estado Actual'
    
    def status_badge(self, obj):
        """Muestra badge con el status"""
        colors = {
            'active': '#28a745',
            'completed': '#198754',
            'cancelled': '#dc3545',
            'suspended': '#ffc107',
            'error': '#dc3545',
        }
        return format_html(
            '<span style="background-color: {}; padding: 3px 8px; border-radius: 3px; color: white; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Status'
    
    def complete_instances(self, request, queryset):
        """Completa las instancias seleccionadas"""
        for instance in queryset:
            instance.complete()
        self.message_user(request, f'{queryset.count()} instancias completadas')
    complete_instances.short_description = 'Completar instancias'
    
    def cancel_instances(self, request, queryset):
        """Cancela las instancias seleccionadas"""
        for instance in queryset:
            instance.cancel()
        self.message_user(request, f'{queryset.count()} instancias canceladas')
    cancel_instances.short_description = 'Cancelar instancias'


@admin.register(WorkflowHistory)
class WorkflowHistoryAdmin(admin.ModelAdmin):
    list_display = ['instance', 'transition_badge', 'user', 'created_at']
    list_filter = ['created_at', 'organization']
    search_fields = ['instance__workflow__name', 'user__username', 'comment']
    readonly_fields = ['instance', 'organization', 'transition', 'from_state', 'to_state', 'user', 'comment', 'metadata', 'ip_address', 'created_at']
    
    fieldsets = (
        ('Instancia', {
            'fields': ('instance', 'organization')
        }),
        ('Transición', {
            'fields': ('transition', 'from_state', 'to_state')
        }),
        ('Usuario', {
            'fields': ('user', 'comment')
        }),
        ('Metadata', {
            'fields': ('metadata', 'ip_address', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """No permitir crear historial manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir editar historial"""
        return False
    
    def transition_badge(self, obj):
        """Muestra la transición con flecha"""
        return format_html(
            '<span style="background-color: #0d6efd; padding: 3px 8px; border-radius: 3px; color: white; font-size: 11px;">'
            '{} → {}'
            '</span>',
            obj.from_state,
            obj.to_state
        )
    transition_badge.short_description = 'Transición'


@admin.register(WorkflowApproval)
class WorkflowApprovalAdmin(admin.ModelAdmin):
    list_display = ['instance', 'transition', 'status_badge', 'requested_by', 'approver', 'requested_at']
    list_filter = ['status', 'organization', 'requested_at']
    search_fields = ['instance__workflow__name', 'requested_by__username', 'approver__username']
    readonly_fields = ['requested_at', 'responded_at']
    
    fieldsets = (
        ('Aprobación', {
            'fields': ('instance', 'organization', 'transition')
        }),
        ('Usuarios', {
            'fields': ('requested_by', 'approver')
        }),
        ('Estado', {
            'fields': ('status', 'comment')
        }),
        ('Fechas', {
            'fields': ('requested_at', 'responded_at')
        }),
    )
    
    actions = ['approve_requests', 'reject_requests']
    
    def status_badge(self, obj):
        """Muestra badge con el estado"""
        colors = {
            'pending': '#ffc107',
            'approved': '#28a745',
            'rejected': '#dc3545',
        }
        return format_html(
            '<span style="background-color: {}; padding: 3px 8px; border-radius: 3px; color: white; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def approve_requests(self, request, queryset):
        """Aprueba las solicitudes seleccionadas"""
        from apps.workflows.services import WorkflowApprovalService
        
        for approval in queryset.filter(status='pending'):
            WorkflowApprovalService.approve_transition(approval, request.user)
        
        self.message_user(request, f'Solicitudes aprobadas')
    approve_requests.short_description = 'Aprobar solicitudes'
    
    def reject_requests(self, request, queryset):
        """Rechaza las solicitudes seleccionadas"""
        from apps.workflows.services import WorkflowApprovalService
        
        for approval in queryset.filter(status='pending'):
            WorkflowApprovalService.reject_transition(approval, request.user)
        
        self.message_user(request, f'Solicitudes rechazadas')
    reject_requests.short_description = 'Rechazar solicitudes'
