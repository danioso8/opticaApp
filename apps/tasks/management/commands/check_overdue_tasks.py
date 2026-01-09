"""
Management command para detectar y notificar tareas vencidas
"""
from django.core.management.base import BaseCommand
from apps.tasks.services import TaskService
from apps.notifications.services import NotificationService


class Command(BaseCommand):
    help = 'Detecta tareas vencidas y envía notificaciones'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--organization-id',
            type=int,
            help='ID de organización específica (opcional)'
        )
    
    def handle(self, *args, **options):
        from apps.organizations.models import Organization
        
        self.stdout.write('Detectando tareas vencidas...')
        
        if options['organization_id']:
            organizations = Organization.objects.filter(id=options['organization_id'])
        else:
            organizations = Organization.objects.filter(is_active=True)
        
        total_overdue = 0
        total_notifications = 0
        
        for org in organizations:
            overdue_tasks = TaskService.get_overdue_tasks(org)
            
            for task in overdue_tasks:
                if task.assigned_to and not task.reminder_sent:
                    try:
                        NotificationService.create_notification(
                            organization=org,
                            user=task.assigned_to,
                            title=f"Tarea Vencida: {task.title}",
                            message=f"La tarea '{task.title}' está vencida desde {task.due_date.strftime('%d/%m/%Y')}",
                            notification_type='task_overdue',
                            channel='email',
                            priority='high',
                            related_object=task
                        )
                        
                        task.reminder_sent = True
                        task.save(update_fields=['reminder_sent'])
                        
                        total_notifications += 1
                    
                    except Exception as e:
                        self.stdout.write(
                            self.style.ERROR(f'Error notificando tarea {task.id}: {e}')
                        )
            
            total_overdue += overdue_tasks.count()
        
        self.stdout.write(
            self.style.SUCCESS(
                f'✓ {total_overdue} tareas vencidas detectadas, '
                f'{total_notifications} notificaciones enviadas'
            )
        )
