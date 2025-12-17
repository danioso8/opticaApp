#!/usr/bin/env python
"""
Script para marcar migraciones como fake en Render y aplicar la migración de sphere
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optica.settings')
django.setup()

from django.core.management import call_command
from django.db import connection

def main():
    print("=" * 70)
    print("🔧 Reparando migraciones en Render")
    print("=" * 70)
    
    # 1. Verificar si la constraint ya existe
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT constraint_name 
            FROM information_schema.table_constraints 
            WHERE constraint_name = 'unique_active_appointment_slot'
            AND table_name = 'appointments_appointment';
        """)
        constraint_exists = cursor.fetchone()
        
        if constraint_exists:
            print("✅ Constraint unique_active_appointment_slot ya existe")
            print("   Marcando migración 0012 como fake...")
            try:
                call_command('migrate', 'appointments', '0012', fake=True)
                print("   ✓ Migración 0012 marcada como fake")
            except Exception as e:
                print(f"   ⚠️ Ya estaba marcada: {e}")
        else:
            print("❌ Constraint no existe, aplicando migración normal")
            call_command('migrate', 'appointments', '0012')
    
    # 2. Verificar el tipo de campo refraction_od_sphere
    with connection.cursor() as cursor:
        cursor.execute("""
            SELECT data_type 
            FROM information_schema.columns 
            WHERE table_name = 'patients_clinicalhistory' 
            AND column_name = 'refraction_od_sphere';
        """)
        result = cursor.fetchone()
        
        if result:
            field_type = result[0]
            print(f"\n📊 Campo refraction_od_sphere actual: {field_type}")
            
            if field_type == 'character varying':
                print("✅ Campo ya es VARCHAR (CharField)")
                print("   Marcando migración 0018 como fake...")
                try:
                    call_command('migrate', 'patients', '0018', fake=True)
                    print("   ✓ Migración 0018 marcada como fake")
                except Exception as e:
                    print(f"   ⚠️ Ya estaba marcada: {e}")
            elif field_type == 'numeric':
                print("❌ Campo es NUMERIC, necesita conversión")
                print("   Aplicando migración 0018...")
                call_command('migrate', 'patients', '0018')
                print("   ✓ Migración 0018 aplicada")
            else:
                print(f"⚠️ Tipo inesperado: {field_type}")
        else:
            print("❌ Campo refraction_od_sphere no encontrado")
    
    # 3. Aplicar todas las migraciones pendientes
    print("\n🔄 Aplicando migraciones restantes...")
    try:
        call_command('migrate')
        print("✅ Todas las migraciones aplicadas correctamente")
    except Exception as e:
        print(f"⚠️ Error al aplicar migraciones: {e}")
    
    print("\n" + "=" * 70)
    print("✅ Proceso completado")
    print("=" * 70)

if __name__ == '__main__':
    main()
