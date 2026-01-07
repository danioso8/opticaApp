#!/bin/bash

# Script de instalacion automatica para Contabo VPS
# Ejecutar como root: bash install_contabo.sh

set -e  # Detener si hay errores

echo "========================================="
echo "  OPTICAAPP - INSTALACION EN CONTABO"
echo "========================================="
echo ""

# Colores
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# 1. Actualizar sistema
echo -e "${YELLOW}[1/7] Actualizando sistema...${NC}"
apt update && apt upgrade -y
echo -e "${GREEN}[OK] Sistema actualizado${NC}"
echo ""

# 2. Instalar utilidades
echo -e "${YELLOW}[2/7] Instalando utilidades...${NC}"
apt install -y curl wget git ufw unzip htop
echo -e "${GREEN}[OK] Utilidades instaladas${NC}"
echo ""

# 3. Instalar Node.js 20
echo -e "${YELLOW}[3/7] Instalando Node.js 20...${NC}"
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
NODE_VERSION=$(node --version)
NPM_VERSION=$(npm --version)
echo -e "${GREEN}[OK] Node.js $NODE_VERSION instalado${NC}"
echo -e "${GREEN}[OK] npm $NPM_VERSION instalado${NC}"
echo ""

# 4. Instalar PM2
echo -e "${YELLOW}[4/7] Instalando PM2...${NC}"
npm install -g pm2
PM2_VERSION=$(pm2 --version)
echo -e "${GREEN}[OK] PM2 $PM2_VERSION instalado${NC}"
echo ""

# 5. Configurar firewall
echo -e "${YELLOW}[5/7] Configurando firewall...${NC}"
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 3000/tcp comment 'WhatsApp Server'
ufw --force enable
echo -e "${GREEN}[OK] Firewall configurado${NC}"
ufw status
echo ""

# 6. Crear directorio para WhatsApp server
echo -e "${YELLOW}[6/7] Creando directorio de trabajo...${NC}"
mkdir -p /root/whatsapp-server
cd /root/whatsapp-server

# Crear package.json
cat > package.json << 'EOF'
{
  "name": "opticaapp-whatsapp-server",
  "version": "1.0.0",
  "description": "Servidor WhatsApp Baileys para OpticaApp",
  "main": "server.js",
  "scripts": {
    "start": "node server.js"
  },
  "dependencies": {
    "@whiskeysockets/baileys": "^6.6.0",
    "express": "^4.18.2",
    "qrcode-terminal": "^0.12.0",
    "pino": "^8.16.0"
  }
}
EOF

echo -e "${GREEN}[OK] Directorio creado: /root/whatsapp-server${NC}"
echo ""

# 7. Instalar dependencias npm
echo -e "${YELLOW}[7/7] Instalando dependencias de Node.js...${NC}"
npm install
echo -e "${GREEN}[OK] Dependencias instaladas${NC}"
echo ""

# Resumen
echo "========================================="
echo -e "${GREEN}  INSTALACION COMPLETADA${NC}"
echo "========================================="
echo ""
echo -e "${YELLOW}Siguiente paso:${NC}"
echo "1. Sube el archivo server.js a /root/whatsapp-server/"
echo ""
echo "   Desde tu PC (PowerShell):"
echo -e "   ${GREEN}scp D:\\ESCRITORIO\\OpticaApp\\whatsapp-server\\server.js root@$(hostname -I | awk '{print $1}'):/root/whatsapp-server/${NC}"
echo ""
echo "2. Luego ejecuta:"
echo -e "   ${GREEN}bash start_whatsapp.sh${NC}"
echo ""
echo -e "${YELLOW}IP del servidor:${NC} $(hostname -I | awk '{print $1}')"
echo ""
