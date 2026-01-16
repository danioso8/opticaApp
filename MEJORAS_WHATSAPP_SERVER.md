# Mejoras y Mitigación de Errores - Servidor WhatsApp (Baileys)

## Resumen de Investigación

Basado en la investigación de issues de Baileys y mejores prácticas de la comunidad, he identificado las siguientes mejoras críticas para nuestro servidor de WhatsApp.

---

## 1. ERROR 515 - Stream Error (Rate Limiting)

### Causa Principal
El error 515 es un **rate limit de WhatsApp** que ocurre cuando:
- Se hacen demasiados intentos de conexión en corto tiempo
- WhatsApp detecta comportamiento automatizado sospechoso
- El número ha sido marcado temporalmente por múltiples escaneos de QR fallidos

### Soluciones Implementadas ✅
1. **Delay de 5 minutos** después del error 515 antes de reintentar
2. Actualización a **Baileys 7.0.0-rc.9** (última versión)
3. Configuración simplificada del socket

### Mejoras Adicionales Recomendadas

```javascript
// 1. IMPLEMENTAR RATE LIMITING POR ORGANIZACIÓN
const connectionAttempts = new Map(); // organizationId -> { count, firstAttempt }

function canAttemptConnection(organizationId) {
    const now = Date.now();
    const attempts = connectionAttempts.get(organizationId) || { count: 0, firstAttempt: now };
    
    // Permitir máximo 3 intentos en 30 minutos
    if (now - attempts.firstAttempt > 1800000) {
        connectionAttempts.set(organizationId, { count: 1, firstAttempt: now });
        return true;
    }
    
    if (attempts.count >= 3) {
        logger.warn(`Rate limit alcanzado para ${organizationId}. Esperar 30 minutos.`);
        return false;
    }
    
    attempts.count++;
    connectionAttempts.set(organizationId, attempts);
    return true;
}

// 2. IMPLEMENTAR BACKOFF EXPONENCIAL MÁS AGRESIVO
function getReconnectionDelay(retryCount, errorCode) {
    if (errorCode === 515) {
        // Para error 515, usar delays mucho más largos
        return Math.min(300000 * Math.pow(2, retryCount), 3600000); // 5min, 10min, 20min, max 1 hora
    }
    // Para otros errores, backoff normal
    return Math.min(1000 * Math.pow(2, retryCount), 30000);
}

// 3. LIMPIAR SESIONES CORRUPTAS MÁS AGRESIVAMENTE
function shouldClearSession(organizationId) {
    const session = sessions.get(organizationId);
    if (!session) return false;
    
    // Si hay más de 3 errores 515 en 1 hora, limpiar sesión completamente
    if (session.error515Count > 3) {
        logger.error(`Demasiados errores 515 para ${organizationId}. Limpiando sesión.`);
        return true;
    }
    
    return false;
}
```

---

## 2. Gestión de Sesiones Mejorada

### Problemas Identificados
- Las sesiones se corrompen fácilmente con Bad MAC errors
- No hay validación de integridad de credenciales guardadas
- Socket WebSocket se desconecta inesperadamente

### Mejoras Recomendadas

```javascript
// 1. VALIDAR CREDENCIALES ANTES DE USARLAS
async function validateStoredCredentials(organizationId) {
    const authPath = path.join(AUTH_DIR, organizationId);
    const credsPath = path.join(authPath, 'creds.json');
    
    try {
        if (!fs.existsSync(credsPath)) return false;
        
        const creds = JSON.parse(fs.readFileSync(credsPath, 'utf-8'));
        
        // Verificar que tenga los campos esenciales
        if (!creds.me || !creds.me.id || !creds.noiseKey) {
            logger.warn(`Credenciales incompletas para ${organizationId}`);
            return false;
        }
        
        return true;
    } catch (error) {
        logger.error(`Error validando credenciales de ${organizationId}: ${error.message}`);
        return false;
    }
}

// 2. IMPLEMENTAR HEALTH CHECK DEL SOCKET
setInterval(() => {
    for (const [orgId, session] of sessions.entries()) {
        if (session.status === 'connected' && session.sock) {
            // Verificar si el socket está realmente vivo
            if (!session.sock.user || session.sock.ws?.readyState !== 1) {
                logger.warn(`Socket muerto detectado para ${orgId}, reconectando...`);
                session.status = 'disconnected';
                createWhatsAppConnection(orgId);
            }
        }
    }
}, 60000); // Cada minuto

// 3. KEEP-ALIVE MEJORADO
function setupKeepAlive(sock, organizationId) {
    const keepAliveInterval = setInterval(async () => {
        try {
            // Enviar ping para mantener conexión viva
            if (sock.ws?.readyState === 1) {
                await sock.query({
                    tag: 'iq',
                    attrs: {
                        to: '@s.whatsapp.net',
                        type: 'get',
                        xmlns: 'w:p'
                    }
                });
                logger.debug(`Keep-alive enviado para ${organizationId}`);
            }
        } catch (error) {
            logger.warn(`Error en keep-alive para ${organizationId}: ${error.message}`);
        }
    }, 30000); // Cada 30 segundos
    
    // Guardar referencia para limpiar después
    sessions.get(organizationId).keepAliveInterval = keepAliveInterval;
}
```

