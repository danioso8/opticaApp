#!/bin/bash
# Script para actualizar OpticaApp en servidor Contabo

echo "============================================"
echo " ACTUALIZANDO OPTICAAPP EN CONTABO"
echo "============================================"

SERVER="root@84.247.129.180"
APP_DIR="/var/www/opticaapp"

echo ""
echo "1. Comprimiendo archivos..."
zip -r opticaapp_update.zip \
    apps \
    opticaapp \
    static \
    templates \
    manage.py \
    requirements.txt \
    package.json \
    tailwind.config.js \
    -x "*.pyc" "*/__pycache__/*" "*/.git/*" "*/.venv/*" "*/venv/*" "*.sqlite3" "*/node_modules/*" "*/auth_sessions/*" "*.log" "*/media/*" "*/staticfiles/*"

echo "Archivos comprimidos"

echo ""
echo "2. Subiendo archivos al servidor..."
scp opticaapp_update.zip $SERVER:/var/www/

echo ""
echo "3. Descomprimiendo en servidor..."
ssh $SERVER << 'ENDSSH'
cd /var/www/opticaapp
unzip -o /var/www/opticaapp_update.zip
rm /var/www/opticaapp_update.zip
echo "Codigo actualizado"
ENDSSH

echo ""
echo "4. Instalando dependencias Python..."
ssh $SERVER << 'ENDSSH'
cd /var/www/opticaapp
source venv/bin/activate
pip install -r requirements.txt
ENDSSH

echo ""
echo "5. Ejecutando migraciones..."
ssh $SERVER << 'ENDSSH'
cd /var/www/opticaapp
source venv/bin/activate
python manage.py migrate
ENDSSH

echo ""
echo "6. Compilando Tailwind CSS..."
ssh $SERVER << 'ENDSSH'
cd /var/www/opticaapp
npm run build:css
ENDSSH

echo ""
echo "7. Recolectando archivos estaticos..."
ssh $SERVER << 'ENDSSH'
cd /var/www/opticaapp
source venv/bin/activate
python manage.py collectstatic --noinput
ENDSSH

echo ""
echo "8. Reiniciando servicios..."
ssh $SERVER << 'ENDSSH'
sudo systemctl restart gunicorn || sudo systemctl restart opticaapp
sudo systemctl reload nginx
ENDSSH

echo ""
echo "============================================"
echo " ACTUALIZACION COMPLETADA"
echo "============================================"
echo ""
echo "URL: https://www.opticapp.com.co"

# Limpiar archivo temporal
rm opticaapp_update.zip
