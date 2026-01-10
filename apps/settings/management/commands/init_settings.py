"""
Management command para inicializar configuraciones por defecto.
Uso: python manage.py init_settings
"""
from django.core.management.base import BaseCommand
from apps.settings.services import create_default_settings, create_default_categories


class Command(BaseCommand):
    help = 'Inicializa configuraciones y categorías por defecto del sistema'
    
    def handle(self, *args, **options):
        self.stdout.write('Inicializando configuraciones por defecto...')
        
        # Crear configuraciones
        settings_count = create_default_settings()
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ {settings_count} configuraciones creadas"
            )
        )
        
        # Crear categorías
        categories_count = create_default_categories()
        self.stdout.write(
            self.style.SUCCESS(
                f"✓ {categories_count} categorías creadas"
            )
        )
        
        self.stdout.write(
            self.style.SUCCESS(
                '\n✓ Inicialización completada exitosamente'
            )
        )
