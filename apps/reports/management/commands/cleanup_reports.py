"""
Management command para limpiar reportes expirados.
Uso: python manage.py cleanup_reports
"""
from django.core.management.base import BaseCommand
from apps.reports.services import ReportService


class Command(BaseCommand):
    help = 'Elimina reportes expirados del sistema'
    
    def handle(self, *args, **options):
        self.stdout.write('Limpiando reportes expirados...')
        
        count = ReportService.cleanup_expired_reports()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ {count} reportes eliminados"
            )
        )
