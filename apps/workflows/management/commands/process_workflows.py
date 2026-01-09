"""
Management command para procesar workflows pendientes
"""
from django.core.management.base import BaseCommand
from apps.workflows.models import WorkflowInstance


class Command(BaseCommand):
    help = 'Procesa workflows en estados pendientes'
    
    def handle(self, *args, **options):
        self.stdout.write('Procesando workflows pendientes...')
        
        # Obtener instancias activas
        active_instances = WorkflowInstance.objects.filter(
            status='active'
        ).count()
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ {active_instances} workflows activos encontrados')
        )
