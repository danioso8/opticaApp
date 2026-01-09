"""
Admin para tareas
"""
from django.contrib import admin
from django.utils.html import format_html
from apps.tasks.models import (
    TaskCategory, Task, TaskComment, TaskActivity,
    TaskChecklist, TaskReminder
)


@admin.register(TaskCategory)
class TaskCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'organization', 'color_badge', 'is_active', 'created_at']
    list_filter = ['is_active', 'organization', 'created_at']
    search_fields = ['name', 'slug', 'description']
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'slug', 'description', 'organization')
        }),
        ('Apariencia', {
            'fields': ('color', 'icon')
        }),
        ('Estado', {
            'fields': ('is_active', 'created_by')
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def color_badge(self, obj):
        """Muestra un badge con el color"""
        return format_html(
            '<span style="background-color: {}; padding: 5px 10px; border-radius: 3px; color: white;">{}</span>',
            obj.color,
            obj.name
        )
    color_badge.short_description = 'Color'


class TaskCommentInline(admin.TabularInline):
    model = TaskComment
    extra = 0
    fields = ['user', 'comment', 'is_internal', 'created_at']
    readonly_fields = ['created_at']


class TaskChecklistInline(admin.TabularInline):
    model = TaskChecklist
    extra = 0
    fields = ['title', 'items', 'created_at']
    readonly_fields = ['created_at']


@admin.register(Task)
class TaskAdmin(admin.ModelAdmin):
    list_display = [
        'title', 'category', 'status_badge', 'priority_badge',
        'assigned_to', 'due_date', 'progress_bar', 'created_at'
    ]
    list_filter = [
        'status', 'priority', 'category', 'organization',
        'is_recurring', 'created_at', 'due_date'
    ]
    search_fields = ['title', 'description', 'assigned_to__username', 'created_by__username']
    readonly_fields = [
        'completed_at', 'created_at', 'updated_at',
        'is_overdue', 'has_subtasks', 'get_subtasks_count'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'description', 'category', 'organization')
        }),
        ('Estado y Prioridad', {
            'fields': ('status', 'priority', 'progress')
        }),
        ('Asignación', {
            'fields': ('assigned_to', 'created_by')
        }),
        ('Fechas', {
            'fields': ('start_date', 'due_date', 'completed_at')
        }),
        ('Estimación', {
            'fields': ('estimated_hours', 'actual_hours')
        }),
        ('Relación con Objetos', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Recurrencia', {
            'fields': ('is_recurring', 'recurrence_rule', 'parent_task'),
            'classes': ('collapse',)
        }),
        ('Datos Adicionales', {
            'fields': ('tags', 'attachments', 'metadata'),
            'classes': ('collapse',)
        }),
        ('Info', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    inlines = [TaskCommentInline, TaskChecklistInline]
    
    actions = ['mark_as_completed', 'mark_as_cancelled', 'set_high_priority']
    
    def status_badge(self, obj):
        """Muestra un badge con el estado"""
        colors = {
            'pending': '#6c757d',
            'in_progress': '#0d6efd',
            'on_hold': '#ffc107',
            'completed': '#198754',
            'cancelled': '#dc3545',
        }
        return format_html(
            '<span style="background-color: {}; padding: 3px 8px; border-radius: 3px; color: white; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#6c757d'),
            obj.get_status_display()
        )
    status_badge.short_description = 'Estado'
    
    def priority_badge(self, obj):
        """Muestra un badge con la prioridad"""
        colors = {
            'low': '#28a745',
            'medium': '#ffc107',
            'high': '#fd7e14',
            'urgent': '#dc3545',
        }
        return format_html(
            '<span style="background-color: {}; padding: 3px 8px; border-radius: 3px; color: white; font-size: 11px;">{}</span>',
            colors.get(obj.priority, '#6c757d'),
            obj.get_priority_display()
        )
    priority_badge.short_description = 'Prioridad'
    
    def progress_bar(self, obj):
        """Muestra una barra de progreso"""
        color = '#198754' if obj.progress == 100 else '#0d6efd'
        return format_html(
            '<div style="width: 100px; background-color: #e9ecef; border-radius: 3px;">'
            '<div style="width: {}%; background-color: {}; padding: 2px; text-align: center; color: white; border-radius: 3px; font-size: 11px;">'
            '{}%'
            '</div></div>',
            obj.progress,
            color,
            obj.progress
        )
    progress_bar.short_description = 'Progreso'
    
    def mark_as_completed(self, request, queryset):
        """Marca tareas como completadas"""
        for task in queryset:
            task.complete()
        self.message_user(request, f'{queryset.count()} tareas marcadas como completadas')
    mark_as_completed.short_description = 'Marcar como completadas'
    
    def mark_as_cancelled(self, request, queryset):
        """Marca tareas como canceladas"""
        for task in queryset:
            task.cancel()
        self.message_user(request, f'{queryset.count()} tareas canceladas')
    mark_as_cancelled.short_description = 'Cancelar tareas'
    
    def set_high_priority(self, request, queryset):
        """Establece prioridad alta"""
        updated = queryset.update(priority='high')
        self.message_user(request, f'{updated} tareas marcadas como prioridad alta')
    set_high_priority.short_description = 'Marcar como prioridad alta'


