#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

with connection.cursor() as cursor:
    # PostgreSQL: verificar tipo de campo
    cursor.execute("""
        SELECT column_name, data_type, character_maximum_length
        FROM information_schema.columns 
        WHERE table_name = 'patients_clinicalhistory' 
        AND column_name LIKE '%sphere%'
    """)
    
    print("=" * 70)
    print("Verificando campos 'sphere' en patients_clinicalhistory (PostgreSQL):")
    print("=" * 70)
    
    rows = cursor.fetchall()
    for row in rows:
        col_name, data_type, max_length = row
        print(f"  • {col_name}: {data_type}", end="")
        if max_length:
            print(f"({max_length})")
        else:
            print()
    
    print("=" * 70)
    
    # Verificar si hay datos
    cursor.execute("""
        SELECT id, refraction_od_sphere, refraction_os_sphere 
        FROM patients_clinicalhistory 
        WHERE refraction_od_sphere IS NOT NULL 
        OR refraction_os_sphere IS NOT NULL 
        LIMIT 5
    """)
    
    print("\nDatos existentes (primeros 5):")
    data_rows = cursor.fetchall()
    if data_rows:
        for row in data_rows:
            print(f"  ID {row[0]}: OD={row[1]}, OS={row[2]}")
    else:
        print("  No hay datos")
    
    print("=" * 70)
