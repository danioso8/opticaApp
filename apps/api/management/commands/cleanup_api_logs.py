"""
Management command para limpiar logs antiguos de API
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.api.models import APILog


class Command(BaseCommand):
    help = 'Elimina logs de API antiguos'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            type=int,
            default=30,
            help='Días de antigüedad para eliminar (default: 30)'
        )
    
    def handle(self, *args, **options):
        days = options['days']
        cutoff_date = timezone.now() - timedelta(days=days)
        
        self.stdout.write(f'Eliminando logs de API anteriores a {cutoff_date}...')
        
        deleted, details = APILog.objects.filter(
            created_at__lt=cutoff_date
        ).delete()
        
        self.stdout.write(
            self.style.SUCCESS(f'✓ {deleted} logs eliminados')
        )
        
        if details:
            for model, count in details.items():
                if count > 0:
                    self.stdout.write(f'  - {model}: {count}')
