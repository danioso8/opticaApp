#!/bin/bash

# Script de instalacion completa del stack para Contabo VPS
# Ejecutar como root: bash install_full_stack.sh

set -e

echo "======================================================="
echo "  INSTALACION COMPLETA DEL STACK - CONTABO VPS"
echo "======================================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# 1. Actualizar sistema
echo -e "${YELLOW}[1/10] Actualizando sistema...${NC}"
apt update && apt upgrade -y
echo -e "${GREEN}[OK] Sistema actualizado${NC}"
echo ""

# 2. Instalar utilidades básicas
echo -e "${YELLOW}[2/10] Instalando utilidades básicas...${NC}"
apt install -y curl wget git ufw unzip htop vim net-tools software-properties-common
echo -e "${GREEN}[OK] Utilidades instaladas${NC}"
echo ""

# 3. Instalar Node.js 20
echo -e "${YELLOW}[3/10] Instalando Node.js 20...${NC}"
curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
apt install -y nodejs
NODE_VERSION=$(node --version)
NPM_VERSION=$(npm --version)
echo -e "${GREEN}[OK] Node.js $NODE_VERSION instalado${NC}"
echo -e "${GREEN}[OK] npm $NPM_VERSION instalado${NC}"
echo ""

# 4. Instalar PM2
echo -e "${YELLOW}[4/10] Instalando PM2...${NC}"
npm install -g pm2
PM2_VERSION=$(pm2 --version)
echo -e "${GREEN}[OK] PM2 $PM2_VERSION instalado${NC}"
echo ""

# 5. Instalar Python 3.11
echo -e "${YELLOW}[5/10] Instalando Python 3.11...${NC}"
add-apt-repository -y ppa:deadsnakes/ppa
apt update
apt install -y python3.11 python3.11-venv python3.11-dev python3-pip
update-alternatives --install /usr/bin/python3 python3 /usr/bin/python3.11 1
PYTHON_VERSION=$(python3 --version)
echo -e "${GREEN}[OK] $PYTHON_VERSION instalado${NC}"
echo ""

# 6. Instalar PostgreSQL 15
echo -e "${YELLOW}[6/10] Instalando PostgreSQL 15...${NC}"
sh -c 'echo "deb http://apt.postgresql.org/pub/repos/apt $(lsb_release -cs)-pgdg main" > /etc/apt/sources.list.d/pgdg.list'
wget --quiet -O - https://www.postgresql.org/media/keys/ACCC4CF8.asc | apt-key add -
apt update
apt install -y postgresql-15 postgresql-contrib-15
systemctl enable postgresql
systemctl start postgresql
PSQL_VERSION=$(sudo -u postgres psql --version)
echo -e "${GREEN}[OK] $PSQL_VERSION instalado${NC}"
echo ""

# 7. Instalar Nginx
echo -e "${YELLOW}[7/10] Instalando Nginx...${NC}"
apt install -y nginx
systemctl enable nginx
systemctl start nginx
NGINX_VERSION=$(nginx -v 2>&1)
echo -e "${GREEN}[OK] $NGINX_VERSION instalado${NC}"
echo ""

# 8. Instalar Certbot (SSL)
echo -e "${YELLOW}[8/10] Instalando Certbot para SSL...${NC}"
apt install -y certbot python3-certbot-nginx
echo -e "${GREEN}[OK] Certbot instalado${NC}"
echo ""

# 9. Instalar dependencias adicionales
echo -e "${YELLOW}[9/10] Instalando dependencias adicionales...${NC}"
apt install -y build-essential libssl-dev libffi-dev
apt install -y libpq-dev python3.11-distutils
pip3 install --upgrade pip setuptools wheel
echo -e "${GREEN}[OK] Dependencias instaladas${NC}"
echo ""

# 10. Configurar firewall básico
echo -e "${YELLOW}[10/10] Configurando firewall...${NC}"
ufw --force reset
ufw default deny incoming
ufw default allow outgoing
ufw allow 22/tcp comment 'SSH'
ufw allow 80/tcp comment 'HTTP'
ufw allow 443/tcp comment 'HTTPS'
ufw allow 3000/tcp comment 'WhatsApp Server'
ufw --force enable
echo -e "${GREEN}[OK] Firewall configurado${NC}"
echo ""

# Crear directorios base
echo -e "${YELLOW}Creando estructura de directorios...${NC}"
mkdir -p /var/www
mkdir -p /root/backups
mkdir -p /root/scripts
echo -e "${GREEN}[OK] Directorios creados${NC}"
echo ""

# Resumen
echo "======================================================="
echo -e "${GREEN}  INSTALACION COMPLETADA EXITOSAMENTE${NC}"
echo "======================================================="
echo ""
echo -e "${YELLOW}Software instalado:${NC}"
echo "  - Node.js: $NODE_VERSION"
echo "  - PM2: $PM2_VERSION"
echo "  - Python: $PYTHON_VERSION"
echo "  - PostgreSQL: $PSQL_VERSION"
echo "  - Nginx: $NGINX_VERSION"
echo "  - Certbot: Instalado"
echo ""
echo -e "${YELLOW}Siguiente paso:${NC}"
echo "  1. Crear bases de datos: bash create_databases.sh"
echo "  2. Subir proyectos a /var/www/"
echo "  3. Desplegar proyectos: bash deploy_project.sh"
echo ""
echo -e "${YELLOW}IP del servidor:${NC} $(hostname -I | awk '{print $1}')"
echo ""
