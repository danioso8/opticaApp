"""
Comando para ejecutar auto-corrección de errores
Uso: python manage.py auto_fix_errors
"""
from django.core.management.base import BaseCommand
from apps.audit.error_auto_fix import auto_fix_errors
import logging


logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Auto-corrige errores comunes del sistema'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Simula correcciones sin aplicarlas',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        
        if dry_run:
            self.stdout.write(self.style.WARNING('🔍 Modo DRY-RUN - No se aplicarán correcciones'))
        
        self.stdout.write(self.style.SUCCESS('🤖 Iniciando auto-corrección de errores...'))
        
        try:
            report = auto_fix_errors()
            
            self.stdout.write(self.style.SUCCESS(f'\n✅ Proceso completado:'))
            self.stdout.write(f'  • Correcciones aplicadas: {report["fixes_applied"]}')
            self.stdout.write(f'  • Correcciones fallidas: {report["fixes_failed"]}')
            
            if report['details']['applied']:
                self.stdout.write(self.style.SUCCESS('\n📝 Correcciones exitosas:'))
                for fix in report['details']['applied']:
                    self.stdout.write(f'  • Error #{fix["error_id"]}: {fix["error_type"]} - {fix["fix_method"]}')
            
            if report['details']['failed']:
                self.stdout.write(self.style.WARNING('\n⚠️ Correcciones fallidas:'))
                for fail in report['details']['failed']:
                    self.stdout.write(f'  • Error #{fail["error_id"]}: {fail["error_type"]} - {fail["reason"]}')
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f'\n❌ Error durante auto-corrección: {str(e)}'))
            logger.exception('Error en auto-corrección')