@admin.register(TaskComment)
class TaskCommentAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'comment_preview', 'is_internal', 'created_at']
    list_filter = ['is_internal', 'created_at', 'organization']
    search_fields = ['comment', 'task__title', 'user__username']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Información', {
            'fields': ('task', 'organization', 'user')
        }),
        ('Comentario', {
            'fields': ('comment', 'parent_comment', 'is_internal')
        }),
        ('Adjuntos', {
            'fields': ('attachments',),
            'classes': ('collapse',)
        }),
        ('Fechas', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def comment_preview(self, obj):
        """Muestra un preview del comentario"""
        return obj.comment[:100] + '...' if len(obj.comment) > 100 else obj.comment
    comment_preview.short_description = 'Comentario'


@admin.register(TaskActivity)
class TaskActivityAdmin(admin.ModelAdmin):
    list_display = ['task', 'action', 'user', 'description_preview', 'created_at']
    list_filter = ['action', 'created_at', 'organization']
    search_fields = ['task__title', 'user__username', 'description']
    readonly_fields = ['task', 'organization', 'user', 'action', 'description', 'old_value', 'new_value', 'ip_address', 'created_at']
    
    fieldsets = (
        ('Información', {
            'fields': ('task', 'organization', 'user', 'action')
        }),
        ('Detalles', {
            'fields': ('description', 'old_value', 'new_value')
        }),
        ('Metadata', {
            'fields': ('ip_address', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def has_add_permission(self, request):
        """No permitir crear actividades manualmente"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """No permitir editar actividades"""
        return False
    
    def description_preview(self, obj):
        """Muestra un preview de la descripción"""
        return obj.description[:100] if obj.description else '-'
    description_preview.short_description = 'Descripción'


@admin.register(TaskChecklist)
class TaskChecklistAdmin(admin.ModelAdmin):
    list_display = ['title', 'task', 'completion_badge', 'created_at']
    list_filter = ['created_at', 'organization']
    search_fields = ['title', 'task__title']
    readonly_fields = ['created_at', 'updated_at', 'get_completion_percentage']
    
    fieldsets = (
        ('Información', {
            'fields': ('task', 'organization', 'title')
        }),
        ('Items', {
            'fields': ('items',)
        }),
        ('Info', {
            'fields': ('created_by', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    def completion_badge(self, obj):
        """Muestra badge de completitud"""
        percentage = obj.get_completion_percentage()
        color = '#198754' if percentage == 100 else '#0d6efd'
        return format_html(
            '<span style="background-color: {}; padding: 3px 8px; border-radius: 3px; color: white; font-size: 11px;">'
            '{}%'
            '</span>',
            color,
            percentage
        )
    completion_badge.short_description = 'Completitud'


@admin.register(TaskReminder)
class TaskReminderAdmin(admin.ModelAdmin):
    list_display = ['task', 'user', 'reminder_type', 'remind_at', 'is_sent', 'sent_at']
    list_filter = ['reminder_type', 'is_sent', 'remind_at', 'organization']
    search_fields = ['task__title', 'user__username', 'message']
    readonly_fields = ['sent_at', 'created_at']
    
    fieldsets = (
        ('Información', {
            'fields': ('task', 'organization', 'user')
        }),
        ('Recordatorio', {
            'fields': ('reminder_type', 'remind_at', 'message')
        }),
        ('Estado', {
            'fields': ('is_sent', 'sent_at')
        }),
        ('Fecha Creación', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_sent']
    
    def mark_as_sent(self, request, queryset):
        """Marca recordatorios como enviados"""
        from django.utils import timezone
        updated = queryset.update(is_sent=True, sent_at=timezone.now())
        self.message_user(request, f'{updated} recordatorios marcados como enviados')
    mark_as_sent.short_description = 'Marcar como enviados'
