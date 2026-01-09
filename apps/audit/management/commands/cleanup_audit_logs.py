"""
Management command para limpiar logs antiguos de auditoría.
Uso: python manage.py cleanup_audit_logs [--days=365]
"""
from django.core.management.base import BaseCommand
from apps.audit.services import AuditService


class Command(BaseCommand):
    help = 'Elimina registros de auditoría antiguos según políticas de retención'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=None,
            help='Días de retención (usa config por defecto si no se especifica)'
        )
    
    def handle(self, *args, **options):
        days = options.get('days')
        
        self.stdout.write('Iniciando limpieza de logs de auditoría...')
        
        result = AuditService.cleanup_old_logs(days=days)
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\nLimpieza completada:"
                f"\n- Logs eliminados: {result['deleted']}"
                f"\n- Duración: {result['duration']:.2f} segundos"
            )
        )
        
        if result['details']:
            self.stdout.write("\nDetalles por modelo:")
            for model, info in result['details'].items():
                self.stdout.write(f"  - {model}: {info['deleted']} logs")
