#!/bin/bash
# Script para desplegar cambios en Contabo

echo "🚀 DESPLEGANDO EN CONTABO..."
echo "================================"

cd /home/optica/OpticaApp

echo ""
echo "📥 1. Obteniendo últimos cambios..."
git fetch origin
git pull origin main

echo ""
echo "📦 2. Instalando dependencias Python..."
source venv/bin/activate
pip install -r requirements.txt

echo ""
echo "🗃️  3. Ejecutando migraciones..."
python manage.py migrate

echo ""
echo "📊 4. Recolectando archivos estáticos..."
python manage.py collectstatic --noinput

echo ""
echo "🔄 5. Reiniciando servicios..."
sudo systemctl restart opticaapp
sudo systemctl reload nginx

echo ""
echo "✅ Despliegue Django completado"
echo ""
echo "================================"
echo "🔍 VERIFICANDO SERVIDOR WHATSAPP"
echo "================================"

# Verificar si el servidor WhatsApp está corriendo
if pm2 list | grep -q "whatsapp-server"; then
    echo "✅ Servidor WhatsApp encontrado en PM2"
    echo ""
    echo "📊 Estado actual:"
    pm2 info whatsapp-server
    
    echo ""
    echo "📋 Logs recientes:"
    pm2 logs whatsapp-server --lines 20 --nostream
else
    echo "❌ Servidor WhatsApp NO está en PM2"
    echo ""
    echo "🔧 Iniciando servidor WhatsApp..."
    cd /home/optica/whatsapp-server
    pm2 start server.js --name whatsapp-server
    pm2 save
fi

echo ""
echo "================================"
echo "✅ PROCESO COMPLETADO"
echo "================================"
echo ""
echo "🌐 URLs:"
echo "   - Django: https://www.opticapp.com.co"
echo "   - WhatsApp API: http://localhost:3000"
echo ""
echo "📊 Comandos útiles:"
echo "   pm2 status                     - Ver estado servicios"
echo "   pm2 logs whatsapp-server       - Ver logs WhatsApp"
echo "   pm2 restart whatsapp-server    - Reiniciar WhatsApp"
echo "   sudo systemctl status opticaapp - Ver estado Django"
