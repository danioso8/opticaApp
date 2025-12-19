"""
Script para restaurar el backup migration_data.json a Render
Ejecutar desde el Shell de Render
"""
import os
import json
from django.core.management import call_command

def restore_backup():
    backup_file = 'migration_data.json'
    
    if not os.path.exists(backup_file):
        print(f"❌ Archivo {backup_file} no encontrado")
        return
    
    print("=" * 70)
    print("RESTAURANDO DATOS A RENDER")
    print("=" * 70)
    
    # Verificar que el archivo es JSON válido
    try:
        with open(backup_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"✓ Archivo válido con {len(data)} registros")
    except json.JSONDecodeError as e:
        print(f"❌ Error al leer JSON: {e}")
        return
    
    # Importar datos
    print("\nImportando datos...")
    try:
        call_command('loaddata', backup_file, verbosity=2)
        print("\n✅ Datos restaurados exitosamente")
    except Exception as e:
        print(f"\n❌ Error al importar: {e}")
        print("\nIntenta ejecutar:")
        print(f"  python manage.py loaddata {backup_file}")

if __name__ == '__main__':
    restore_backup()
