# 🛡️ Protecciones Anti-Bloqueo de WhatsApp
## Implementadas el 16 de Enero de 2026

---

## ⚠️ SITUACIÓN PREVIA
- **Problema**: Servidor bloqueado por WhatsApp (Error 515)
- **Causa**: Intentos de conexión excesivos y reconexiones automáticas agresivas
- **Impacto**: Imposibilidad total de conectar cualquier número de WhatsApp

---

## ✅ PROTECCIONES IMPLEMENTADAS

### 1. **Rate Limiting Global del Servidor**
```javascript
MAX_GLOBAL_CONNECTIONS_PER_HOUR = 3
```
- **Qué hace**: Limita todo el servidor a máximo 3 intentos de conexión por hora (total)
- **Por qué**: WhatsApp monitorea IPs con actividad excesiva
- **Efecto**: Si 3 organizaciones intentan conectar en la misma hora, la 4ta deberá esperar

### 2. **Límite Diario por Organización**
```javascript
MAX_ATTEMPTS_PER_DAY = 2
```
- **Qué hace**: Cada organización solo puede intentar conectar 2 veces en 24 horas
- **Por qué**: Prevenir intentos repetidos de la misma organización
- **Efecto**: Después de 2 intentos fallidos, la organización queda bloqueada 24 horas

### 3. **Cooldown Después de Fallo**
```javascript
COOLDOWN_AFTER_FAILURE = 2 horas
```
- **Qué hace**: Después de un intento fallido, esperar obligatoriamente 2 horas
- **Por qué**: Dar tiempo para que WhatsApp "olvide" el intento anterior
- **Efecto**: No se puede reintentar inmediatamente después de un error

### 4. **Delay Obligatorio de 30 Segundos**
```javascript
MANDATORY_DELAY_BEFORE_CONNECTION = 30 segundos
```
- **Qué hace**: Antes de CUALQUIER intento de conexión, esperar 30 segundos
- **Por qué**: Simular comportamiento humano, no automático
- **Efecto**: Cada conexión tarda mínimo 30 segundos en iniciar

### 5. **Detección de Error 515 (Crítico)**
```javascript
ERROR_515_COOLDOWN = 24 horas
```
- **Qué hace**: Si se detecta Error 515, bloquear organización por 24 horas
- **Por qué**: Error 515 = WhatsApp ya bloqueó temporalmente
- **Efecto**: Organización marcada como "bloqueada" y no puede intentar por 24 horas

### 6. **Sin Reconexión Automática**
```javascript
// ANTES: Al desconectar, reintentar automáticamente
// AHORA: Al desconectar, ESPERAR reconexión manual vía API
```
- **Qué hace**: Elimina todos los intentos automáticos de reconexión
- **Por qué**: Reconexiones automáticas causan bloqueos por actividad sospechosa
- **Efecto**: Si se pierde conexión, debe reconectarse manualmente desde la UI

### 7. **Configuración de Socket Más Conservadora**
```javascript
browser: ['Windows', 'Chrome', '120.0.0']  // Más genérico
connectTimeoutMs: 60000  // 60 segundos
keepAliveIntervalMs: 30000  // Keep-alive cada 30s
markOnlineOnConnect: false  // No marcar online automáticamente
```
- **Qué hace**: Socket se identifica de forma más genérica y estable
- **Por qué**: Evitar firmas de bot, parecer navegador normal
- **Efecto**: WhatsApp ve el servidor como cliente web normal

---

## 📊 MONITOREO Y CONTROL

### Nuevo Endpoint: `/api/rate-limit-status`

**Verificar estado global:**
```bash
curl -H "X-API-Key: opticaapp_2026_whatsapp_baileys_secret_key_12345" \
  http://84.247.129.180:3000/api/rate-limit-status
```

**Respuesta ejemplo:**
```json
{
  "global_attempts_last_hour": 2,
  "global_limit": 3,
  "global_blocked": false,
  "organizations": [
    {
      "organization_id": "2",
      "can_connect": false,
      "block_reason": "error_515_block",
      "attempts_last_24h": 2,
      "is_blocked_515": true,
      "last_failure": "2026-01-16T20:00:00Z"
    }
  ]
}
```

**Verificar organización específica:**
```bash
curl -H "X-API-Key: opticaapp_2026_whatsapp_baileys_secret_key_12345" \
  "http://84.247.129.180:3000/api/rate-limit-status?organization_id=2"
```

