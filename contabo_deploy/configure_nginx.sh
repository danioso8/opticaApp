#!/bin/bash

# Script para configurar Nginx para todos los proyectos
# Ejecutar como root: bash configure_nginx.sh

set -e

echo "======================================================="
echo "  CONFIGURAR NGINX PARA 7 PROYECTOS"
echo "======================================================="
echo ""

GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Solicitar dominio base
read -p "Ingresa tu dominio base (ej: tudominio.com): " BASE_DOMAIN

if [ -z "$BASE_DOMAIN" ]; then
    echo "Dominio no puede estar vacío"
    exit 1
fi

# Array de proyectos y puertos
declare -A PROJECTS=(
    ["proyecto1"]="8001"
    ["proyecto2"]="8002"
    ["proyecto3"]="8003"
    ["proyecto4"]="8004"
    ["proyecto5"]="8005"
    ["proyecto6"]="8006"
    ["opticaapp"]="8007"
)

echo -e "${YELLOW}Creando configuraciones Nginx...${NC}"
echo ""

for PROJECT in "${!PROJECTS[@]}"; do
    PORT=${PROJECTS[$PROJECT]}
    SUBDOMAIN="${PROJECT}.${BASE_DOMAIN}"
    CONFIG_FILE="/etc/nginx/sites-available/${PROJECT}"
    
    echo -e "${YELLOW}[${PROJECT}] Creando configuración...${NC}"
    
    # Crear configuración
    cat > $CONFIG_FILE << EOF
server {
    listen 80;
    server_name ${SUBDOMAIN};

    client_max_body_size 100M;

    location / {
        proxy_pass http://localhost:${PORT};
        proxy_set_header Host \$host;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
        proxy_redirect off;
        proxy_buffering off;
    }

    location /static/ {
        alias /var/www/${PROJECT}/static/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    location /media/ {
        alias /var/www/${PROJECT}/media/;
        expires 30d;
        add_header Cache-Control "public, immutable";
    }

    access_log /var/log/nginx/${PROJECT}_access.log;
    error_log /var/log/nginx/${PROJECT}_error.log;
}
EOF

    # Crear enlace simbólico
    ln -sf $CONFIG_FILE /etc/nginx/sites-enabled/${PROJECT}
    
    echo -e "${GREEN}[OK] ${SUBDOMAIN} configurado${NC}"
done

echo ""

# Eliminar configuración por defecto
echo -e "${YELLOW}Eliminando configuración por defecto...${NC}"
rm -f /etc/nginx/sites-enabled/default
echo -e "${GREEN}[OK] Configuración por defecto eliminada${NC}"
echo ""

# Verificar configuración
echo -e "${YELLOW}Verificando configuración de Nginx...${NC}"
nginx -t

if [ $? -eq 0 ]; then
    echo -e "${GREEN}[OK] Configuración válida${NC}"
    echo ""
    
    # Reiniciar Nginx
    echo -e "${YELLOW}Reiniciando Nginx...${NC}"
    systemctl restart nginx
    echo -e "${GREEN}[OK] Nginx reiniciado${NC}"
else
    echo -e "${RED}[ERROR] Configuración inválida${NC}"
    exit 1
fi

echo ""
echo "======================================================="
echo -e "${GREEN}  NGINX CONFIGURADO EXITOSAMENTE${NC}"
echo "======================================================="
echo ""
echo -e "${YELLOW}Dominios configurados:${NC}"
for PROJECT in "${!PROJECTS[@]}"; do
    echo "  - ${PROJECT}.${BASE_DOMAIN}"
done
echo ""
echo -e "${YELLOW}IMPORTANTE - Configuración DNS:${NC}"
echo "Crea estos registros A en tu proveedor de DNS:"
echo ""
for PROJECT in "${!PROJECTS[@]}"; do
    echo "  ${PROJECT}.${BASE_DOMAIN}  →  $(hostname -I | awk '{print $1}')"
done
echo ""
echo -e "${YELLOW}Siguiente paso (después de configurar DNS):${NC}"
echo "Instalar certificados SSL:"
echo ""
for PROJECT in "${!PROJECTS[@]}"; do
    echo "  certbot --nginx -d ${PROJECT}.${BASE_DOMAIN}"
done
echo ""
