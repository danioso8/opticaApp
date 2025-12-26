#!/bin/bash

# Script de inicialización para Render
# Crea la estructura de carpetas necesaria en el disco persistente

echo "🔧 Inicializando disco persistente de Render..."

# Ruta del disco persistente (montado por Render)
MEDIA_PATH="${RENDER_MEDIA_PATH:-/opt/render/project/src/media_storage}"

# Crear estructura de carpetas si no existe
if [ -d "$MEDIA_PATH" ]; then
    echo "✅ Disco persistente encontrado en: $MEDIA_PATH"
    
    # Crear carpetas necesarias
    mkdir -p "$MEDIA_PATH/landing/logos"
    mkdir -p "$MEDIA_PATH/landing/hero"
    mkdir -p "$MEDIA_PATH/organizations/logos"
    mkdir -p "$MEDIA_PATH/billing/invoices"
    
    # Establecer permisos
    chmod -R 755 "$MEDIA_PATH"
    
    echo "✅ Estructura de carpetas creada"
    echo "📂 Contenido del disco:"
    ls -la "$MEDIA_PATH"
else
    echo "⚠️  Advertencia: Disco persistente no encontrado en $MEDIA_PATH"
    echo "   Si estás en Render, asegúrate de haber creado el disco en Dashboard"
    echo "   Si estás en desarrollo local, esto es normal (se usa carpeta local)"
fi

echo "✅ Inicialización completada"
