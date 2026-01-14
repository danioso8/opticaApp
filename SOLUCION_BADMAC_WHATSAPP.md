# Solución: Auto-Limpieza de Sesiones WhatsApp Corruptas

## 🔴 Problema Identificado

El servidor WhatsApp presenta **errores recurrentes "Bad MAC Error"** que indican:
- Sesiones de cifrado corruptas
- Conflicto con otra conexión activa del mismo número (WhatsApp Web, otro dispositivo)
- Claves de sesión desincronizadas

**Síntomas:**
- Desconexiones constantes de WhatsApp
- Mensajes "Failed to decrypt message with any known session"
- Reconexiones automáticas que fallan repetidamente
- Usuario reporta que "se desconecta y se conecta" constantemente

**Logs del problema:**
```
Session error:Error: Bad MAC Error: Bad MAC
Closing open session in favor of incoming prekey bundle
Failed to decrypt message with any known session...
Connection Closed
```

---

## ✅ Solución Implementada

### 1. **Sistema de Detección Automática**

Se agregó un sistema que:
- Monitorea errores "Bad MAC" en tiempo real
- Cuenta cuántos errores ocurren por organización
- Resetea el contador si pasa 1 minuto sin errores

```javascript
// Límites configurables
const BAD_MAC_ERROR_LIMIT = 5;        // Máximo de errores antes de limpiar
const BAD_MAC_RESET_TIME = 60000;     // 1 minuto para resetear contador
```

### 2. **Limpieza Automática de Sesiones Corruptas**

Cuando se alcanzan 5 errores "Bad MAC" en menos de 1 minuto:

1. **Cierra el socket corrupto**
2. **Respalda la sesión corrupta** (mantiene últimos 3 backups)
3. **Elimina archivos de sesión corruptos**
4. **Crea una nueva conexión limpia**
5. **Genera nuevo código QR automáticamente**

```javascript
async function clearCorruptedSession(organizationId) {
    // 1. Cerrar socket
    await session.sock.end();
    
    // 2. Backup de sesión corrupta
    const backupPath = `${organizationId}_corrupted_${Date.now()}`;
    fs.renameSync(authPath, backupPath);
    
    // 3. Resetear sesión en memoria
    sessions.set(organizationId, { status: 'qr_required' });
    
    // 4. Crear nueva conexión
    setTimeout(() => createWhatsAppConnection(organizationId), 2000);
}
```

### 3. **Detección en Múltiples Puntos**

El sistema detecta errores Bad MAC en:

- **connection.update events**: Al desconectarse
- **Socket events interceptados**: Durante operación normal
- **Mensajes de error**: En logs de descifrado

### 4. **Nuevo Endpoint Manual**

Se agregó endpoint para limpiar sesiones manualmente:

```bash
POST /api/clear-corrupted-session
Headers: x-api-key: <API_KEY>
Body: {
  "organization_id": "2"
}
```

---

## 🚀 Despliegue de la Solución

### Opción A: Despliegue Completo (Recomendado)

```bash
# 1. Copiar archivo actualizado al servidor
scp whatsapp-server/server.js root@84.247.129.180:/var/www/whatsapp-server/

# 2. Reiniciar servidor WhatsApp
ssh root@84.247.129.180 "pm2 restart whatsapp-server"

# 3. Verificar logs
ssh root@84.247.129.180 "pm2 logs whatsapp-server --lines 50"
```

### Opción B: Limpieza Manual Inmediata (Solución Rápida)

Si necesitas solucionar el problema **ahora mismo** sin actualizar el código:

```bash
# Ejecutar script de limpieza manual
bash fix_whatsapp_session.sh
```

El script:
1. Detiene el servidor WhatsApp
2. Respalda la sesión actual
3. Elimina archivos corruptos
4. Reinicia el servidor
5. Muestra logs en tiempo real

**Después de ejecutar:**
- El usuario debe ir a OpticaApp → Configuración → WhatsApp
- Escanear el nuevo código QR
- ⚠️ **IMPORTANTE**: Cerrar WhatsApp Web en otros dispositivos

---

## 📊 Monitoreo de la Solución

### Logs a Revisar

```bash
# Ver logs del servidor WhatsApp
ssh root@84.247.129.180 "pm2 logs whatsapp-server --lines 100"
```