---

## 3. Configuración Óptima del Socket

### Investigación de Issues de Baileys
Según issues #2094, #2040, #1769, la configuración debe ser minimalista:

```javascript
const sock = makeWASocket({
    version,
    logger: pino({ level: 'error' }), // Solo errores en producción
    printQRInTerminal: false,
    auth: state,
    getMessage: async () => undefined,
    
    // CONFIGURACIÓN CRÍTICA
    browser: ['OpticaApp', 'Chrome', '120.0.0'], // Identificarse como navegador conocido
    syncFullHistory: false, // NUNCA sincronizar historial completo
    markOnlineOnConnect: false, // No marcar como online automáticamente
    
    // MANEJO DE ERRORES
    shouldIgnoreJid: jid => {
        // Ignorar JIDs problemáticos que causan errores de descifrado
        return jid?.includes('broadcast') || jid?.includes('newsletter');
    },
    
    // PERFORMANCE
    generateHighQualityLinkPreview: false,
    linkPreviewImageThumbnailWidth: 192,
    transactionOpts: {
        maxCommitRetries: 10,
        delayBetweenTriesMs: 3000
    },
    
    // EVITAR ERRORES DE RECIBO
    getMessage: async (key) => {
        // No enviar recibos para mensajes de broadcast/newsletter
        if (key.remoteJid?.includes('broadcast') || key.remoteJid?.includes('newsletter')) {
            return undefined;
        }
        return undefined;
    }
});
```

---

## 4. Manejo de Errores Específicos

### Bad MAC Errors (Issue #1769)

```javascript
sock.ev.on('messages.upsert', async ({ messages }) => {
    for (const msg of messages) {
        try {
            // Intentar procesar mensaje
            await handleMessage(msg);
        } catch (error) {
            if (error.message?.includes('Bad MAC') || 
                error.message?.includes('decrypt')) {
                logger.warn(`Mensaje con Bad MAC ignorado de ${msg.key.remoteJid}`);
                // NO cerrar la sesión, solo ignorar el mensaje
                continue;
            }
            throw error;
        }
    }
});
```

### Connection Failure Handling

```javascript
sock.ev.on('connection.update', async (update) => {
    const { connection, lastDisconnect, qr } = update;
    
    if (connection === 'close') {
        const statusCode = lastDisconnect?.error?.output?.statusCode;
        const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
        
        // MANEJO ESPECÍFICO POR CÓDIGO DE ERROR
        switch (statusCode) {
            case 515: // Rate limit
                logger.error(`Error 515: Rate limit. Esperar ${5 * 60000}ms`);
                setTimeout(() => createWhatsAppConnection(organizationId), 300000);
                break;
                
            case 401: // No autorizado - credenciales inválidas
                logger.error(`Error 401: Credenciales inválidas. Limpiando sesión.`);
                await clearCorruptedSession(organizationId);
                break;
                
            case 428: // Conexión perdida
                logger.warn(`Error 428: Conexión perdida. Reintentando en 10s`);
                setTimeout(() => createWhatsAppConnection(organizationId), 10000);
                break;
                
            case 408: // QR timeout
                logger.info(`Error 408: QR expiró. Generando nuevo QR.`);
                createWhatsAppConnection(organizationId);
                break;
                
            case 440: // Sesión reemplazada
                logger.warn(`Error 440: Sesión reemplazada por otro dispositivo`);
                session.status = 'qr_required';
                break;
                
            default:
                if (shouldReconnect) {
                    logger.warn(`Desconexión con código ${statusCode}. Reconectando...`);
                    createWhatsAppConnection(organizationId);
                }
        }
    }
});
```

---

## 5. Monitoreo y Logging Mejorado

