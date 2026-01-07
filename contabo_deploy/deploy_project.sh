#!/bin/bash

# Script para desplegar un proyecto Django en Contabo
# Uso: bash deploy_project.sh NOMBRE_PROYECTO PUERTO DB_NAME DB_USER

set -e

if [ $# -ne 4 ]; then
    echo "Uso: bash deploy_project.sh NOMBRE_PROYECTO PUERTO DB_NAME DB_USER"
    echo "Ejemplo: bash deploy_project.sh opticaapp 8007 opticaapp_db opticaapp_user"
    exit 1
fi

PROJECT_NAME=$1
PORT=$2
DB_NAME=$3
DB_USER=$4

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

PROJECT_DIR="/var/www/${PROJECT_NAME}"

echo "======================================================="
echo "  DESPLEGAR PROYECTO: ${PROJECT_NAME}"
echo "======================================================="
echo ""

# Verificar que el directorio existe
if [ ! -d "$PROJECT_DIR" ]; then
    echo -e "${RED}[ERROR] Directorio no existe: ${PROJECT_DIR}${NC}"
    echo "Crea el directorio y sube el código primero:"
    echo "  mkdir -p ${PROJECT_DIR}"
    echo "  cd ${PROJECT_DIR}"
    echo "  git clone TU_REPO ."
    exit 1
fi

cd $PROJECT_DIR

# 1. Crear entorno virtual
echo -e "${YELLOW}[1/9] Creando entorno virtual...${NC}"
python3 -m venv venv
source venv/bin/activate
echo -e "${GREEN}[OK] Entorno virtual creado${NC}"
echo ""

# 2. Instalar dependencias
echo -e "${YELLOW}[2/9] Instalando dependencias...${NC}"
if [ -f "requirements.txt" ]; then
    pip install --upgrade pip
    pip install -r requirements.txt
    pip install gunicorn psycopg2-binary
    echo -e "${GREEN}[OK] Dependencias instaladas${NC}"
else
    echo -e "${RED}[ERROR] No se encontró requirements.txt${NC}"
    exit 1
fi
echo ""

# 3. Obtener credenciales de BD
echo -e "${YELLOW}[3/9] Obteniendo credenciales de base de datos...${NC}"
DB_PASSWORD=$(grep -A 5 "\[${PROJECT_NAME}\]" /root/database_credentials.txt | grep DATABASE_PASSWORD | cut -d'=' -f2)
if [ -z "$DB_PASSWORD" ]; then
    echo -e "${RED}[ERROR] No se encontró contraseña para ${PROJECT_NAME}${NC}"
    echo "Ejecuta primero: bash create_databases.sh"
    exit 1
fi
echo -e "${GREEN}[OK] Credenciales obtenidas${NC}"
echo ""

# 4. Crear archivo .env
echo -e "${YELLOW}[4/9] Creando archivo .env...${NC}"
cat > .env << EOF
# Configuración Django para ${PROJECT_NAME}
DEBUG=False
SECRET_KEY=$(openssl rand -base64 32)
ALLOWED_HOSTS=${PROJECT_NAME}.tudominio.com,localhost,127.0.0.1

# Base de datos
DATABASE_NAME=${DB_NAME}
DATABASE_USER=${DB_USER}
DATABASE_PASSWORD=${DB_PASSWORD}
DATABASE_HOST=localhost
DATABASE_PORT=5432

# WhatsApp (solo para opticaapp)
WHATSAPP_SERVER_URL=http://localhost:3000
WHATSAPP_API_KEY=opticaapp_2026_whatsapp_baileys_secret_key_12345

# Email (configurar según necesites)
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
# EMAIL_HOST_USER=tu@email.com
# EMAIL_HOST_PASSWORD=tu_password
EOF
echo -e "${GREEN}[OK] Archivo .env creado${NC}"
echo ""

# 5. Ejecutar migraciones
echo -e "${YELLOW}[5/9] Ejecutando migraciones...${NC}"
python manage.py migrate --noinput
echo -e "${GREEN}[OK] Migraciones aplicadas${NC}"
echo ""

# 6. Recolectar archivos estáticos
echo -e "${YELLOW}[6/9] Recolectando archivos estáticos...${NC}"
python manage.py collectstatic --noinput
echo -e "${GREEN}[OK] Estáticos recolectados${NC}"
echo ""

# 7. Crear directorios necesarios
echo -e "${YELLOW}[7/9] Creando directorios...${NC}"
mkdir -p logs media
chown -R www-data:www-data media
echo -e "${GREEN}[OK] Directorios creados${NC}"
echo ""

# 8. Crear script de inicio para PM2
echo -e "${YELLOW}[8/9] Creando script de inicio...${NC}"
cat > start.sh << EOF
#!/bin/bash
cd ${PROJECT_DIR}
source venv/bin/activate
exec gunicorn ${PROJECT_NAME}.wsgi:application \\
    --bind 0.0.0.0:${PORT} \\
    --workers 3 \\
    --timeout 120 \\
    --access-logfile logs/access.log \\
    --error-logfile logs/error.log \\
    --log-level info
EOF
chmod +x start.sh
echo -e "${GREEN}[OK] Script de inicio creado${NC}"
echo ""

# 9. Iniciar con PM2
echo -e "${YELLOW}[9/9] Iniciando proyecto con PM2...${NC}"
pm2 delete ${PROJECT_NAME} 2>/dev/null || true
pm2 start start.sh --name ${PROJECT_NAME}
pm2 save
echo -e "${GREEN}[OK] Proyecto iniciado${NC}"
echo ""

# Resumen
echo "======================================================="
echo -e "${GREEN}  PROYECTO DESPLEGADO EXITOSAMENTE${NC}"
echo "======================================================="
echo ""
echo -e "${YELLOW}Proyecto:${NC} ${PROJECT_NAME}"
echo -e "${YELLOW}Puerto:${NC} ${PORT}"
echo -e "${YELLOW}Base de datos:${NC} ${DB_NAME}"
echo -e "${YELLOW}Usuario BD:${NC} ${DB_USER}"
echo ""
echo -e "${YELLOW}Comandos útiles:${NC}"
echo "  pm2 logs ${PROJECT_NAME}     - Ver logs"
echo "  pm2 restart ${PROJECT_NAME}  - Reiniciar"
echo "  pm2 stop ${PROJECT_NAME}     - Detener"
echo ""
echo -e "${YELLOW}Probar:${NC}"
echo "  curl http://localhost:${PORT}"
echo ""
echo -e "${YELLOW}Siguiente paso:${NC}"
echo "  Configurar Nginx para ${PROJECT_NAME}.tudominio.com"
echo ""
