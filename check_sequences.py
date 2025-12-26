"""
Script para verificar el estado de las secuencias vs los IDs actuales
Útil para diagnosticar problemas de "duplicate key"
"""
import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection


def check_sequences():
    """Verifica el estado de todas las secuencias"""
    
    db_vendor = connection.vendor
    
    print("\n" + "=" * 80)
    print("📊 VERIFICACIÓN DE SECUENCIAS DE BASE DE DATOS")
    print("=" * 80)
    print(f"Base de datos: {db_vendor.upper()}\n")
    
    issues_found = []
    
    with connection.cursor() as cursor:
        if db_vendor == 'postgresql':
            # Obtener todas las secuencias
            cursor.execute("""
                SELECT 
                    c.relname as sequence_name,
                    n.nspname as schema_name,
                    t.relname as table_name
                FROM pg_class c
                JOIN pg_namespace n ON c.relnamespace = n.oid
                LEFT JOIN pg_depend d ON d.objid = c.oid
                LEFT JOIN pg_class t ON d.refobjid = t.oid
                WHERE c.relkind = 'S'
                AND n.nspname = 'public'
                ORDER BY c.relname;
            """)
            
            sequences = cursor.fetchall()
            
            print(f"{'Tabla':<40} {'Max ID':<12} {'Seq Actual':<12} {'Estado':<15}")
            print("-" * 80)
            
            for seq_name, schema, table_name in sequences:
                if table_name and '_id_seq' in seq_name:
                    # Obtener el máximo ID de la tabla
                    try:
                        cursor.execute(f"SELECT MAX(id) FROM {table_name}")
                        max_id = cursor.fetchone()[0] or 0
                    except:
                        max_id = 0
                    
                    # Obtener el valor actual de la secuencia
                    cursor.execute(f"SELECT last_value FROM {seq_name}")
                    seq_value = cursor.fetchone()[0]
                    
                    # Determinar estado
                    if seq_value <= max_id:
                        status = "⚠️  PROBLEMA"
                        issues_found.append((table_name, max_id, seq_value))
                    else:
                        status = "✅ OK"
                    
                    print(f"{table_name:<40} {max_id:<12} {seq_value:<12} {status:<15}")
        
        elif db_vendor == 'sqlite':
            # En SQLite, revisar sqlite_sequence
            cursor.execute("SELECT name, seq FROM sqlite_sequence ORDER BY name")
            sequences = cursor.fetchall()
            
            print(f"{'Tabla':<40} {'Max ID':<12} {'Seq Actual':<12} {'Estado':<15}")
            print("-" * 80)
            
            for table_name, seq_value in sequences:
                # Obtener el máximo ID de la tabla
                try:
                    cursor.execute(f"SELECT MAX(id) FROM {table_name}")
                    max_id = cursor.fetchone()[0] or 0
                except:
                    max_id = 0
                
                # Determinar estado
                if seq_value < max_id:
                    status = "⚠️  PROBLEMA"
                    issues_found.append((table_name, max_id, seq_value))
                else:
                    status = "✅ OK"
                
                print(f"{table_name:<40} {max_id:<12} {seq_value or 0:<12} {status:<15}")
    
    print("\n" + "=" * 80)
    
    if issues_found:
        print("⚠️  PROBLEMAS ENCONTRADOS:")
        print("=" * 80)
        for table, max_id, seq_val in issues_found:
            print(f"\n❌ {table}:")
            print(f"   Max ID en tabla: {max_id}")
            print(f"   Secuencia actual: {seq_val}")
            print(f"   ⚠️  La secuencia está DETRÁS del máximo ID")
            print(f"   🔧 Ejecuta: python fix_sequences.py")
    else:
        print("✅ TODAS LAS SECUENCIAS ESTÁN CORRECTAS")
        print("=" * 80)
        print("No se encontraron problemas. El sistema debería funcionar correctamente.")
    
    print("\n")


if __name__ == '__main__':
    check_sequences()
