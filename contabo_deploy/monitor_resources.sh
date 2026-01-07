#!/bin/bash

# Script de monitoreo de recursos del servidor
# Ejecutar cada hora: 0 * * * * /root/monitor_resources.sh

# Configuración
ALERT_EMAIL="tu@email.com"  # Cambiar por tu email
CPU_THRESHOLD=80
RAM_THRESHOLD=80
DISK_THRESHOLD=80

LOG_FILE="/var/log/monitor_resources.log"

# Obtener uso de CPU
CPU_USAGE=$(top -bn1 | grep "Cpu(s)" | awk '{print $2}' | cut -d'%' -f1 | cut -d'.' -f1)

# Obtener uso de RAM
RAM_USAGE=$(free | grep Mem | awk '{print int($3/$2 * 100)}')

# Obtener uso de disco
DISK_USAGE=$(df -h / | tail -1 | awk '{print $5}' | cut -d'%' -f1)

# Timestamp
TIMESTAMP=$(date "+%Y-%m-%d %H:%M:%S")

# Registrar en log
echo "$TIMESTAMP - CPU: ${CPU_USAGE}% | RAM: ${RAM_USAGE}% | DISK: ${DISK_USAGE}%" >> $LOG_FILE

# Función para enviar alerta
send_alert() {
    SUBJECT="$1"
    MESSAGE="$2"
    
    echo "$MESSAGE" | mail -s "$SUBJECT" $ALERT_EMAIL 2>/dev/null || true
}

# Verificar umbrales y enviar alertas
ALERT_MSG=""

if [ $CPU_USAGE -gt $CPU_THRESHOLD ]; then
    ALERT_MSG="${ALERT_MSG}\nCPU: ${CPU_USAGE}% (Umbral: ${CPU_THRESHOLD}%)"
fi

if [ $RAM_USAGE -gt $RAM_THRESHOLD ]; then
    ALERT_MSG="${ALERT_MSG}\nRAM: ${RAM_USAGE}% (Umbral: ${RAM_THRESHOLD}%)"
fi

if [ $DISK_USAGE -gt $DISK_THRESHOLD ]; then
    ALERT_MSG="${ALERT_MSG}\nDISCO: ${DISK_USAGE}% (Umbral: ${DISK_THRESHOLD}%)"
fi

# Enviar alerta si hay problemas
if [ ! -z "$ALERT_MSG" ]; then
    FULL_MESSAGE="ALERTA: Recursos del servidor exceden umbrales\n\n$ALERT_MSG\n\nServidor: $(hostname)\nFecha: $TIMESTAMP"
    send_alert "⚠️ Alerta de Recursos - $(hostname)" "$FULL_MESSAGE"
fi

# Verificar servicios críticos
SERVICES=("nginx" "postgresql" "pm2")

for SERVICE in "${SERVICES[@]}"; do
    if [ "$SERVICE" = "pm2" ]; then
        # PM2 no es un servicio systemd, verificar proceso
        if ! pgrep -x "PM2" > /dev/null; then
            send_alert "⚠️ Servicio caído - PM2" "PM2 no está corriendo en $(hostname)"
            echo "$TIMESTAMP - ALERTA: PM2 no está corriendo" >> $LOG_FILE
        fi
    else
        if ! systemctl is-active --quiet $SERVICE; then
            send_alert "⚠️ Servicio caído - $SERVICE" "$SERVICE no está corriendo en $(hostname)"
            echo "$TIMESTAMP - ALERTA: $SERVICE no está corriendo" >> $LOG_FILE
        fi
    fi
done

# Limpiar log si es muy grande (mantener últimos 1000 líneas)
if [ -f "$LOG_FILE" ]; then
    LINE_COUNT=$(wc -l < "$LOG_FILE")
    if [ $LINE_COUNT -gt 1000 ]; then
        tail -n 1000 "$LOG_FILE" > "${LOG_FILE}.tmp"
        mv "${LOG_FILE}.tmp" "$LOG_FILE"
    fi
fi
