"""
Script para aplicar fake de la migración problemática en Render
Ejecutar en Shell de Render: python fake_migration_render.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command

print("=== Aplicando fake de migración 0009 ===")
print("Esta migración ya tiene el constraint creado en la BD")
print()

try:
    # Marcar como aplicada sin ejecutarla
    call_command('migrate', 'appointments', '0009', fake=True, verbosity=2)
    print("\n✓ Migración marcada como aplicada exitosamente")
    print("\nAhora el deploy debería funcionar correctamente")
except Exception as e:
    print(f"\n✗ Error: {e}")
    print("\nSi esto falla, ejecuta manualmente en el shell:")
    print("python manage.py migrate appointments 0009 --fake")
