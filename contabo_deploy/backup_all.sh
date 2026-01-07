#!/bin/bash

# Script de respaldo automático para todos los proyectos
# Ejecutar: bash backup_all.sh
# Configurar en cron: 0 2 * * * /root/backup_all.sh

set -e

BACKUP_DIR="/root/backups"
DATE=$(date +%Y%m%d_%H%M%S)
BACKUP_PATH="${BACKUP_DIR}/${DATE}"

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo "======================================================="
echo "  RESPALDO AUTOMÁTICO - $(date)"
echo "======================================================="
echo ""

# Crear directorio de respaldo
mkdir -p $BACKUP_PATH

# Array de proyectos
PROJECTS=("proyecto1" "proyecto2" "proyecto3" "proyecto4" "proyecto5" "proyecto6" "opticaapp")

# 1. Respaldar bases de datos
echo -e "${YELLOW}[1/4] Respaldando bases de datos...${NC}"
mkdir -p ${BACKUP_PATH}/databases

for PROJECT in "${PROJECTS[@]}"; do
    DB_NAME="${PROJECT}_db"
    DB_USER="${PROJECT}_user"
    DB_FILE="${BACKUP_PATH}/databases/${DB_NAME}.sql"
    
    echo "  - Respaldando ${DB_NAME}..."
    sudo -u postgres pg_dump $DB_NAME > $DB_FILE
    gzip $DB_FILE
    echo -e "${GREEN}    [OK] ${DB_NAME}.sql.gz${NC}"
done

echo -e "${GREEN}[OK] Bases de datos respaldadas${NC}"
echo ""

# 2. Respaldar archivos media
echo -e "${YELLOW}[2/4] Respaldando archivos media...${NC}"
mkdir -p ${BACKUP_PATH}/media

for PROJECT in "${PROJECTS[@]}"; do
    MEDIA_DIR="/var/www/${PROJECT}/media"
    if [ -d "$MEDIA_DIR" ]; then
        echo "  - Respaldando media de ${PROJECT}..."
        tar -czf ${BACKUP_PATH}/media/${PROJECT}_media.tar.gz -C $MEDIA_DIR . 2>/dev/null || true
        echo -e "${GREEN}    [OK] ${PROJECT}_media.tar.gz${NC}"
    fi
done

echo -e "${GREEN}[OK] Archivos media respaldados${NC}"
echo ""

# 3. Respaldar configuraciones de Nginx
echo -e "${YELLOW}[3/4] Respaldando configuraciones Nginx...${NC}"
mkdir -p ${BACKUP_PATH}/nginx
cp -r /etc/nginx/sites-available ${BACKUP_PATH}/nginx/
tar -czf ${BACKUP_PATH}/nginx_configs.tar.gz -C ${BACKUP_PATH} nginx
rm -rf ${BACKUP_PATH}/nginx
echo -e "${GREEN}[OK] Configuraciones Nginx respaldadas${NC}"
echo ""

# 4. Respaldar sesiones de WhatsApp
echo -e "${YELLOW}[4/4] Respaldando sesiones WhatsApp...${NC}"
WHATSAPP_DIR="/var/www/whatsapp-server/auth_sessions"
if [ -d "$WHATSAPP_DIR" ]; then
    tar -czf ${BACKUP_PATH}/whatsapp_sessions.tar.gz -C /var/www/whatsapp-server auth_sessions
    echo -e "${GREEN}[OK] Sesiones WhatsApp respaldadas${NC}"
else
    echo "  - No se encontraron sesiones WhatsApp"
fi
echo ""

# Calcular tamaño del respaldo
BACKUP_SIZE=$(du -sh $BACKUP_PATH | cut -f1)

echo "======================================================="
echo -e "${GREEN}  RESPALDO COMPLETADO${NC}"
echo "======================================================="
echo ""
echo -e "${YELLOW}Ubicación:${NC} $BACKUP_PATH"
echo -e "${YELLOW}Tamaño:${NC} $BACKUP_SIZE"
echo ""
echo -e "${YELLOW}Contenido:${NC}"
ls -lh $BACKUP_PATH
echo ""

# Limpiar respaldos antiguos (mantener solo 7 días)
echo -e "${YELLOW}Limpiando respaldos antiguos (>7 días)...${NC}"
find $BACKUP_DIR -type d -mtime +7 -exec rm -rf {} + 2>/dev/null || true
echo -e "${GREEN}[OK] Respaldos antiguos eliminados${NC}"
echo ""

# Resumen
echo -e "${YELLOW}Respaldos disponibles:${NC}"
ls -lt $BACKUP_DIR | head -n 8
echo ""
