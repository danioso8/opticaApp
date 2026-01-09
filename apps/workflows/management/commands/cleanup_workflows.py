"""
Management command para limpiar workflows completados antiguos
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.workflows.models import WorkflowInstance


class Command(BaseCommand):
    help = 'Limpia workflows completados antiguos (>90 días)'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=90,
            help='Días de antigüedad para eliminar (default: 90)'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(f'Limpiando workflows completados antes de {cutoff_date}...')
        
        # Eliminar workflows completados antiguos
        old_workflows = WorkflowInstance.objects.filter(
            status='completed',
            completed_at__lt=cutoff_date
        )
        
        count = old_workflows.count()
        old_workflows.delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ {count} workflows eliminados')
        )
