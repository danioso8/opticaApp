"""
Script para ejecutar en Render Shell para solucionar el problema de migración
Ejecuta: python fix_render_migration.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

print("=== Solucionando problema de migración en Render ===\n")

# Opción 1: Desactivar temporalmente los triggers
print("Opción 1: Ejecutar migración con --fake si ya está aplicada en la BD")
print("Comando: python manage.py migrate patients 0015 --fake\n")

# Opción 2: Verificar estado de migraciones
print("Opción 2: Verificar migraciones aplicadas")
print("Comando: python manage.py showmigrations patients\n")

# Opción 3: Aplicar manualmente
print("Opción 3: Si la tabla ya tiene los cambios, marcar como aplicada:")
print("Comando: python manage.py migrate patients 0015 --fake\n")

# Verificar la estructura actual de la tabla
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'patients_clinicalhistory'
        ORDER BY ordinal_position;
    """)
    
    print("Columnas actuales en patients_clinicalhistory:")
    for row in cursor.fetchall():
        print(f"  - {row[0]}: {row[1]} {'NULL' if row[3] == 'YES' else 'NOT NULL'}")

print("\n=== INSTRUCCIONES ===")
print("1. En Render Shell, ejecuta: python manage.py showmigrations patients")
print("2. Si la migración 0015 no está marcada con [X], prueba:")
print("   python manage.py migrate patients 0015 --fake")
print("3. Si el problema persiste, ejecuta:")
print("   python manage.py migrate --run-syncdb")
