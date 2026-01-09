"""
Signals para tareas
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from apps.tasks.models import Task, TaskComment
from apps.tasks.services import TaskActivityService


@receiver(pre_save, sender=Task)
def task_pre_save(sender, instance, **kwargs):
    """Signal antes de guardar una tarea"""
    # Si la tarea ya existe, verificar cambios
    if instance.pk:
        try:
            old_task = Task.objects.get(pk=instance.pk)
            
            # Auto-completar cuando el progreso llega a 100
            if instance.progress == 100 and instance.status != 'completed':
                instance.status = 'completed'
                if not instance.completed_at:
                    from django.utils import timezone
                    instance.completed_at = timezone.now()
        
        except Task.DoesNotExist:
            pass


@receiver(post_save, sender=TaskComment)
def task_comment_post_save(sender, instance, created, **kwargs):
    """Signal después de crear un comentario"""
    if created:
        # Notificar al asignado si no es quien comenta
        if instance.task.assigned_to and instance.task.assigned_to != instance.user:
            try:
                from apps.notifications.services import NotificationService
                
                NotificationService.create_notification(
                    organization=instance.organization,
                    user=instance.task.assigned_to,
                    title=f"Nuevo comentario en: {instance.task.title}",
                    message=instance.comment[:200],
                    notification_type='task_comment',
                    channel='app',
                    related_object=instance.task
                )
            except Exception as e:
                print(f"Error enviando notificación de comentario: {e}")
