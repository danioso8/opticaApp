"""
Management command para verificar y expirar API Keys vencidas
"""
from django.core.management.base import BaseCommand
from django.utils import timezone
from apps.api.models import APIKey


class Command(BaseCommand):
    help = 'Marca como expiradas las API Keys vencidas'
    
    def handle(self, *args, **options):
        now = timezone.now()
        
        self.stdout.write('Verificando API Keys expiradas...')
        
        expired_keys = APIKey.objects.filter(
            expires_at__lt=now,
            status='active'
        )
        
        count = expired_keys.count()
        
        if count > 0:
            expired_keys.update(status='expired')
            
            self.stdout.write(
                self.style.SUCCESS(f'✓ {count} API Keys marcadas como expiradas')
            )
            
            for key in expired_keys:
                self.stdout.write(f'  - {key.name} ({key.key_prefix}...)')
        else:
            self.stdout.write(
                self.style.SUCCESS('✓ No hay API Keys expiradas')
            )
