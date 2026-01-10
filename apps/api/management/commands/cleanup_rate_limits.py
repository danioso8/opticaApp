"""
Management command para limpiar registros de rate limiting antiguos
"""
from django.core.management.base import BaseCommand
from apps.api.services import RateLimitService


class Command(BaseCommand):
    help = 'Elimina registros de rate limiting antiguos'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=7,
            help='Días de antigüedad para eliminar (default: 7)'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        
        self.stdout.write(f'Limpiando registros de rate limiting de más de {days} días...')
        
        deleted = RateLimitService.cleanup_old_records(days=days)
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ {deleted} registros eliminados')
        )
