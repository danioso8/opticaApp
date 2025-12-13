"""
Script para eliminar y recrear el registro de migración 0011
Ejecutar en Render: python fix_migration_0011_render.py
"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db.migrations.recorder import MigrationRecorder
from django.db import connection

recorder = MigrationRecorder(connection)

# Eliminar el registro de la migración 0011
deleted = recorder.migration_qs.filter(
    app='appointments', 
    name='0011_appointment_companion_name_and_more'
).delete()

print(f"✅ Registro de migración 0011 eliminado: {deleted[0]} filas")
print("\nAhora ejecuta:")
print("  python manage.py migrate appointments 0011 --fake")
print("  python manage.py migrate")
