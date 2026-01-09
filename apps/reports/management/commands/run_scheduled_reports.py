"""
Management command para ejecutar reportes programados.
Uso: python manage.py run_scheduled_reports
"""
from django.core.management.base import BaseCommand
from apps.reports.services import ScheduledReportService


class Command(BaseCommand):
    help = 'Ejecuta reportes programados pendientes'
    
    def handle(self, *args, **options):
        self.stdout.write('Ejecutando reportes programados...')
        
        result = ScheduledReportService.execute_scheduled_reports()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\nEjecución completada:"
                f"\n- Ejecutados: {result['executed']}"
                f"\n- Fallidos: {result['failed']}"
                f"\n- Total: {result['total']}"
            )
        )
