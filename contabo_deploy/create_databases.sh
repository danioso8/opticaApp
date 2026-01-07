#!/bin/bash

# Script para crear 7 bases de datos PostgreSQL independientes
# Ejecutar como root: bash create_databases.sh

set -e

echo "======================================================="
echo "  CREAR BASES DE DATOS Y USUARIOS"
echo "======================================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Función para generar contraseña aleatoria
generate_password() {
    openssl rand -base64 16 | tr -d "=+/" | cut -c1-16
}

# Array de proyectos
PROJECTS=("proyecto1" "proyecto2" "proyecto3" "proyecto4" "proyecto5" "proyecto6" "opticaapp")

# Archivo para guardar credenciales
CREDENTIALS_FILE="/root/database_credentials.txt"
echo "# CREDENCIALES DE BASES DE DATOS" > $CREDENTIALS_FILE
echo "# Generado: $(date)" >> $CREDENTIALS_FILE
echo "" >> $CREDENTIALS_FILE

echo -e "${YELLOW}Creando 7 bases de datos...${NC}"
echo ""

for PROJECT in "${PROJECTS[@]}"; do
    DB_NAME="${PROJECT}_db"
    DB_USER="${PROJECT}_user"
    DB_PASS=$(generate_password)
    
    echo -e "${YELLOW}[${PROJECT}] Creando base de datos y usuario...${NC}"
    
    # Crear base de datos
    sudo -u postgres psql -c "CREATE DATABASE ${DB_NAME};" 2>/dev/null || echo "  - BD ${DB_NAME} ya existe"
    
    # Crear usuario
    sudo -u postgres psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASS}';" 2>/dev/null || echo "  - Usuario ${DB_USER} ya existe"
    
    # Otorgar privilegios
    sudo -u postgres psql -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER};"
    sudo -u postgres psql -c "ALTER DATABASE ${DB_NAME} OWNER TO ${DB_USER};"
    
    # Guardar credenciales
    echo "[${PROJECT}]" >> $CREDENTIALS_FILE
    echo "DATABASE_NAME=${DB_NAME}" >> $CREDENTIALS_FILE
    echo "DATABASE_USER=${DB_USER}" >> $CREDENTIALS_FILE
    echo "DATABASE_PASSWORD=${DB_PASS}" >> $CREDENTIALS_FILE
    echo "DATABASE_HOST=localhost" >> $CREDENTIALS_FILE
    echo "DATABASE_PORT=5432" >> $CREDENTIALS_FILE
    echo "" >> $CREDENTIALS_FILE
    
    echo -e "${GREEN}[OK] ${PROJECT} - BD y usuario creados${NC}"
    echo ""
done

# Configurar autenticación
echo -e "${YELLOW}Configurando autenticación PostgreSQL...${NC}"

# Backup de configuración original
cp /etc/postgresql/15/main/pg_hba.conf /etc/postgresql/15/main/pg_hba.conf.backup

# Agregar reglas de acceso local
cat >> /etc/postgresql/15/main/pg_hba.conf << 'EOF'

# Reglas para proyectos Django (agregadas por script)
local   all             all                                     md5
host    all             all             127.0.0.1/32            md5
host    all             all             ::1/128                 md5
EOF

echo -e "${GREEN}[OK] Autenticación configurada${NC}"
echo ""

# Reiniciar PostgreSQL
echo -e "${YELLOW}Reiniciando PostgreSQL...${NC}"
systemctl restart postgresql
echo -e "${GREEN}[OK] PostgreSQL reiniciado${NC}"
echo ""

# Resumen
echo "======================================================="
echo -e "${GREEN}  BASES DE DATOS CREADAS EXITOSAMENTE${NC}"
echo "======================================================="
echo ""
echo -e "${YELLOW}Bases de datos creadas:${NC}"
for PROJECT in "${PROJECTS[@]}"; do
    echo "  - ${PROJECT}_db"
done
echo ""
echo -e "${YELLOW}Credenciales guardadas en:${NC}"
echo "  ${CREDENTIALS_FILE}"
echo ""
echo -e "${YELLOW}Ver credenciales:${NC}"
echo "  cat ${CREDENTIALS_FILE}"
echo ""
echo -e "${YELLOW}Conectar a base de datos:${NC}"
echo "  psql -U proyecto1_user -d proyecto1_db"
echo ""