**Respuesta ejemplo:**
```json
{
  "global_attempts_last_hour": 1,
  "global_limit": 3,
  "global_blocked": false,
  "organization_id": "2",
  "can_connect": false,
  "block_reason": "cooldown_after_failure",
  "wait_time_minutes": 87,
  "attempts_last_24h": 1,
  "daily_limit": 2,
  "is_blocked_515": false,
  "last_failure": "2026-01-16T18:33:00Z",
  "block_until": "2026-01-16T20:33:00Z"
}
```

### Estados de Bloqueo Posibles

| Razón | Descripción | Tiempo de Espera |
|-------|-------------|------------------|
| `server_rate_limit` | Servidor alcanzó límite global | 1 hora |
| `error_515_block` | WhatsApp bloqueó con Error 515 | 24 horas |
| `daily_limit` | Organización alcanzó límite diario | 24 horas |
| `cooldown_after_failure` | Cooldown después de fallo | 2 horas |

---

## 🔄 FLUJO DE CONEXIÓN AHORA

### ANTES (Problemático):
```
1. Iniciar sesión
2. Si falla → reintentar automáticamente cada 2s
3. Si falla 3 veces → reintentar cada 5s
4. Si falla más → seguir intentando indefinidamente
❌ Resultado: WhatsApp detecta bot y bloquea servidor
```

### AHORA (Protegido):
```
1. Verificar rate limiting (¿puedo intentar?)
   ├─ Si NO → Devolver error con tiempo de espera
   └─ Si SÍ → Continuar
   
2. Esperar 30 segundos obligatorios

3. Intentar conexión

4. Si falla:
   ├─ Registrar fallo
   ├─ Activar cooldown de 2 horas
   ├─ Si es Error 515 → Bloquear 24 horas
   └─ NO reintentar automáticamente
   
5. Si desconecta:
   ├─ NO reconectar automáticamente
   ├─ Esperar reconexión manual desde UI
   └─ Registrar desconexión
```

---

## 📋 INSTRUCCIONES PARA EL LUNES 20 DE ENERO

### 1. **Verificar que pasaron 48 horas**
```bash
# Fecha/hora del bloqueo: 16 Ene 2026 ~20:00
# Fecha/hora segura para reintentar: 18 Ene 2026 20:00
# Recomendado esperar hasta: 20 Ene 2026 09:00 (lunes por la mañana)
```

### 2. **Verificar estado del servidor**
```bash
ssh root@84.247.129.180
pm2 status
# whatsapp-server debe estar STOPPED
```

### 3. **Verificar rate limiting**
```bash
curl -H "X-API-Key: opticaapp_2026_whatsapp_baileys_secret_key_12345" \
  http://84.247.129.180:3000/api/rate-limit-status
```

Debe mostrar:
```json
{
  "global_attempts_last_hour": 0,  // ← DEBE SER 0
  "global_blocked": false,           // ← DEBE SER false
  "organizations": []                // ← DEBE ESTAR VACÍO
}
```

### 4. **Limpiar sesiones antiguas (IMPORTANTE)**
```bash
ssh root@84.247.129.180
rm -rf /var/www/whatsapp-server/auth_sessions/*
echo "Sesiones limpiadas"
```

### 5. **Iniciar servidor**
```bash
pm2 start whatsapp-server
pm2 logs whatsapp-server --lines 20
```

**Verificar en logs:**
- ✅ "Servidor WhatsApp escuchando en puerto 3000"
- ✅ NO debe haber intentos de reconexión automática
- ✅ NO debe haber errores

### 6. **Intentar conectar UN SOLO número**
```bash
# Desde OpticaApp UI, intentar conectar SOLO UNA organización
# Esperar los 30 segundos obligatorios
# Escanear QR rápidamente (máximo 60 segundos)
```

**Lo que verás en logs:**
```
⏳ Esperando 30s antes de conectar 2 (protección anti-bloqueo)...
📊 Intentos org 2: 1/día, Global: 1/hora
🔐 Usando Baileys versión X.X.X
QR generado para 2
```

### 7. **Si falla el primer intento:**
```bash
# NO REINTENTAR INMEDIATAMENTE
# Esperar 2 horas completas
# Verificar rate limiting antes de reintentar:

curl -H "X-API-Key: opticaapp_2026_whatsapp_baileys_secret_key_12345" \
  "http://84.247.129.180:3000/api/rate-limit-status?organization_id=2"
```

