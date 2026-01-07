#!/bin/bash
# Script para descargar backups del servidor a tu PC local
# Ejecutar en tu PC local con: ./descargar_backups.sh

SERVER="root@84.247.129.180"
REMOTE_DIR="/var/www/opticaapp/backups"
LOCAL_DIR="d:/ESCRITORIO/OpticaApp/backups_servidor"
DATE=$(date +%Y%m%d)

mkdir -p "$LOCAL_DIR"

echo "Descargando backups del servidor..."

# Descargar el backup más reciente
scp $SERVER:$REMOTE_DIR/backup_latest.json "$LOCAL_DIR/backup_$DATE.json"

# Verificar que tiene usuarios
python << EOF
import json
import sys

try:
    with open('$LOCAL_DIR/backup_$DATE.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    users = [x for x in data if x.get('model') == 'auth.user']
    print(f"\n✅ Backup descargado correctamente")
    print(f"   Usuarios: {len(users)}")
    print(f"   Archivo: $LOCAL_DIR/backup_$DATE.json")
    
    if len(users) == 0:
        print("\n❌ ADVERTENCIA: Este backup NO tiene usuarios")
        sys.exit(1)
        
except Exception as e:
    print(f"\n❌ ERROR: {e}")
    sys.exit(1)
EOF

if [ $? -eq 0 ]; then
    echo "\n✅ Backup seguro descargado"
else
    echo "\n❌ Backup tiene problemas - revisar"
fi
