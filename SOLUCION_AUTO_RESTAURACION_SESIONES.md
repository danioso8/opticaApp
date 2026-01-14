# Solución: Auto-Restauración de Sesiones WhatsApp

## Problema Detectado

Cuando un usuario escaneaba el código QR y creaba una nueva sesión de WhatsApp, si el servidor se reiniciaba poco después, la nueva sesión NO se restauraba automáticamente. Esto causaba que el usuario tuviera que volver a escanear el código QR.

### Causa Raíz

El servidor WhatsApp solo detectaba y restauraba las sesiones que **existían al momento de iniciar**. Si una sesión se creaba después del inicio del servidor (por ejemplo, al escanear un QR), esa sesión se guardaba en archivos pero no se agregaba a la lista de sesiones activas en memoria. Al reiniciar el servidor, no se cargaba automáticamente.

**Cronología del problema:**
1. Servidor inicia a las 00:50 → Detecta solo sesión de org 4
2. Usuario escanea QR a las 03:35 → Se crea sesión para org 2 en archivos
3. Servidor se reinicia a las 03:29 (antes del escaneo) → Solo restaura org 4
4. Usuario escanea QR a las 03:35 → Sesión creada pero no cargada en memoria
5. Servidor NO restaura org 2 porque la sesión fue creada después del inicio

## Solución Implementada

### 1. Función de Auto-Detección (`checkForNewSessions`)

Se agregó una nueva función que verifica periódicamente si hay sesiones guardadas en archivos que no están cargadas en memoria:

```javascript
async function checkForNewSessions() {
    try {
        const organizations = fs.readdirSync(AUTH_DIR);
        
        for (const orgId of organizations) {
            // Si ya existe una sesión activa para esta org, saltarla
            if (sessions.has(orgId)) {
                continue;
            }

            const authPath = path.join(AUTH_DIR, orgId);
            const credsPath = path.join(authPath, 'creds.json');
            
            // Si existe creds.json pero no hay sesión cargada, restaurarla
            if (fs.existsSync(credsPath)) {
                logger.info(`🔄 Nueva sesión detectada para ${orgId}, restaurando...`);
                
                sessions.set(orgId, {
                    sock: null,
                    qr: null,
                    status: 'restoring',
                    retryCount: 0
                });

                const sock = await createWhatsAppConnection(orgId);
                sessions.get(orgId).sock = sock;
                
                logger.info(`✅ Sesión restaurada automáticamente para ${orgId}`);
            }
        }
    } catch (error) {
        logger.error(`Error verificando nuevas sesiones: ${error.message}`);
    }
}
```

### 2. Verificación Periódica Automática

Se configuró un intervalo que ejecuta la verificación cada 30 segundos:

```javascript
app.listen(PORT, async () => {
    logger.info(`🚀 Servidor WhatsApp iniciado en puerto ${PORT}`);
    logger.info(`📱 API Key: ${API_KEY}`);
    logger.info(`📂 Sesiones guardadas en: ${AUTH_DIR}`);
    
    // Restaurar sesiones existentes
    await restoreExistingSessions();
    
    // Verificar cada 30 segundos si hay nuevas sesiones guardadas que no están cargadas
    setInterval(async () => {
        await checkForNewSessions();
    }, 30000); // 30 segundos
    
    logger.info('🔍 Auto-detección de nuevas sesiones activada (cada 30 segundos)');
});
```

## Beneficios de la Solución

### ✅ Recuperación Automática
- Si se crea una nueva sesión (escaneo de QR), se detecta automáticamente en máximo 30 segundos
- No requiere reiniciar manualmente el servidor
- No requiere intervención del usuario

### ✅ Tolerancia a Fallos
- Si el servidor se reinicia poco después de crear una sesión, la sesión se restaura automáticamente
- Protege contra pérdida de sesiones por reinicios programados o inesperados
- Sincronización constante entre archivos y memoria

### ✅ Experiencia de Usuario Mejorada
- El usuario solo necesita escanear el código QR una vez
- La sesión persiste incluso con reinicios frecuentes del servidor
- Reduce significativamente los casos donde se requiere re-escanear QR

