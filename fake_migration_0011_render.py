"""
Script para marcar como aplicada la migración 0011 de appointments en Render
ya que las columnas companion_* ya existen en la base de datos

EJECUTAR EN RENDER SHELL:
python manage.py shell < fake_migration_0011_render.py

O copiar y pegar este código en Render Shell
"""

from django.db import connection
from django.db.migrations.recorder import MigrationRecorder

# Verificar si las columnas existen
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='appointments_appointment' 
        AND column_name IN ('companion_name', 'companion_phone', 'companion_relationship', 'has_companion')
        ORDER BY column_name;
    """)
    existing_columns = [row[0] for row in cursor.fetchall()]
    print(f"Columnas existentes: {existing_columns}")

# Verificar si la migración ya está registrada
recorder = MigrationRecorder(connection)
migration_exists = recorder.migration_qs.filter(
    app='appointments',
    name='0011_appointment_companion_name_and_more'
).exists()

print(f"\nMigración 0011 registrada en django_migrations: {migration_exists}")

if existing_columns and not migration_exists:
    print("\n✅ Las columnas existen pero la migración NO está registrada.")
    print("Marcando migración como aplicada...")
    
    # Marcar la migración como aplicada sin ejecutarla
    recorder.record_applied('appointments', '0011_appointment_companion_name_and_more')
    
    print("✅ Migración 0011 marcada como aplicada exitosamente")
    print("\nAhora ejecuta: python manage.py migrate")
    
elif existing_columns and migration_exists:
    print("\n✅ Todo correcto: Las columnas existen Y la migración está registrada")
    
else:
    print("\n⚠️ Situación inesperada - revisar manualmente")
