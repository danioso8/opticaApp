"""
Management command para limpiar shares expirados.
Uso: python manage.py cleanup_document_shares
"""
from django.core.management.base import BaseCommand
from apps.documents.services import DocumentService


class Command(BaseCommand):
    help = 'Elimina enlaces compartidos de documentos expirados'
    
    def handle(self, *args, **options):
        self.stdout.write('Limpiando shares expirados...')
        
        count = DocumentService.cleanup_expired_shares()
        
        self.stdout.write(
            self.style.SUCCESS(
                f"\n✓ {count} shares eliminados"
            )
        )
