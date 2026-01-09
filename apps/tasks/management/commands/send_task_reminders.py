"""
Management command para enviar recordatorios de tareas
"""
from django.core.management.base import BaseCommand
from apps.tasks.services import TaskReminderService


class Command(BaseCommand):
    help = 'Envía recordatorios pendientes de tareas'
    
    def handle(self, *args, **options):
        self.stdout.write('Enviando recordatorios de tareas...')
        
        sent_count = TaskReminderService.send_reminders()
        
        if sent_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'✓ {sent_count} recordatorios enviados')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('✓ No hay recordatorios pendientes')
            )
