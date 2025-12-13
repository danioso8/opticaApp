"""
Script para ejecutar ANTES de las migraciones en Render
Detecta automáticamente columnas/constraints existentes y marca migraciones como fake

USAR EN build.sh ANTES DE python manage.py migrate:
python pre_migrate_check.py
"""

from django.core.management import setup_environ
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opticaapp.settings')
django.setup()

from django.db import connection
from django.db.migrations.recorder import MigrationRecorder

def column_exists(table_name, column_name):
    """Verifica si una columna existe en una tabla"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name=%s AND column_name=%s
        """, [table_name, column_name])
        return cursor.fetchone() is not None

def constraint_exists(constraint_name):
    """Verifica si un constraint existe"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT conname 
            FROM pg_constraint 
            WHERE conname = %s
        """, [constraint_name])
        return cursor.fetchone() is not None

def migration_is_applied(app_label, migration_name):
    """Verifica si una migración está registrada"""
    recorder = MigrationRecorder(connection)
    return recorder.migration_qs.filter(
        app=app_label,
        name=migration_name
    ).exists()

def fake_migration(app_label, migration_name):
    """Marca una migración como aplicada sin ejecutarla"""
    recorder = MigrationRecorder(connection)
    recorder.record_applied(app_label, migration_name)
    print(f"✅ Migración {app_label}.{migration_name} marcada como FAKE")

def main():
    print("=" * 70)
    print("🔍 Verificando estado de migraciones...")
    print("=" * 70)
    
    checks_passed = True
    
    # CHECK 1: Migración 0011 de appointments (columnas companion)
    migration_0011 = '0011_appointment_companion_name_and_more'
    if not migration_is_applied('appointments', migration_0011):
        if column_exists('appointments_appointment', 'companion_name'):
            print(f"\n⚠️  Columnas companion_* existen pero migración {migration_0011} NO registrada")
            fake_migration('appointments', migration_0011)
        else:
            print(f"\n✅ Migración {migration_0011}: Las columnas NO existen, migración se ejecutará normalmente")
    else:
        print(f"\n✅ Migración {migration_0011} ya está aplicada")
    
    # CHECK 2: Migración 0012 de appointments (constraint unique)
    migration_0012 = '0012_appointment_unique_active_appointment_slot'
    if not migration_is_applied('appointments', migration_0012):
        if constraint_exists('unique_active_appointment_slot'):
            print(f"\n⚠️  Constraint existe pero migración {migration_0012} NO registrada")
            fake_migration('appointments', migration_0012)
        else:
            print(f"\n✅ Migración {migration_0012}: El constraint NO existe, migración se ejecutará normalmente")
    else:
        print(f"\n✅ Migración {migration_0012} ya está aplicada")
    
    print("\n" + "=" * 70)
    print("✅ Verificación completada. Ahora puedes ejecutar: python manage.py migrate")
    print("=" * 70)
    
    return 0

if __name__ == '__main__':
    try:
        sys.exit(main())
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
