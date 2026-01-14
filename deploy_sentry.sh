#!/bin/bash
# Script de deployment de Sentry y Auto-Fix a Contabo
# Ejecutar desde local: bash deploy_sentry.sh

set -e  # Exit on error

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

SERVER="root@84.247.129.180"
APP_DIR="/var/www/opticaapp"
LOCAL_DIR="d:/ESCRITORIO/OpticaApp"

echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}🚀 Deployment de Sentry y Bot Auto-Fix${NC}"
echo -e "${GREEN}================================================${NC}\n"

# 1. Subir archivos nuevos
echo -e "${YELLOW}📤 Subiendo archivos al servidor...${NC}"

scp "${LOCAL_DIR}/config/sentry.py" ${SERVER}:${APP_DIR}/config/
scp "${LOCAL_DIR}/apps/audit/error_auto_fix.py" ${SERVER}:${APP_DIR}/apps/audit/
scp "${LOCAL_DIR}/apps/audit/management/commands/auto_fix_errors.py" ${SERVER}:${APP_DIR}/apps/audit/management/commands/
scp "${LOCAL_DIR}/requirements.txt" ${SERVER}:${APP_DIR}/
scp "${LOCAL_DIR}/config/settings.py" ${SERVER}:${APP_DIR}/config/
scp "${LOCAL_DIR}/setup_sentry.py" ${SERVER}:${APP_DIR}/
scp "${LOCAL_DIR}/SENTRY_Y_AUTO_FIX.md" ${SERVER}:${APP_DIR}/

echo -e "${GREEN}✅ Archivos subidos${NC}\n"

# 2. Instalar dependencias
echo -e "${YELLOW}📦 Instalando dependencias...${NC}"

ssh ${SERVER} << 'EOF'
cd /var/www/opticaapp
source venv/bin/activate
pip install sentry-sdk==1.40.0
echo "✅ sentry-sdk instalado"
EOF

echo -e "${GREEN}✅ Dependencias instaladas${NC}\n"

# 3. Verificar estructura de directorios
echo -e "${YELLOW}📁 Verificando directorios...${NC}"

ssh ${SERVER} << 'EOF'
mkdir -p /var/www/opticaapp/apps/audit/management/commands
mkdir -p /var/log/opticaapp
touch /var/www/opticaapp/apps/audit/management/__init__.py
touch /var/www/opticaapp/apps/audit/management/commands/__init__.py
echo "✅ Directorios verificados"
EOF

echo -e "${GREEN}✅ Directorios creados${NC}\n"

# 4. Reiniciar aplicación
echo -e "${YELLOW}🔄 Reiniciando aplicación...${NC}"

ssh ${SERVER} << 'EOF'
pm2 restart opticaapp
sleep 3
pm2 logs opticaapp --lines 20 --nostream
EOF

echo -e "${GREEN}✅ Aplicación reiniciada${NC}\n"

# 5. Verificar instalación
echo -e "${YELLOW}🔍 Verificando instalación...${NC}"

ssh ${SERVER} << 'EOF'
cd /var/www/opticaapp
source venv/bin/activate

# Verificar que sentry-sdk está instalado
python -c "import sentry_sdk; print('✅ sentry-sdk importado correctamente')" || echo "❌ Error al importar sentry-sdk"

# Verificar que el módulo de auto-fix existe
python -c "from apps.audit.error_auto_fix import auto_fix_errors; print('✅ error_auto_fix importado correctamente')" || echo "❌ Error al importar error_auto_fix"

# Verificar comando de management
python manage.py auto_fix_errors --dry-run || echo "⚠️ Comando auto_fix_errors no disponible aún (normal si no hay errores)"

EOF

echo -e "${GREEN}✅ Verificación completada${NC}\n"

# 6. Instrucciones finales
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}✅ DEPLOYMENT COMPLETADO${NC}"
echo -e "${GREEN}================================================${NC}\n"

echo -e "${YELLOW}📋 PRÓXIMOS PASOS:${NC}\n"

echo -e "1. Configurar Sentry DSN en el servidor:"
echo -e "   ${GREEN}ssh ${SERVER}${NC}"
echo -e "   ${GREEN}nano ${APP_DIR}/.env${NC}"
echo -e "   Agregar:"
echo -e "   ${GREEN}SENTRY_DSN=https://TU_DSN_AQUI@o123456.ingest.sentry.io/7654321${NC}"
echo -e "   ${GREEN}ENVIRONMENT=production${NC}"
echo -e "   ${GREEN}APP_VERSION=1.0.0${NC}\n"

echo -e "2. Reiniciar aplicación:"
echo -e "   ${GREEN}pm2 restart opticaapp${NC}\n"

echo -e "3. Probar auto-corrección:"
echo -e "   ${GREEN}python manage.py auto_fix_errors --dry-run${NC}\n"

echo -e "4. Ver instrucciones completas:"
echo -e "   ${GREEN}python setup_sentry.py${NC}\n"

echo -e "5. Dashboard de errores interno:"
echo -e "   ${GREEN}http://84.247.129.180/saas-admin/errors/${NC}\n"

echo -e "${YELLOW}📚 Documentación completa: SENTRY_Y_AUTO_FIX.md${NC}\n"

echo -e "${GREEN}================================================${NC}\n"
