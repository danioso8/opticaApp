#!/bin/bash
# Sistema de Backup Automático para OpticaApp
# Se ejecuta diariamente y verifica que los backups sean válidos

BACKUP_DIR="/var/www/opticaapp/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="$BACKUP_DIR/backup_$DATE.json"
LATEST_LINK="$BACKUP_DIR/backup_latest.json"
LOG_FILE="$BACKUP_DIR/backup.log"

# Crear directorio si no existe
mkdir -p $BACKUP_DIR

cd /var/www/opticaapp
source venv/bin/activate

echo "==========================================" >> $LOG_FILE
echo "Backup iniciado: $(date)" >> $LOG_FILE
echo "==========================================" >> $LOG_FILE

# Hacer backup
python manage.py dumpdata --indent 2 --exclude contenttypes --exclude auth.permission > $BACKUP_FILE 2>> $LOG_FILE

# Verificar que el backup tiene datos críticos
VERIFICATION=$(python << EOF
import json
import sys

try:
    with open('$BACKUP_FILE', 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    users = [x for x in data if x.get('model') == 'auth.user']
    orgs = [x for x in data if x.get('model') == 'organizations.organization']
    patients = [x for x in data if x.get('model') == 'patients.patient']
    
    print(f"✅ BACKUP VÁLIDO")
    print(f"   Usuarios: {len(users)}")
    print(f"   Organizaciones: {len(orgs)}")
    print(f"   Pacientes: {len(patients)}")
    print(f"   Total objetos: {len(data)}")
    
    if len(users) == 0:
        print("❌ ERROR: NO HAY USUARIOS EN EL BACKUP")
        sys.exit(1)
    
    sys.exit(0)
except Exception as e:
    print(f"❌ ERROR: {e}")
    sys.exit(1)
EOF
)

RESULT=$?
echo "$VERIFICATION" >> $LOG_FILE

if [ $RESULT -eq 0 ]; then
    # Backup válido - crear enlace simbólico al último
    ln -sf $BACKUP_FILE $LATEST_LINK
    
    # Comprimir backup antiguo (más de 1 día)
    find $BACKUP_DIR -name "backup_*.json" -mtime +1 -exec gzip {} \;
    
    # Eliminar backups antiguos (más de 30 días)
    find $BACKUP_DIR -name "backup_*.json.gz" -mtime +30 -delete
    
    echo "✅ Backup completado exitosamente: $BACKUP_FILE" >> $LOG_FILE
    
    # Enviar copia al escritorio local (opcional)
    # scp $BACKUP_FILE usuario@tupc:/ruta/backups/
    
else
    echo "❌ Backup FALLÓ - archivo corrupto o sin usuarios" >> $LOG_FILE
    rm -f $BACKUP_FILE
    exit 1
fi

echo "Backup finalizado: $(date)" >> $LOG_FILE
echo "" >> $LOG_FILE
