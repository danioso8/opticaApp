#!/bin/bash

# Script para iniciar el servidor de WhatsApp con PM2
# Ejecutar: bash start_whatsapp.sh

set -e

echo "========================================="
echo "  INICIANDO SERVIDOR WHATSAPP"
echo "========================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# Verificar que estamos en el directorio correcto
if [ ! -f "/root/whatsapp-server/server.js" ]; then
    echo -e "${RED}[ERROR] No se encuentra server.js${NC}"
    echo "Asegurate de estar en /root/whatsapp-server/"
    exit 1
fi

cd /root/whatsapp-server

# Detener si ya está corriendo
echo -e "${YELLOW}Deteniendo procesos anteriores...${NC}"
pm2 delete whatsapp-opticaapp 2>/dev/null || true
echo ""

# Iniciar con PM2
echo -e "${YELLOW}Iniciando servidor con PM2...${NC}"
pm2 start server.js --name whatsapp-opticaapp

# Guardar configuración
pm2 save

# Configurar auto-inicio
pm2 startup | grep -v PM2 | bash || true

echo ""
echo -e "${GREEN}[OK] Servidor iniciado correctamente${NC}"
echo ""

# Mostrar estado
pm2 status

echo ""
echo "========================================="
echo -e "${GREEN}  SERVIDOR CORRIENDO${NC}"
echo "========================================="
echo ""
echo -e "${YELLOW}IMPORTANTE:${NC}"
echo "1. El servidor mostrará un código QR en los logs"
echo "2. Escanea el QR con WhatsApp en tu celular"
echo ""
echo -e "${YELLOW}Para ver el QR, ejecuta:${NC}"
echo -e "   ${GREEN}pm2 logs whatsapp-opticaapp${NC}"
echo ""
echo -e "${YELLOW}Para detener los logs:${NC}"
echo "   Presiona Ctrl+C"
echo ""
echo -e "${YELLOW}Comandos útiles:${NC}"
echo "   pm2 status              - Ver estado"
echo "   pm2 logs                - Ver logs"
echo "   pm2 restart whatsapp-opticaapp - Reiniciar"
echo "   pm2 stop whatsapp-opticaapp    - Detener"
echo ""
echo -e "${YELLOW}URL del servidor:${NC}"
echo "   http://$(hostname -I | awk '{print $1}'):3000"
echo ""
echo -e "${YELLOW}Configurar en Render:${NC}"
echo "   WHATSAPP_SERVER_URL=http://$(hostname -I | awk '{print $1}'):3000"
echo ""

# Mostrar logs automáticamente
echo -e "${YELLOW}Mostrando logs (Ctrl+C para salir)...${NC}"
echo ""
sleep 2
pm2 logs whatsapp-opticaapp
