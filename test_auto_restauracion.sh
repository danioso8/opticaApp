#!/bin/bash
# Script de prueba para verificar la auto-restauración de sesiones

echo "======================================================"
echo "🧪 PRUEBA: Auto-Restauración de Sesiones WhatsApp"
echo "======================================================"
echo ""

# Función para esperar un tiempo y mostrar contador
wait_with_countdown() {
    local seconds=$1
    local message=$2
    echo "$message"
    for i in $(seq $seconds -1 1); do
        echo -ne "\rEsperando ${i} segundos...   "
        sleep 1
    done
    echo -e "\r✅ Listo                    "
    echo ""
}

# Paso 1: Verificar estado inicial
echo "📊 Paso 1: Estado inicial de sesiones"
echo "------------------------------------------------------"
curl -s -X GET http://localhost:3000/status \
  -H "x-api-key: opticaapp_2026_whatsapp_baileys_secret_key_12345" | python3 -m json.tool
echo ""

# Paso 2: Listar sesiones en archivos
echo "📁 Paso 2: Sesiones guardadas en archivos"
echo "------------------------------------------------------"
ls -1 /var/www/whatsapp-server/auth_sessions/
echo ""

# Paso 3: Esperar el ciclo de verificación (30 segundos)
wait_with_countdown 35 "⏱️  Paso 3: Esperando ciclo de auto-detección (30 seg + margen)"

# Paso 4: Verificar que todas las sesiones están cargadas
echo "🔍 Paso 4: Verificar sesiones después del ciclo"
echo "------------------------------------------------------"
curl -s -X GET http://localhost:3000/status \
  -H "x-api-key: opticaapp_2026_whatsapp_baileys_secret_key_12345" | python3 -m json.tool
echo ""

# Paso 5: Verificar logs recientes
echo "📋 Paso 5: Últimos logs del servidor"
echo "------------------------------------------------------"
pm2 logs whatsapp-server --lines 20 --nostream | grep -E "Nueva sesión detectada|Auto-detección|Sesión restaurada|conectado exitosamente" || echo "No se detectaron nuevas sesiones (esto es normal si todas ya estaban cargadas)"
echo ""

echo "======================================================"
echo "✅ PRUEBA COMPLETADA"
echo "======================================================"
echo ""
echo "💡 Interpretación de resultados:"
echo "  - Si ves '🔄 Nueva sesión detectada': La auto-detección funcionó"
echo "  - Si todas las sesiones muestran 'connected': Todo funciona correctamente"
echo "  - Si no ves mensajes de detección: Las sesiones ya estaban cargadas (OK)"