## Verificación de la Solución

### Logs del Servidor
Al iniciar, se verá:
```
🚀 Servidor WhatsApp iniciado en puerto 3000
📱 API Key: opticaapp_2026_whatsapp_baileys_secret_key_12345
📂 Sesiones guardadas en: /var/www/whatsapp-server/auth_sessions
Restaurando 2 sesiones existentes...
Restaurando sesión para 2
Restaurando sesión para 4
Restauración de sesiones completada
🔍 Auto-detección de nuevas sesiones activada (cada 30 segundos)
✅ WhatsApp conectado exitosamente para 2
📱 Número conectado: 573007915262
✅ WhatsApp conectado exitosamente para 4
📱 Número conectado: 573126809496
```

### Cuando se Detecta una Nueva Sesión
```
🔄 Nueva sesión detectada para {orgId}, restaurando...
✅ Sesión restaurada automáticamente para {orgId}
```

## Configuración

### Ajustar el Intervalo de Verificación
Por defecto está configurado en 30 segundos. Para modificarlo:

```javascript
// En server.js, línea ~437
setInterval(async () => {
    await checkForNewSessions();
}, 30000); // Cambiar 30000 a los milisegundos deseados
```

**Recomendaciones:**
- 30 segundos (30000 ms) - Balance óptimo entre rapidez y recursos
- 60 segundos (60000 ms) - Para servidores con recursos limitados
- 15 segundos (15000 ms) - Para máxima rapidez de detección

## Casos de Uso Resueltos

### Caso 1: Usuario Escanea QR y Servidor se Reinicia
1. Usuario escanea código QR → Sesión creada en archivos
2. Servidor se reinicia → Auto-detección activa
3. En máximo 30 segundos → Sesión restaurada automáticamente
4. Usuario NO necesita re-escanear

### Caso 2: Sesión Perdida por Crash del Servidor
1. Servidor tiene crash inesperado
2. Al reiniciar → Restaura todas las sesiones guardadas
3. Auto-detección verifica que todas las sesiones estén cargadas
4. Sesiones funcionan sin intervención

### Caso 3: Múltiples Organizaciones
1. Org 1 escanea QR a las 10:00
2. Servidor reinicia a las 10:15
3. Org 2 escanea QR a las 10:30
4. Org 1 se restaura al inicio (10:15)
5. Org 2 se restaura automáticamente (10:30 + máx 30 seg)
6. Ambas organizaciones funcionan sin re-escanear

## Archivos Modificados

### `/var/www/whatsapp-server/server.js`
- ✅ Agregada función `checkForNewSessions()`
- ✅ Agregado intervalo de verificación automática
- ✅ Logs informativos de auto-detección

## Monitoreo

### Ver Logs en Tiempo Real
```bash
pm2 logs whatsapp-server
```

### Ver Estado de Sesiones
```bash
ssh root@84.247.129.180 "ls -la /var/www/whatsapp-server/auth_sessions/"
```

### Verificar Estado en Base de Datos
```bash
cd /var/www/opticaapp
source venv/bin/activate
python sync_whatsapp_connections.py
```

## Fecha de Implementación
**14 de Enero de 2026**

## Estado
✅ **IMPLEMENTADO Y ACTIVO EN PRODUCCIÓN**

## Próximos Pasos (Opcional)

### Mejoras Futuras Sugeridas
1. **Webhook de Notificación**: Agregar webhook que notifique a Django inmediatamente cuando se crea una nueva sesión
2. **Sincronización Bidireccional**: Permitir que Django active la restauración desde el backend
3. **Dashboard de Monitoreo**: Crear interfaz para ver estado de sesiones en tiempo real
4. **Alertas Automáticas**: Enviar notificación si una sesión no se puede restaurar después de varios intentos

---

**Autor:** Sistema de Auto-Corrección OpticaApp  
**Versión:** 1.0  
**Última Actualización:** 14 de Enero de 2026
