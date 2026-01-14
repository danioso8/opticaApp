#!/usr/bin/env python
"""
Script para verificar y aplicar migración de incluir_en_nomina.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

print("\n🔍 Verificando campo 'incluir_en_nomina' en tabla dashboard_employee...\n")

with connection.cursor() as cursor:
    cursor.execute("""
        SELECT column_name, data_type, is_nullable
        FROM information_schema.columns
        WHERE table_name = 'dashboard_employee'
        AND column_name LIKE '%nomina%'
    """)
    
    columns = cursor.fetchall()
    
    if columns:
        print("✅ Columnas encontradas:")
        for col in columns:
            print(f"   - {col[0]} ({col[1]}) - Nullable: {col[2]}")
    else:
        print("❌ No se encontró la columna 'incluir_en_nomina'")
        print("\n🔧 Aplicando migración...")
        
        # Aplicar migración
        import subprocess
        result = subprocess.run(
            ['python', 'manage.py', 'migrate', 'dashboard'],
            capture_output=True,
            text=True
        )
        
        print(result.stdout)
        if result.returncode == 0:
            print("✅ Migración aplicada exitosamente")
        else:
            print(f"❌ Error: {result.stderr}")

print("\n")
