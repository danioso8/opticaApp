"""
Servicios de lógica de negocio para tareas
"""
from django.utils import timezone
from django.db import transaction
from django.db.models import Q, Count, Avg
from datetime import timedelta

from apps.tasks.models import (
    Task, TaskCategory, TaskComment, TaskActivity,
    TaskChecklist, TaskReminder
)


class TaskService:
    """Servicio para gestión de tareas"""
    
    @staticmethod
    def create_task(organization, created_by, title, **kwargs):
        """
        Crea una nueva tarea
        
        Args:
            organization: Organización
            created_by: Usuario creador
            title: Título de la tarea
            **kwargs: Otros campos opcionales
        
        Returns:
            Task: La tarea creada
        """
        task = Task.objects.create(
            organization=organization,
            created_by=created_by,
            title=title,
            **kwargs
        )
        
        # Registrar actividad
        TaskActivityService.log_activity(
            task=task,
            user=created_by,
            action='created',
            description=f'Tarea creada: {title}'
        )
        
        return task
    
    @staticmethod
    def assign_task(task, assigned_to, assigned_by):
        """
        Asigna una tarea a un usuario
        
        Args:
            task: Tarea a asignar
            assigned_to: Usuario asignado
            assigned_by: Usuario que asigna
        
        Returns:
            Task: La tarea actualizada
        """
        old_assigned = task.assigned_to
        task.assign_to(assigned_to)
        
        # Registrar actividad
        TaskActivityService.log_activity(
            task=task,
            user=assigned_by,
            action='assigned',
            description=f'Asignada a {assigned_to.get_full_name() or assigned_to.username}',
            old_value={'assigned_to': old_assigned.id if old_assigned else None},
            new_value={'assigned_to': assigned_to.id}
        )
        
        return task
    
    @staticmethod
    def update_status(task, new_status, user):
        """
        Actualiza el estado de una tarea
        
        Args:
            task: Tarea
            new_status: Nuevo estado
            user: Usuario que actualiza
        
        Returns:
            Task: La tarea actualizada
        """
        old_status = task.status
        task.status = new_status
        
        if new_status == 'completed':
            task.completed_at = timezone.now()
            task.progress = 100
        
        task.save()
        
        # Registrar actividad
        TaskActivityService.log_activity(
            task=task,
            user=user,
            action='status_changed',
            description=f'Estado cambiado de {old_status} a {new_status}',
            old_value={'status': old_status},
            new_value={'status': new_status}
        )
        
        return task
    
    @staticmethod
    def update_priority(task, new_priority, user):
        """Actualiza la prioridad de una tarea"""
        old_priority = task.priority
        task.priority = new_priority
        task.save()
        
        TaskActivityService.log_activity(
            task=task,
            user=user,
            action='priority_changed',
            description=f'Prioridad cambiada de {old_priority} a {new_priority}',
            old_value={'priority': old_priority},
            new_value={'priority': new_priority}
        )
        
        return task
    
    @staticmethod
    def get_user_tasks(user, status=None, priority=None, due_soon=False):
        """
        Obtiene las tareas de un usuario
        
        Args:
            user: Usuario
            status: Filtrar por estado
            priority: Filtrar por prioridad
            due_soon: Solo tareas que vencen pronto
        
        Returns:
            QuerySet: Tareas del usuario
        """
        tasks = Task.objects.filter(assigned_to=user)
        
        if status:
            tasks = tasks.filter(status=status)
        
        if priority:
            tasks = tasks.filter(priority=priority)
        
        if due_soon:
            soon = timezone.now() + timedelta(days=3)
            tasks = tasks.filter(
                due_date__lte=soon,
                due_date__gte=timezone.now()
            ).exclude(status__in=['completed', 'cancelled'])
        
        return tasks.order_by('due_date', '-priority')
    
    @staticmethod
    def get_overdue_tasks(organization):
        """Obtiene tareas vencidas de una organización"""
        return Task.objects.filter(
            organization=organization,
            due_date__lt=timezone.now()
        ).exclude(
            status__in=['completed', 'cancelled']
        ).order_by('due_date')
    
    @staticmethod
    def get_tasks_by_category(category):
        """Obtiene tareas de una categoría"""
        return Task.objects.filter(category=category).order_by('-created_at')
    
    @staticmethod
    def get_related_tasks(content_type, object_id):
        """Obtiene tareas relacionadas con un objeto específico"""
        return Task.objects.filter(
            content_type=content_type,
            object_id=object_id
        ).order_by('-created_at')
    
    @staticmethod
    def get_statistics(organization, user=None):
        """
        Obtiene estadísticas de tareas
        
        Args:
            organization: Organización
            user: Usuario opcional para filtrar
        
        Returns:
            dict: Estadísticas de tareas
        """
        tasks = Task.objects.filter(organization=organization)
        
        if user:
            tasks = tasks.filter(assigned_to=user)
        
        total = tasks.count()
        by_status = tasks.values('status').annotate(count=Count('id'))
        by_priority = tasks.values('priority').annotate(count=Count('id'))
        
        overdue = tasks.filter(
            due_date__lt=timezone.now()
        ).exclude(status__in=['completed', 'cancelled']).count()
        
        completed_this_month = tasks.filter(
            status='completed',
            completed_at__gte=timezone.now().replace(day=1)
        ).count()
        
        avg_completion_time = tasks.filter(
            status='completed',
            completed_at__isnull=False
        ).annotate(
            completion_time=models.F('completed_at') - models.F('created_at')
        ).aggregate(
            avg_time=Avg('completion_time')
        )['avg_time']
        
        return {
            'total': total,
            'by_status': list(by_status),
            'by_priority': list(by_priority),
            'overdue': overdue,
            'completed_this_month': completed_this_month,
            'avg_completion_time': avg_completion_time,
        }


