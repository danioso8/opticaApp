#!/bin/bash
# Script para actualizar OpticaApp en Contabo con la corrección de email

echo "========================================"
echo "ACTUALIZANDO OPTICAAPP EN CONTABO"
echo "========================================"

SERVER_IP="84.247.129.180"
SERVER_USER="root"
APP_DIR="/var/www/opticaapp"

echo ""
echo "1️⃣  Descargando cambios del repositorio..."
ssh ${SERVER_USER}@${SERVER_IP} << 'EOF'
cd /var/www/opticaapp
git pull origin main
EOF

echo ""
echo "2️⃣  Actualizando variables de entorno..."
ssh ${SERVER_USER}@${SERVER_IP} << 'EOF'
cd /var/www/opticaapp

# Verificar si las variables de email ya existen
if ! grep -q "EMAIL_BACKEND" .env; then
    echo ""
    echo "Agregando configuración de email al .env..."
    cat >> .env << 'ENVEOF'

# ==================== Email Configuration ====================
# Configuración de Gmail SMTP para notificaciones
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_USE_SSL=False
EMAIL_HOST_USER=compueasys@gmail.com
EMAIL_HOST_PASSWORD=hucewtoa stbqrcnk
DEFAULT_FROM_EMAIL=OpticaApp <compueasys@gmail.com>
CONTACT_EMAIL=compueasys@gmail.com

# ==================== Notification Settings ====================
# True = Usar Email en producción (gratis)
# False = Usar WhatsApp local en desarrollo
USE_EMAIL_NOTIFICATIONS=True
ENVEOF
    echo "✅ Variables de email agregadas"
else
    echo "⚠️  Variables de email ya existen en .env"
fi
EOF

echo ""
echo "3️⃣  Reiniciando aplicación Django..."
ssh ${SERVER_USER}@${SERVER_IP} << 'EOF'
pm2 restart opticaapp
pm2 save
EOF

echo ""
echo "4️⃣  Verificando estado de los servicios..."
ssh ${SERVER_USER}@${SERVER_IP} << 'EOF'
pm2 status
EOF

echo ""
echo "========================================"
echo "✅ ACTUALIZACIÓN COMPLETADA"
echo "========================================"
echo ""
echo "El sistema de verificación de email ahora está configurado en Contabo"
echo ""
echo "Para verificar logs:"
echo "  ssh root@84.247.129.180"
echo "  pm2 logs opticaapp"
echo ""
