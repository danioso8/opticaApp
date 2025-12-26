"""
Script para resetear las secuencias de PostgreSQL/SQLite y evitar errores de ID duplicado
"""
from django.core.management import call_command
from django.db import connection
import os
import sys

# Agregar el directorio del proyecto al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.apps import apps


def reset_sequences():
    """Resetea las secuencias de auto-incremento de todas las tablas"""
    
    # Obtener el tipo de base de datos
    db_vendor = connection.vendor
    
    if db_vendor == 'postgresql':
        print("🔧 Reseteando secuencias de PostgreSQL...")
        
        # Obtener todas las secuencias
        with connection.cursor() as cursor:
            # Obtener todas las secuencias
            cursor.execute("""
                SELECT 
                    c.relname as sequence_name,
                    t.relname as table_name,
                    a.attname as column_name
                FROM pg_class c
                JOIN pg_namespace n ON c.relnamespace = n.oid
                LEFT JOIN pg_depend d ON d.objid = c.oid
                LEFT JOIN pg_class t ON d.refobjid = t.oid
                LEFT JOIN pg_attribute a ON a.attrelid = t.oid AND a.attnum = d.refobjsubid
                WHERE c.relkind = 'S'
                AND n.nspname = 'public'
                AND t.relname IS NOT NULL
                ORDER BY c.relname;
            """)
            
            sequences = cursor.fetchall()
            count = 0
            
            for seq_name, table_name, column_name in sequences:
                try:
                    # Obtener el máximo ID actual
                    cursor.execute(f"SELECT MAX({column_name}) FROM {table_name}")
                    max_id = cursor.fetchone()[0] or 0
                    
                    # Resetear la secuencia al siguiente valor
                    next_val = max_id + 1
                    cursor.execute(f"SELECT setval('{seq_name}', {next_val}, false)")
                    print(f"  ✅ {table_name}.{column_name}: {max_id} → {next_val}")
                    count += 1
                except Exception as e:
                    print(f"  ⚠️  Error en {table_name}.{column_name}: {e}")
            
            print(f"\n  📊 Total: {count} secuencias reseteadas")
    
    elif db_vendor == 'sqlite':
        print("🔧 Reseteando secuencias de SQLite...")
        
        with connection.cursor() as cursor:
            # En SQLite, actualizar sqlite_sequence
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            count = 0
            
            for (table_name,) in tables:
                if table_name not in ['sqlite_sequence', 'django_migrations']:
                    try:
                        # Obtener el máximo ID
                        cursor.execute(f"SELECT MAX(id) FROM {table_name}")
                        max_id = cursor.fetchone()[0]
                        
                        if max_id is not None:
                            # Actualizar o insertar en sqlite_sequence
                            cursor.execute(f"""
                                INSERT OR REPLACE INTO sqlite_sequence (name, seq) 
                                VALUES ('{table_name}', {max_id})
                            """)
                            print(f"  ✅ {table_name}: secuencia reseteada a {max_id}")
                            count += 1
                    except Exception as e:
                        # La tabla puede no tener columna id
                        pass
            
            print(f"\n  📊 Total: {count} secuencias reseteadas")
    
    else:
        print(f"⚠️  Base de datos {db_vendor} no soportada para reset de secuencias")
    
    print("\n✨ Secuencias reseteadas correctamente!")


def main():
    print("=" * 60)
    print("🔧 RESETEO DE SECUENCIAS DE BASE DE DATOS")
    print("=" * 60)
    print()
    
    try:
        reset_sequences()
        print()
        print("=" * 60)
        print("✅ PROCESO COMPLETADO EXITOSAMENTE")
        print("=" * 60)
    except Exception as e:
        print()
        print("=" * 60)
        print(f"❌ ERROR: {str(e)}")
        print("=" * 60)
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