class TaskCommentService:
    """Servicio para comentarios en tareas"""
    
    @staticmethod
    def add_comment(task, user, comment, parent_comment=None, is_internal=False):
        """
        Agrega un comentario a una tarea
        
        Args:
            task: Tarea
            user: Usuario que comenta
            comment: Texto del comentario
            parent_comment: Comentario padre (para respuestas)
            is_internal: Si es comentario interno
        
        Returns:
            TaskComment: El comentario creado
        """
        task_comment = TaskComment.objects.create(
            task=task,
            organization=task.organization,
            user=user,
            comment=comment,
            parent_comment=parent_comment,
            is_internal=is_internal
        )
        
        # Registrar actividad
        TaskActivityService.log_activity(
            task=task,
            user=user,
            action='commented',
            description='Comentario agregado'
        )
        
        return task_comment
    
    @staticmethod
    def get_task_comments(task, include_internal=True):
        """
        Obtiene los comentarios de una tarea
        
        Args:
            task: Tarea
            include_internal: Incluir comentarios internos
        
        Returns:
            QuerySet: Comentarios de la tarea
        """
        comments = TaskComment.objects.filter(task=task)
        
        if not include_internal:
            comments = comments.filter(is_internal=False)
        
        return comments.order_by('created_at')


class TaskActivityService:
    """Servicio para actividades/log de tareas"""
    
    @staticmethod
    def log_activity(task, user, action, description='', old_value=None, new_value=None, ip_address=None):
        """
        Registra una actividad en una tarea
        
        Args:
            task: Tarea
            user: Usuario que realiza la acción
            action: Tipo de acción
            description: Descripción de la actividad
            old_value: Valor anterior
            new_value: Valor nuevo
            ip_address: IP del usuario
        
        Returns:
            TaskActivity: La actividad registrada
        """
        activity = TaskActivity.objects.create(
            task=task,
            organization=task.organization,
            user=user,
            action=action,
            description=description,
            old_value=old_value or {},
            new_value=new_value or {},
            ip_address=ip_address
        )
        
        return activity
    
    @staticmethod
    def get_task_history(task):
        """Obtiene el historial de actividades de una tarea"""
        return TaskActivity.objects.filter(task=task).order_by('-created_at')


class TaskChecklistService:
    """Servicio para checklists de tareas"""
    
    @staticmethod
    def create_checklist(task, created_by, title, items=None):
        """
        Crea un checklist para una tarea
        
        Args:
            task: Tarea
            created_by: Usuario creador
            title: Título del checklist
            items: Lista de items (opcional)
        
        Returns:
            TaskChecklist: El checklist creado
        """
        if items is None:
            items = []
        
        # Formato de items: [{'text': 'Item 1', 'completed': False}, ...]
        formatted_items = [
            {'text': item if isinstance(item, str) else item.get('text', ''),
             'completed': False if isinstance(item, str) else item.get('completed', False)}
            for item in items
        ]
        
        checklist = TaskChecklist.objects.create(
            task=task,
            organization=task.organization,
            created_by=created_by,
            title=title,
            items=formatted_items
        )
        
        return checklist
    
    @staticmethod
    def add_item(checklist, item_text):
        """Agrega un item al checklist"""
        items = checklist.items or []
        items.append({'text': item_text, 'completed': False})
        checklist.items = items
        checklist.save()
        return checklist
    
    @staticmethod
    def toggle_item(checklist, item_index):
        """Cambia el estado de un item"""
        items = checklist.items or []
        
        if 0 <= item_index < len(items):
            items[item_index]['completed'] = not items[item_index].get('completed', False)
            checklist.items = items
            checklist.save()
            
            # Actualizar progreso de la tarea
            TaskChecklistService.update_task_progress(checklist.task)
        
        return checklist
    
    @staticmethod
    def update_task_progress(task):
        """Actualiza el progreso de la tarea basado en checklists"""
        checklists = task.checklists.all()
        
        if not checklists:
            return
        
        total_items = 0
        completed_items = 0
        
        for checklist in checklists:
            items = checklist.items or []
            total_items += len(items)
            completed_items += sum(1 for item in items if item.get('completed', False))
        
        if total_items > 0:
            task.progress = int((completed_items / total_items) * 100)
            task.save(update_fields=['progress'])


