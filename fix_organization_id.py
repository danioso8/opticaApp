"""
Script específico para resetear la secuencia de Organizations
Ejecutar si aparece el error: duplicate key value violates unique constraint "organizations_organization_pkey"
"""
import os
import sys
import django

# Setup Django
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection


def fix_organization_sequence():
    """Resetea la secuencia de ID de la tabla organizations_organization"""
    
    db_vendor = connection.vendor
    
    print("=" * 70)
    print("🔧 RESETEO DE SECUENCIA: organizations_organization")
    print("=" * 70)
    print()
    
    with connection.cursor() as cursor:
        if db_vendor == 'postgresql':
            print("📊 Base de datos: PostgreSQL")
            
            # Obtener el máximo ID actual
            cursor.execute("SELECT MAX(id) FROM organizations_organization")
            max_id = cursor.fetchone()[0]
            
            if max_id is None:
                max_id = 0
                print(f"  ℹ️  No hay registros en la tabla")
            else:
                print(f"  ℹ️  Máximo ID actual: {max_id}")
            
            # Resetear la secuencia
            next_id = max_id + 1
            cursor.execute(f"SELECT setval('organizations_organization_id_seq', {next_id}, false)")
            
            print(f"  ✅ Secuencia reseteada al siguiente valor: {next_id}")
            
            # Verificar
            cursor.execute("SELECT last_value FROM organizations_organization_id_seq")
            current_seq = cursor.fetchone()[0]
            print(f"  ✅ Valor actual de la secuencia: {current_seq}")
            
        elif db_vendor == 'sqlite':
            print("📊 Base de datos: SQLite")
            
            # Obtener el máximo ID actual
            cursor.execute("SELECT MAX(id) FROM organizations_organization")
            max_id = cursor.fetchone()[0]
            
            if max_id is None:
                max_id = 0
                print(f"  ℹ️  No hay registros en la tabla")
            else:
                print(f"  ℹ️  Máximo ID actual: {max_id}")
            
            # Actualizar sqlite_sequence
            cursor.execute("""
                INSERT OR REPLACE INTO sqlite_sequence (name, seq) 
                VALUES ('organizations_organization', ?)
            """, [max_id])
            
            print(f"  ✅ Secuencia actualizada a: {max_id}")
        
        else:
            print(f"  ⚠️  Base de datos {db_vendor} no soportada")
            return
    
    print()
    print("=" * 70)
    print("✅ PROCESO COMPLETADO")
    print("=" * 70)
    print()
    print("💡 Ahora puedes crear organizaciones sin error de ID duplicado")


if __name__ == '__main__':
    fix_organization_sequence()
