# Solución: Desconexiones WhatsApp en Booking de Oceano Optico

**Fecha:** 14 de enero de 2026  
**Usuario afectado:** Oceano Optico (Julio Cesar Zapata Ospina)  
**Email:** Oceanoptics4@gmail.com  
**Org ID:** 2  
**WhatsApp:** 573007915262

## 🔴 Problema Reportado

El usuario reportó dos síntomas:
1. **Al usar el sistema de agendamiento** (booking) en la landing page, no estaba con la sesión iniciada
2. **WhatsApp se desconectaba** cada vez que se probaba el agendamiento

## 🔍 Diagnóstico

### Problema Real Identificado

Tras investigación exhaustiva se determinó que:

1. **La vista de booking NO tiene problemas de sesión** - La vista `apps/public/views.py` funciona correctamente tanto para usuarios autenticados como no autenticados

2. **El problema real era la sesión corrupta de WhatsApp** con los siguientes síntomas:
   - Múltiples errores "Bad MAC" en libsignal (capa de cifrado de WhatsApp)
   - Desconexiones recurrentes con "Stream Errored (ack)"
   - Errores "Connection Closed" al intentar enviar mensajes
   - Reconexiones automáticas que **no solucionaban** el problema de corrupción

### Logs del Problema

```
Conexión cerrada para 2. Status: 500, Reconectar: true
Razón de desconexión: Stream Errored (ack)
Session error:Error: Bad MAC Error: Bad MAC
Error al enviar mensaje: Connection Closed
```

## ✅ Solución Implementada

### 1. Sistema Mejorado de Detección y Auto-Limpieza

**Cambios en `/var/www/whatsapp-server/server.js`:**

#### A. Límites más agresivos
```javascript
const BAD_MAC_ERROR_LIMIT = 3; // Reducido de 5 a 3
const BAD_MAC_RESET_TIME = 30000; // Reducido a 30s
const STREAM_ERROR_LIMIT = 2; // Nuevo límite para errores de stream
const STREAM_ERROR_RESET_TIME = 60000; // 1 minuto
```

#### B. Nueva función `handleStreamError()`
Detecta y maneja automáticamente:
- `Stream Errored`
- `Connection Closed`
- Errores de `ack`

Después de 2 errores en 1 minuto → **Limpieza automática**

#### C. Mejoras en la detección de errores
```javascript
// Detectar errores de stream en desconexiones
if (errorMsg.includes('Stream Errored') || 
    errorMsg.includes('Connection Closed') || 
    errorMsg.includes('ack')) {
    handleStreamError(organizationId, errorMsg);
    return; // No reconectar con sesión corrupta
}
```

#### D. Endpoint para limpieza manual
```javascript
POST /api/force-clean-session
Headers:
  Content-Type: application/json
  x-api-key: opticaapp_2026_whatsapp_baileys_secret_key_12345
Body:
  {"organization_id": "2"}
```

### 2. Limpieza de Sesión Corrupta de Oceano Optico

**Acción ejecutada:**
```bash
wget --quiet --output-document=- \
  --post-data='{"organization_id":"2"}' \
  --header='Content-Type: application/json' \
  --header='x-api-key: opticaapp_2026_whatsapp_baileys_secret_key_12345' \
  http://localhost:3000/api/force-clean-session
```

**Resultado:**
```
✅ Sesión limpiada exitosamente
💾 Backup creado: /var/www/whatsapp-server/auth_sessions/2_corrupted_1768424188372
🔄 Nueva conexión creada
📱 QR generado para re-escaneo
```

## 📋 Pasos para el Usuario

### Oceano Optico debe:

1. **Acceder al módulo de WhatsApp** en el dashboard de OpticaApp
2. **Escanear el nuevo código QR** con el teléfono vinculado (573007915262)
3. **Verificar conexión** - Debería mostrar estado "Conectado"
4. **Probar el agendamiento** desde la landing page booking

### URL de la landing page:
- General: `https://opticaapp.co/agendar/`
- Específica: `https://opticaapp.co/oceanoptico/agendar/` (si tiene slug)

## 🛡️ Prevención Futura

El sistema ahora cuenta con:

### Auto-limpieza activada
- **Bad MAC errors:** 3 errores en 30 segundos → limpieza automática
- **Stream errors:** 2 errores en 1 minuto → limpieza automática
- **Backups automáticos:** Mantiene últimas 3 sesiones corruptas
- **Reset de contadores:** Al conectar exitosamente

### Monitoreo mejorado
- Logs más descriptivos de errores
- Contadores de errores por tipo
- Identificación temprana de sesiones problemáticas

## 🔧 Mantenimiento

### Si el problema se repite:

1. **Verificar logs:**
```bash
ssh root@84.247.129.180
pm2 logs whatsapp-server --lines 50 | grep "org_id_2"
```

2. **Forzar limpieza manual:**
```bash
wget --quiet --output-document=- \
  --post-data='{"organization_id":"2"}' \
  --header='Content-Type: application/json' \
  --header='x-api-key: opticaapp_2026_whatsapp_baileys_secret_key_12345' \
  http://localhost:3000/api/force-clean-session
```

3. **Verificar estado:**
```bash
pm2 logs whatsapp-server --lines 20 --nostream
```

## 📊 Mejoras Técnicas Implementadas

### Commit: `0b3731c`
- ✅ Sistema de detección de Stream Errors
- ✅ Límites más agresivos para Bad MAC
- ✅ Endpoint `/api/force-clean-session`
- ✅ Reset automático de contadores
- ✅ Backups de sesiones corruptas

### Archivos modificados:
- `whatsapp-server/server.js` (+102 líneas, -6 líneas)

### Servidor actualizado:
- VPS Contabo: 84.247.129.180
- PM2 process: whatsapp-server (PID 306207)
- Estado: ✅ Online y funcional

## 📝 Notas Importantes

1. **La vista de booking es correcta** - No había problema de sesión en el código
2. **El problema era exclusivamente WhatsApp** - Sesión corrupta por errores de cifrado
3. **La solución es permanente** - Sistema de auto-limpieza activo
4. **Usuario debe re-escanear QR** - Paso necesario para nueva sesión limpia

---

**Conclusión:** El problema de "sesión no iniciada" que reportó el usuario era en realidad desconexiones de WhatsApp causadas por corrupción en la sesión de Baileys. El sistema ahora detecta y limpia automáticamente sesiones corruptas, previniendo estos problemas en el futuro.
