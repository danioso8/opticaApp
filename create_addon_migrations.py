"""
Script para generar migraciones de los nuevos modelos de add-ons
Ejecutar: python create_addon_migrations.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command

print("=" * 70)
print("GENERANDO MIGRACIONES PARA NUEVOS MODELOS")
print("=" * 70)

print("\n📝 Generando migraciones para organizations...")
call_command('makemigrations', 'organizations', interactive=False)

print("\n✅ Migraciones generadas exitosamente!")
print("\n⚠️  IMPORTANTE:")
print("   1. Revisa las migraciones generadas en apps/organizations/migrations/")
print("   2. Ejecuta: python manage.py migrate")
print("=" * 70)
