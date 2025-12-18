"""
Script para hacer backup de la base de datos PostgreSQL de Render
"""
import os
from datetime import datetime

# Este script generará el comando para hacer backup
# Necesitarás las credenciales de tu BD actual de Render

def generate_backup_command():
    """
    Genera el comando pg_dump para hacer backup de la base de datos
    """
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    backup_file = f'optica_backup_{timestamp}.sql'
    
    print("=" * 70)
    print("INSTRUCCIONES PARA HACER BACKUP DE LA BASE DE DATOS")
    print("=" * 70)
    print()
    print("1. Ve a tu Dashboard de Render: https://dashboard.render.com/")
    print("2. Selecciona tu base de datos PostgreSQL actual")
    print("3. En la pestaña 'Info', copia la 'External Database URL'")
    print()
    print("4. La URL tiene este formato:")
    print("   postgresql://user:password@host:port/database")
    print()
    print("5. Ejecuta este comando en tu terminal (reemplaza la URL):")
    print()
    print(f"   pg_dump 'postgresql://TU_URL_AQUI' > {backup_file}")
    print()
    print("   O si no tienes pg_dump instalado localmente, usa Render Shell:")
    print()
    print("   a) En el Dashboard de Render, ve a tu Web Service")
    print("   b) Click en 'Shell' en el menú izquierdo")
    print("   c) Ejecuta:")
    print(f"      pg_dump $DATABASE_URL > backup.sql")
    print(f"      cat backup.sql")
    print("   d) Copia todo el contenido y guárdalo localmente")
    print()
    print("6. El archivo de backup se guardará como:", backup_file)
    print()
    print("=" * 70)
    print("ALTERNATIVA: Usar Render Dashboard")
    print("=" * 70)
    print()
    print("Render también permite hacer backups desde el dashboard:")
    print("1. Ve a tu PostgreSQL database en Render")
    print("2. Click en la pestaña 'Backups'")
    print("3. Render hace backups automáticos diarios (según tu plan)")
    print("4. Puedes descargar un backup desde ahí")
    print()
    print("=" * 70)
    print()

if __name__ == '__main__':
    generate_backup_command()
