#!/usr/bin/env python
"""
Script para corregir migraciones problemáticas en Render
Ejecutar en el shell de Render cuando haya conflictos de migraciones
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def check_column_exists(table, column):
    """Verifica si una columna existe en una tabla"""
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name=%s AND column_name=%s
        """, [table, column])
        return cursor.fetchone() is not None

def main():
    print("=" * 70)
    print("🔧 Verificando estado de migraciones en Render")
    print("=" * 70)
    
    # Verificar columnas de acompañante
    companion_fields = ['companion_name', 'companion_relationship', 'companion_phone']
    table = 'appointments_appointment'
    
    print(f"\n📋 Verificando tabla: {table}")
    for field in companion_fields:
        exists = check_column_exists(table, field)
        status = "✅ EXISTE" if exists else "❌ NO EXISTE"
        print(f"  - {field}: {status}")
    
    # Verificar migraciones aplicadas
    print("\n📊 Estado de migraciones de appointments:")
    call_command('showmigrations', 'appointments')
    
    # Si las columnas existen pero la migración 0011 no está marcada como aplicada
    if all(check_column_exists(table, field) for field in companion_fields):
        print("\n✅ Todas las columnas existen en la base de datos")
        print("💡 Si la migración 0011 no está marcada, ejecuta:")
        print("   python manage.py migrate appointments 0011 --fake")
    else:
        print("\n⚠️ Algunas columnas no existen")
        print("💡 Ejecuta las migraciones normalmente:")
        print("   python manage.py migrate")
    
    print("\n" + "=" * 70)
    print("✅ Verificación completada")
    print("=" * 70)

if __name__ == '__main__':
    main()
