#!/bin/bash
# Script para limpiar y reconectar la sesión de WhatsApp corrupta

echo "🔧 Limpiando sesión corrupta de WhatsApp..."

# 1. Detener el servidor de WhatsApp
echo "⏹️  Deteniendo servidor WhatsApp..."
pm2 stop whatsapp-server

# 2. Hacer backup de la sesión actual (por si acaso)
echo "💾 Haciendo backup de sesión actual..."
BACKUP_DIR="/var/www/whatsapp-server/auth_sessions_backup_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
cp -r /var/www/whatsapp-server/auth_sessions/2 "$BACKUP_DIR/" 2>/dev/null || echo "No hay sesión para respaldar"

# 3. Eliminar la sesión corrupta
echo "🗑️  Eliminando sesión corrupta..."
rm -rf /var/www/whatsapp-server/auth_sessions/2

# 4. Reiniciar el servidor de WhatsApp
echo "🔄 Reiniciando servidor WhatsApp..."
pm2 restart whatsapp-server

# 5. Ver logs
echo "📋 Viendo logs (presiona Ctrl+C para salir)..."
sleep 2
pm2 logs whatsapp-server --lines 30

echo ""
echo "✅ Sesión limpiada. Ahora debes:"
echo "   1. Ir a la aplicación OpticaApp"
echo "   2. Ir a Configuración > WhatsApp"
echo "   3. Escanear el nuevo código QR que aparecerá"
echo "   4. Asegurarte de cerrar WhatsApp Web en otros dispositivos"