class TaskReminderService:
    """Servicio para recordatorios de tareas"""
    
    @staticmethod
    def create_reminder(task, user, remind_at, reminder_type='email', message=''):
        """
        Crea un recordatorio para una tarea
        
        Args:
            task: Tarea
            user: Usuario a recordar
            remind_at: Fecha/hora del recordatorio
            reminder_type: Tipo de recordatorio
            message: Mensaje personalizado
        
        Returns:
            TaskReminder: El recordatorio creado
        """
        reminder = TaskReminder.objects.create(
            task=task,
            organization=task.organization,
            user=user,
            reminder_type=reminder_type,
            remind_at=remind_at,
            message=message
        )
        
        return reminder
    
    @staticmethod
    def get_pending_reminders():
        """Obtiene recordatorios pendientes de enviar"""
        return TaskReminder.objects.filter(
            is_sent=False,
            remind_at__lte=timezone.now()
        ).select_related('task', 'user', 'organization')
    
    @staticmethod
    def send_reminders():
        """
        Envía recordatorios pendientes
        
        Returns:
            int: Número de recordatorios enviados
        """
        from apps.notifications.services import NotificationService
        
        pending = TaskReminderService.get_pending_reminders()
        sent_count = 0
        
        for reminder in pending:
            try:
                # Crear notificación
                message = reminder.message or f"Recordatorio: {reminder.task.title}"
                
                NotificationService.create_notification(
                    organization=reminder.organization,
                    user=reminder.user,
                    title=f"Recordatorio de Tarea",
                    message=message,
                    notification_type='task_reminder',
                    channel=reminder.reminder_type,
                    related_object=reminder.task
                )
                
                # Marcar como enviado
                reminder.mark_as_sent()
                sent_count += 1
                
            except Exception as e:
                print(f"Error enviando recordatorio {reminder.id}: {e}")
        
        return sent_count


class TaskCategoryService:
    """Servicio para categorías de tareas"""
    
    @staticmethod
    def create_category(organization, name, slug, created_by, **kwargs):
        """Crea una categoría de tareas"""
        category = TaskCategory.objects.create(
            organization=organization,
            name=name,
            slug=slug,
            created_by=created_by,
            **kwargs
        )
        
        return category
    
    @staticmethod
    def get_categories(organization, active_only=True):
        """Obtiene categorías de una organización"""
        categories = TaskCategory.objects.filter(organization=organization)
        
        if active_only:
            categories = categories.filter(is_active=True)
        
        return categories.order_by('name')


def create_default_categories(organization, created_by):
    """
    Crea categorías predeterminadas de tareas
    
    Args:
        organization: Organización
        created_by: Usuario creador
    
    Returns:
        list: Categorías creadas
    """
    default_categories = [
        {
            'name': 'General',
            'slug': 'general',
            'description': 'Tareas generales',
            'color': '#3498db',
            'icon': 'fas fa-tasks'
        },
        {
            'name': 'Seguimiento',
            'slug': 'seguimiento',
            'description': 'Tareas de seguimiento a clientes',
            'color': '#2ecc71',
            'icon': 'fas fa-user-check'
        },
        {
            'name': 'Administrativo',
            'slug': 'administrativo',
            'description': 'Tareas administrativas',
            'color': '#e74c3c',
            'icon': 'fas fa-briefcase'
        },
        {
            'name': 'Ventas',
            'slug': 'ventas',
            'description': 'Tareas relacionadas con ventas',
            'color': '#f39c12',
            'icon': 'fas fa-chart-line'
        },
        {
            'name': 'Soporte',
            'slug': 'soporte',
            'description': 'Tareas de soporte técnico',
            'color': '#9b59b6',
            'icon': 'fas fa-headset'
        },
    ]
    
    categories = []
    for cat_data in default_categories:
        category, created = TaskCategory.objects.get_or_create(
            organization=organization,
            slug=cat_data['slug'],
            defaults={
                'name': cat_data['name'],
                'description': cat_data['description'],
                'color': cat_data['color'],
                'icon': cat_data['icon'],
                'created_by': created_by
            }
        )
        categories.append(category)
    
    return categories


# Import models for queries
from django.db import models