**Logs de éxito:**
```
⚠️  Bad MAC Error #1 para 2
⚠️  Bad MAC Error #2 para 2
...
🔴 Límite de errores Bad MAC alcanzado para 2. Limpiando sesión corrupta...
💾 Respaldando sesión corrupta en auth_sessions/2_corrupted_1736865432123
✨ Sesión limpiada para 2. Se requiere escanear QR nuevamente.
🔄 Creando nueva conexión para 2...
QR generado para 2
```

### Estados de Sesión

```javascript
// Estado de sesiones en memoria
{
  sock: <Socket>,
  qr: <Base64String>,
  status: 'connected' | 'disconnected' | 'qr_required' | 'restoring',
  retryCount: 0,
  badMacErrors: {
    count: 0,
    lastError: 1736865432123,
    resetTimeout: <TimeoutId>
  }
}
```

---

## 🔧 Configuración Avanzada

### Ajustar Sensibilidad

En [server.js](server.js#L24-L25):

```javascript
const BAD_MAC_ERROR_LIMIT = 5;        // Menos = más agresivo
const BAD_MAC_RESET_TIME = 60000;     // Más tiempo = más tolerante
```

**Recomendaciones:**
- **Producción estable**: `BAD_MAC_ERROR_LIMIT = 5`, `BAD_MAC_RESET_TIME = 60000`
- **Muchas desconexiones**: `BAD_MAC_ERROR_LIMIT = 3`, `BAD_MAC_RESET_TIME = 30000`
- **Red inestable**: `BAD_MAC_ERROR_LIMIT = 10`, `BAD_MAC_RESET_TIME = 120000`

### Limpiar Backups Antiguos

Los backups se limpian automáticamente (se mantienen últimos 3).

Manual:
```bash
ssh root@84.247.129.180 "rm -rf /var/www/whatsapp-server/auth_sessions/*_corrupted_*"
```

---

## 🎯 Prevención de Problemas Futuros

### 1. **Una Sola Conexión Activa**
El usuario debe tener **solo UNA** conexión de WhatsApp activa:
- ✅ OpticaApp en servidor
- ❌ WhatsApp Web en navegador
- ❌ Otra instancia de la app

### 2. **Notificar al Usuario**
Cuando se detecte limpieza automática, enviar notificación:

```python
# En Django (apps/notifications/whatsapp_monitor.py)
from apps.notifications.utils import send_email

def notify_whatsapp_disconnection(organization):
    send_email(
        to=organization.owner.email,
        subject="WhatsApp Desconectado - Acción Requerida",
        body=f"""
        Tu conexión de WhatsApp se desconectó por problemas de sesión.
        
        Por favor:
        1. Ve a Configuración → WhatsApp
        2. Escanea el nuevo código QR
        3. Cierra WhatsApp Web en otros dispositivos
        """
    )
```

### 3. **Webhook de Estado**
Agregar webhook para notificar cambios de estado:

```javascript
// En server.js, después de limpiar sesión
await notifyDjangoApp(organizationId, {
    event: 'session_cleared',
    reason: 'bad_mac_errors',
    timestamp: Date.now()
});
```

---

## 📈 Métricas de Éxito

Después de implementar la solución, verificar:

✅ **Indicadores de éxito:**
- Menos de 1 limpieza de sesión por día por organización
- Reconexiones exitosas en menos de 5 minutos
- No más de 3 errores Bad MAC consecutivos
- Logs sin "Connection Closed" después de reconexión

⚠️ **Señales de problemas persistentes:**
- Limpiezas de sesión cada menos de 1 hora
- Más de 10 errores Bad MAC por sesión
- Usuario reporta que el QR no aparece

Si los problemas persisten, investigar:
1. ¿El número está conectado en otro dispositivo?
2. ¿Hay problemas de red/firewall?
3. ¿WhatsApp bloqueó el número por uso comercial?

---

## 🔗 Referencias

- **Baileys Documentation**: https://whiskeysockets.github.io/
- **Bad MAC Error**: Error de autenticación de mensaje, indica claves de sesión incorrectas
- **PM2 Monitoring**: `pm2 monit` para ver uso de recursos en tiempo real

---

## 👤 Información del Usuario Afectado

**Organización:** Oceano Optico (ID: 2)  
**Número WhatsApp:** 573007915262  
**Email:** Oceanoptics4@gmail.com  
**Plan:** Profesional (con acceso a WhatsApp)

**Acción inmediata recomendada:**
1. Ejecutar `fix_whatsapp_session.sh` para limpiar sesión actual
2. Usuario debe escanear nuevo QR
3. Verificar que no hay WhatsApp Web activo
4. Desplegar versión actualizada del servidor para prevención automática