```javascript
// 1. MÉTRICAS DE SALUD
const metrics = {
    connections: new Map(), // orgId -> { connectedAt, disconnects, errors }
    
    recordConnection(orgId) {
        const metric = this.connections.get(orgId) || { disconnects: 0, errors: [] };
        metric.connectedAt = Date.now();
        this.connections.set(orgId, metric);
    },
    
    recordDisconnect(orgId, reason) {
        const metric = this.connections.get(orgId);
        if (metric) {
            metric.disconnects++;
            metric.lastDisconnect = { reason, at: Date.now() };
        }
    },
    
    getHealth(orgId) {
        const metric = this.connections.get(orgId);
        if (!metric) return 'unknown';
        
        const uptime = Date.now() - metric.connectedAt;
        const disconnectRate = metric.disconnects / (uptime / 3600000); // por hora
        
        if (disconnectRate > 5) return 'unhealthy';
        if (disconnectRate > 2) return 'degraded';
        return 'healthy';
    }
};

// 2. ENDPOINT DE DIAGNÓSTICO
app.get('/api/diagnostics', authenticateAPI, (req, res) => {
    const diagnostics = {
        server: {
            uptime: process.uptime(),
            memory: process.memoryUsage(),
            baileysVersion: require('@whiskeysockets/baileys/package.json').version
        },
        sessions: Array.from(sessions.entries()).map(([orgId, session]) => ({
            organizationId: orgId,
            status: session.status,
            health: metrics.getHealth(orgId),
            retryCount: session.retryCount,
            phoneNumber: session.phoneNumber,
            connectedSince: metrics.connections.get(orgId)?.connectedAt
        }))
    };
    
    res.json(diagnostics);
});
```

---

## 6. Plan de Implementación Prioritario

### Fase 1: Crítico (Implementar YA) ✅
- [x] Actualizar a Baileys 7.0.0-rc.9
- [x] Implementar delay de 5 minutos para error 515
- [x] Simplificar configuración del socket
- [x] Deshabilitar verificación de readyState que causa false positives

### Fase 2: Alta Prioridad (Esta Semana)
- [ ] Implementar rate limiting por organización
- [ ] Validar credenciales antes de usar
- [ ] Mejorar manejo de errores específicos por código
- [ ] Implementar endpoint de diagnóstico

### Fase 3: Media Prioridad (Próximo Sprint)
- [ ] Health check periódico de sockets
- [ ] Keep-alive mejorado con pings
- [ ] Métricas de salud y uptime
- [ ] Alertas automáticas por desconexiones frecuentes

### Fase 4: Baja Prioridad (Futuro)
- [ ] Dashboard de monitoreo de conexiones
- [ ] Logs estructurados con Winston
- [ ] Tests automatizados de conexión/desconexión
- [ ] Documentación completa del servidor

---

## 7. Checklist de Operación Diaria

### Antes de Escanear QR
- [ ] Verificar que no hay otros dispositivos vinculados (máx 4)
- [ ] Limpiar sesiones corruptas: `rm -rf /var/www/whatsapp-server/auth_sessions/*`
- [ ] Reiniciar servidor: `pm2 restart whatsapp-server`
- [ ] Esperar 2 minutos antes de escanear

### Durante el Escaneo
- [ ] Escanear el QR rápidamente (antes de 2 minutos)
- [ ] NO cerrar la app de WhatsApp hasta ver "Conectado exitosamente"
- [ ] Monitorear logs: `pm2 logs whatsapp-server --lines 20`

### Si Falla
- [ ] Esperar 30-60 minutos antes de reintentar
- [ ] Verificar que el número no está bloqueado
- [ ] Probar con otro número si es posible
- [ ] Revisar logs para códigos de error específicos

---

## 8. Recursos Adicionales

- **Documentación Oficial**: https://baileys.wiki
- **Issues Relacionados**:
  - Error 515: https://github.com/WhiskeySockets/Baileys/issues/1533
  - Bad MAC: https://github.com/WhiskeySockets/Baileys/issues/1769
  - Disconnections: https://github.com/WhiskeySockets/Baileys/issues/2060
- **Discord de WhiskeySockets**: https://whiskey.so/discord
- **Changelog v7.0.0**: https://github.com/WhiskeySockets/Baileys/releases/tag/v7.0.0-rc.9

---

## Conclusión

El servidor de WhatsApp requiere:

1. **Paciencia**: Los errores 515 son rate limits de WhatsApp, no bugs del código
2. **Rate Limiting**: Implementar límites de intentos de conexión
3. **Manejo Robusto**: Cada código de error necesita su propia estrategia
4. **Monitoreo**: Métricas para detectar problemas antes de que sean críticos
5. **Simplificación**: Menos configuración = menos problemas

**NOTA CRÍTICA**: El error 515 actual requiere **esperar 30-60 minutos** antes de volver a intentar. No es un problema del código, es WhatsApp bloqueando temporalmente el número.