### 8. **Si recibe Error 515 de nuevo:**
```bash
# DETENER INMEDIATAMENTE
pm2 stop whatsapp-server

# El sistema bloqueará automáticamente por 24 horas
# Considerar alternativas:
# - Opción 1: Cambiar IP del servidor (VPN/Proxy)
# - Opción 2: Nuevo servidor con IP limpia
# - Opción 3: WhatsApp Business API oficial
```

---

## 🚨 SEÑALES DE ALARMA

### SI VES ESTO, DETENER INMEDIATAMENTE:
```
🚨🚨🚨 ERROR 515 DETECTADO
stream:error code 515
Connection Failure (401)
```

### Acción inmediata:
```bash
pm2 stop whatsapp-server
```

---

## 📈 MÉTRICAS DE ÉXITO

### Indicadores de que está funcionando bien:
- ✅ Conexión exitosa al primer intento
- ✅ QR se genera después de 30 segundos
- ✅ Sin errores 515 en logs
- ✅ Sin reconexiones automáticas
- ✅ Sesión estable por más de 24 horas

### Indicadores de problemas:
- ❌ Error 515 aparece
- ❌ Múltiples desconexiones
- ❌ QR expira antes de escanear
- ❌ Error 401 repetitivo

---

## 💾 BACKUP Y ROLLBACK

### Backup creado:
```
/var/www/whatsapp-server/server.js.backup_antes_proteccion
```

### Para revertir cambios (NO RECOMENDADO):
```bash
ssh root@84.247.129.180
cd /var/www/whatsapp-server
cp server.js.backup_antes_proteccion server.js
pm2 restart whatsapp-server
```

---

## 📚 REFERENCIAS TÉCNICAS

### Constantes de Protección:
```javascript
MAX_ATTEMPTS_PER_DAY = 2                     // Intentos/día por org
COOLDOWN_AFTER_FAILURE = 7200000            // 2 horas en ms
MANDATORY_DELAY_BEFORE_CONNECTION = 30000   // 30 segundos en ms
ERROR_515_COOLDOWN = 86400000               // 24 horas en ms
MAX_GLOBAL_CONNECTIONS_PER_HOUR = 3         // Intentos/hora servidor
```

### Funciones Clave:
- `canAttemptConnection(orgId)` - Valida si puede intentar conexión
- `recordConnectionAttempt(orgId, success)` - Registra intento
- `markAsBlocked515(orgId)` - Marca como bloqueado por Error 515

---

## 📞 PLAN DE CONTINGENCIA

### Si el lunes sigue bloqueado:

**Opción A: Esperar 1 semana**
- Costo: $0
- Tiempo: 7 días
- Probabilidad de éxito: 95%

**Opción B: Cambiar IP con Proxy**
- Costo: $5-10/mes
- Tiempo: 2-4 horas
- Probabilidad de éxito: 70%
- Riesgo: Puede violar ToS de WhatsApp

**Opción C: Nuevo Servidor**
- Costo: $5-10/mes
- Tiempo: 4-8 horas
- Probabilidad de éxito: 95%
- Ventaja: IP limpia garantizada

**Opción D: WhatsApp Business API Oficial**
- Costo: $0.005-0.05 por mensaje
- Tiempo: 1-2 semanas (aprobación)
- Probabilidad de éxito: 100%
- Ventaja: Soporte oficial, sin bloqueos

---

## ✅ CHECKLIST PARA EL LUNES

- [ ] Han pasado mínimo 48 horas (idealmente 60 horas)
- [ ] Servidor está STOPPED
- [ ] Sesiones antiguas limpiadas (`auth_sessions/*`)
- [ ] Rate limiting muestra 0 intentos globales
- [ ] Código actualizado con protecciones
- [ ] Plan B preparado por si falla
- [ ] Solo intentar con UNA organización
- [ ] Tener QR listo para escanear en <60s
- [ ] Monitorear logs en tiempo real
- [ ] No reintentar si falla (esperar 2 horas)

---

**Última actualización**: 16 de Enero de 2026, 20:30
**Estado**: Servidor STOPPED esperando 48 horas
**Próxima acción**: Lunes 20 de Enero de 2026, 09:00
