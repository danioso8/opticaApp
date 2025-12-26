"""
Script para aplicar migraciones en Render
Ejecutar en Render Shell: python apply_migrations_render.py
"""

import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import execute_from_command_line

print("=" * 80)
print("APLICANDO MIGRACIONES EN RENDER")
print("=" * 80)

# Ejecutar migraciones
print("\n1️⃣  Ejecutando makemigrations...")
try:
    execute_from_command_line(['manage.py', 'makemigrations'])
    print("✅ Makemigrations completado")
except Exception as e:
    print(f"❌ Error en makemigrations: {e}")

print("\n2️⃣  Ejecutando migrate...")
try:
    execute_from_command_line(['manage.py', 'migrate'])
    print("✅ Migrate completado")
except Exception as e:
    print(f"❌ Error en migrate: {e}")

print("\n3️⃣  Verificando migraciones aplicadas...")
try:
    execute_from_command_line(['manage.py', 'showmigrations'])
    print("✅ Verificación completada")
except Exception as e:
    print(f"❌ Error en showmigrations: {e}")

print("\n" + "=" * 80)
print("PROCESO COMPLETADO")
print("=" * 80)
