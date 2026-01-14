const { default: makeWASocket, DisconnectReason, useMultiFileAuthState, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const express = require('express');
const cors = require('cors');
const QRCode = require('qrcode');
const pino = require('pino');
const fs = require('fs');
const path = require('path');
require('dotenv').config();

const app = express();
const PORT = process.env.PORT || 3000;
const API_KEY = process.env.API_KEY || 'cambiar_en_produccion';

// Middlewares
app.use(cors());
app.use(express.json());

// Logger
const logger = pino({ level: 'info' });

// Almacenamiento de sesiones y sockets por organización
const sessions = new Map(); // organizationId -> { sock, qr, status, retryCount, badMacErrors, streamErrors }
const AUTH_DIR = path.join(__dirname, 'auth_sessions');

// Límite de errores Bad MAC antes de limpiar sesión
const BAD_MAC_ERROR_LIMIT = 3; // Reducido de 5 a 3 para ser más agresivo
const BAD_MAC_RESET_TIME = 30000; // Reducido a 30 segundos
const STREAM_ERROR_LIMIT = 2; // Límite de errores de stream antes de limpiar
const STREAM_ERROR_RESET_TIME = 60000; // 1 minuto

// Crear directorio de sesiones si no existe
if (!fs.existsSync(AUTH_DIR)) {
    fs.mkdirSync(AUTH_DIR, { recursive: true });
}

// Middleware de autenticación
function authenticateAPI(req, res, next) {
    const apiKey = req.headers['x-api-key'];
    if (!apiKey || apiKey !== API_KEY) {
        return res.status(401).json({ error: 'No autorizado' });
    }
    next();
}

// Función para manejar errores Bad MAC recurrentes
function handleBadMacError(organizationId) {
    const session = sessions.get(organizationId);
    if (!session) return;

    // Incrementar contador de errores Bad MAC
    if (!session.badMacErrors) {
        session.badMacErrors = {
            count: 0,
            lastError: Date.now(),
            resetTimeout: null
        };
    }

    const now = Date.now();
    const timeSinceLastError = now - session.badMacErrors.lastError;

    // Si han pasado más de 1 minuto desde el último error, resetear contador
    if (timeSinceLastError > BAD_MAC_RESET_TIME) {
        session.badMacErrors.count = 1;
    } else {
        session.badMacErrors.count++;
    }

    session.badMacErrors.lastError = now;

    logger.warn(`⚠️  Bad MAC Error #${session.badMacErrors.count} para ${organizationId}`);

    // Si alcanzamos el límite, limpiar sesión corrupta
    if (session.badMacErrors.count >= BAD_MAC_ERROR_LIMIT) {
        logger.error(`🔴 Límite de errores Bad MAC alcanzado para ${organizationId}. Limpiando sesión corrupta...`);
        clearCorruptedSession(organizationId);
    }

    // Programar reset del contador después de 1 minuto sin errores
    if (session.badMacErrors.resetTimeout) {
        clearTimeout(session.badMacErrors.resetTimeout);
    }
    
    session.badMacErrors.resetTimeout = setTimeout(() => {
        if (session.badMacErrors) {
            logger.info(`🔄 Reseteando contador de Bad MAC para ${organizationId}`);
            session.badMacErrors.count = 0;
        }
    }, BAD_MAC_RESET_TIME);
}

// Función para manejar errores de stream recurrentes
function handleStreamError(organizationId, reason) {
    const session = sessions.get(organizationId);
    if (!session) return;

    // Incrementar contador de errores de stream
    if (!session.streamErrors) {
        session.streamErrors = {
            count: 0,
            lastError: 0,
            resetTimeout: null
        };
    }

    const now = Date.now();
    const timeSinceLastError = now - session.streamErrors.lastError;

    // Resetear contador si pasó mucho tiempo desde el último error
    if (timeSinceLastError > STREAM_ERROR_RESET_TIME) {
        session.streamErrors.count = 1;
    } else {
        session.streamErrors.count++;
    }

    session.streamErrors.lastError = now;

    logger.warn(`⚠️  Stream Error #${session.streamErrors.count} para ${organizationId}: ${reason}`);

    // Si se superó el límite, limpiar sesión corrupta
    if (session.streamErrors.count >= STREAM_ERROR_LIMIT) {
        logger.error(`🔴 Límite de Stream Errors alcanzado (${STREAM_ERROR_LIMIT}). Limpiando sesión de ${organizationId}`);
        clearCorruptedSession(organizationId);
        return;
    }

    // Programar reseteo automático del contador
    if (session.streamErrors.resetTimeout) {
        clearTimeout(session.streamErrors.resetTimeout);
    }

    session.streamErrors.resetTimeout = setTimeout(() => {
        if (session.streamErrors) {
            logger.info(`Reseteando contador de Stream Errors para ${organizationId}`);
            session.streamErrors.count = 0;
        }
    }, STREAM_ERROR_RESET_TIME);
}

// Función para limpiar sesión corrupta
async function clearCorruptedSession(organizationId) {
    try {
        const session = sessions.get(organizationId);
        
        // Cerrar socket existente
        if (session?.sock) {
            logger.info(`Cerrando socket corrupto de ${organizationId}`);
            try {
                await session.sock.end();
            } catch (e) {
                logger.warn(`Error cerrando socket: ${e.message}`);
            }
        }

        const authPath = path.join(AUTH_DIR, organizationId);
        
        // Hacer backup de la sesión corrupta
        if (fs.existsSync(authPath)) {
            const backupPath = path.join(AUTH_DIR, `${organizationId}_corrupted_${Date.now()}`);
            logger.info(`💾 Respaldando sesión corrupta en ${backupPath}`);
            
            fs.renameSync(authPath, backupPath);
            
            // Eliminar backups antiguos (mantener solo los últimos 3)
            const backups = fs.readdirSync(AUTH_DIR)
                .filter(f => f.startsWith(`${organizationId}_corrupted_`))
                .sort()
                .reverse();
            
            if (backups.length > 3) {
                backups.slice(3).forEach(backup => {
                    const backupFullPath = path.join(AUTH_DIR, backup);
                    logger.info(`🗑️  Eliminando backup antiguo: ${backup}`);
                    fs.rmSync(backupFullPath, { recursive: true, force: true });
                });
            }
        }

        // Resetear sesión en memoria
        sessions.set(organizationId, {
            sock: null,
            qr: null,
            status: 'qr_required',
            retryCount: 0,
            badMacErrors: null,
            streamErrors: null
        });

        logger.info(`✨ Sesión limpiada para ${organizationId}. Se requiere escanear QR nuevamente.`);
        
        // Crear nueva conexión (generará nuevo QR)
        setTimeout(() => {
            logger.info(`🔄 Creando nueva conexión para ${organizationId}...`);
            createWhatsAppConnection(organizationId);
        }, 2000);

    } catch (error) {
        logger.error(`❌ Error limpiando sesión corrupta de ${organizationId}: ${error.message}`);
    }
}

// Crear conexión de WhatsApp para una organización
async function createWhatsAppConnection(organizationId) {
    try {
        const authPath = path.join(AUTH_DIR, organizationId);
        
        if (!fs.existsSync(authPath)) {
            fs.mkdirSync(authPath, { recursive: true });
        }

        const { state, saveCreds } = await useMultiFileAuthState(authPath);
        const { version } = await fetchLatestBaileysVersion();

        const sock = makeWASocket({
            version,
            logger: pino({ level: 'silent' }),
            printQRInTerminal: false,
            auth: state,
            getMessage: async () => undefined
        });

        // Guardar credenciales cuando cambien
        sock.ev.on('creds.update', saveCreds);

        // Manejar errores de sesión (Bad MAC, etc.)
        sock.ev.on('messages.upsert', async ({ messages, type }) => {
            // Este evento se dispara incluso si hay errores de descifrado
            // Interceptar aquí para detectar patrones de errores
        });

        // Capturar errores no manejados del socket
        const originalEmit = sock.ev.emit;
        sock.ev.emit = function(event, ...args) {
            if (event === 'connection.update') {
                // Interceptar y procesar actualizaciones de conexión
                const update = args[0];
                if (update.lastDisconnect?.error) {
                    const error = update.lastDisconnect.error;
                    const errorMsg = error.message || '';
                    
                    // Detectar errores Bad MAC
                    if (errorMsg.includes('Bad MAC') || errorMsg.includes('decrypt')) {
                        handleBadMacError(organizationId);
                    }
                }
            }
            return originalEmit.apply(this, [event, ...args]);
        };


        // Manejar actualizaciones de conexión
        sock.ev.on('connection.update', async (update) => {
            const { connection, lastDisconnect, qr } = update;

            if (qr) {
                // Generar QR como string base64
                const qrString = await QRCode.toDataURL(qr);
                const session = sessions.get(organizationId);
                if (session) {
                    session.qr = qrString;
                    session.status = 'qr_ready';
                }
                logger.info(`QR generado para ${organizationId}`);
            }

            if (connection === 'close') {
                const statusCode = lastDisconnect?.error?.output?.statusCode;
                const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
                
                logger.warn(`Conexión cerrada para ${organizationId}. Status: ${statusCode}, Reconectar: ${shouldReconnect}`);
                
                // Detectar errores de descifrado
                const errorMsg = lastDisconnect?.error?.message || '';
                
                // Manejar errores Bad MAC
                if (errorMsg.includes('Bad MAC') || errorMsg.includes('decrypt')) {
                    logger.error(`🔴 Error de descifrado detectado: ${errorMsg}`);
                    handleBadMacError(organizationId);
                    return; // No intentar reconectar con sesión corrupta
                }
                
                // Manejar errores de stream (ACK, Connection, etc.)
                if (errorMsg.includes('Stream Errored') || 
                    errorMsg.includes('Connection Closed') || 
                    errorMsg.includes('ack')) {
                    logger.error(`🔴 Error de stream detectado: ${errorMsg}`);
                    handleStreamError(organizationId, errorMsg);
                    return; // No intentar reconectar si hay problemas de stream recurrentes
                }
                
                logger.warn(`Razón de desconexión: ${errorMsg || 'Desconocida'}`);

                const session = sessions.get(organizationId);
                if (session) {
                    session.status = 'disconnected';
                }

                if (shouldReconnect) {
                    // Solo reintentar si no estamos ya conectados en otra sesión
                    const retryCount = (session?.retryCount || 0) + 1;
                    
                    // Limitar a 3 reintentos antes de requerir nuevo QR
                    if (retryCount <= 3) {
                        const delay = Math.min(1000 * Math.pow(2, retryCount), 10000);
                        
                        logger.info(`Reintentando conexión para ${organizationId} en ${delay}ms (intento ${retryCount})`);
                        
                        setTimeout(() => {
                            createWhatsAppConnection(organizationId);
                        }, delay);

                        if (session) {
                            session.retryCount = retryCount;
                        }
                    } else {
                        logger.warn(`Máximo de reintentos alcanzado para ${organizationId}. Se requiere escanear QR nuevamente.`);
                        if (session) {
                            session.status = 'qr_ready';
                            session.retryCount = 0;
                        }
                    }
                }
            } else if (connection === 'open') {
                logger.info(`✅ WhatsApp conectado exitosamente para ${organizationId}`);
                const session = sessions.get(organizationId);
                if (session) {
                    session.status = 'connected';
                    session.qr = null;
                    session.retryCount = 0;
                    
                    // Resetear contador de errores Bad MAC al conectar exitosamente
                    if (session.badMacErrors) {
                        if (session.badMacErrors.resetTimeout) {
                            clearTimeout(session.badMacErrors.resetTimeout);
                        }
                        session.badMacErrors = null;
                    }
                    
                    // Resetear contador de errores de stream al conectar exitosamente
                    if (session.streamErrors) {
                        if (session.streamErrors.resetTimeout) {
                            clearTimeout(session.streamErrors.resetTimeout);
                        }
                        session.streamErrors = null;
                    }
                    
                    // Obtener información del usuario conectado
                    try {
                        const user = sock.user;
                        if (user) {
                            session.phoneNumber = user.id.split(':')[0];
                            logger.info(`📱 Número conectado: ${session.phoneNumber}`);
                        }
                    } catch (e) {
                        logger.warn(`No se pudo obtener número de teléfono: ${e.message}`);
                    }
                }
            }
        });

        return sock;
    } catch (error) {
        logger.error(`Error creando conexión para ${organizationId}: ${error.message}`);
        throw error;
    }
}

// Formatear número de teléfono a formato WhatsApp
function formatPhoneNumber(phone) {
    // Limpiar el número
    let cleaned = phone.replace(/\D/g, '');
    
    // Si no empieza con 57 (Colombia), agregarlo
    if (!cleaned.startsWith('57')) {
        cleaned = '57' + cleaned;
    }
    
    // Formato de WhatsApp
    return cleaned + '@s.whatsapp.net';
}

// ==================== ENDPOINTS ====================

// Healthcheck
app.get('/health', (req, res) => {
    res.json({ 
        status: 'ok', 
        sessions: sessions.size,
        timestamp: new Date().toISOString()
    });
});

// Iniciar sesión de WhatsApp (genera QR)
app.post('/api/start-session', authenticateAPI, async (req, res) => {
    try {
        const { organization_id } = req.body;

        if (!organization_id) {
            return res.status(400).json({ error: 'organization_id es requerido' });
        }

        // Verificar si ya existe una sesión
        if (sessions.has(organization_id)) {
            const session = sessions.get(organization_id);
            return res.json({
                message: 'Sesión ya existe',
                status: session.status,
                qr: session.qr
            });
        }

        // Crear nueva sesión
        sessions.set(organization_id, {
            sock: null,
            qr: null,
            status: 'connecting',
            retryCount: 0,
            badMacErrors: null,
            streamErrors: null
        });

        const sock = await createWhatsAppConnection(organization_id);
        sessions.get(organization_id).sock = sock;

        res.json({
            message: 'Sesión iniciada',
            organization_id,
            status: 'connecting'
        });
    } catch (error) {
        logger.error(`Error iniciando sesión: ${error.message}`);
        res.status(500).json({ error: error.message });
    }
});

// Obtener QR de una sesión
app.get('/api/qr/:organization_id', authenticateAPI, (req, res) => {
    try {
        const { organization_id } = req.params;
        const session = sessions.get(organization_id);

        if (!session) {
            return res.status(404).json({ error: 'Sesión no encontrada' });
        }

        res.json({
            organization_id,
            status: session.status,
            qr: session.qr,
            has_qr: !!session.qr
        });
    } catch (error) {
        logger.error(`Error obteniendo QR: ${error.message}`);
        res.status(500).json({ error: error.message });
    }
});

// Obtener estado de sesión
app.get('/api/status/:organization_id', authenticateAPI, (req, res) => {
    try {
        const { organization_id } = req.params;
        const session = sessions.get(organization_id);

        if (!session) {
            return res.json({
                organization_id,
                status: 'not_started',
                connected: false,
                phone_number: null
            });
        }

        res.json({
            organization_id,
            status: session.status,
            connected: session.status === 'connected',
            has_qr: !!session.qr,
            phone_number: session.phoneNumber || null
        });
    } catch (error) {
        logger.error(`Error obteniendo estado: ${error.message}`);
        res.status(500).json({ error: error.message });
    }
});

// Enviar mensaje
app.post('/api/send-message', authenticateAPI, async (req, res) => {
    try {
        const { organization_id, phone, message } = req.body;

        if (!organization_id || !phone || !message) {
            return res.status(400).json({ 
                error: 'organization_id, phone y message son requeridos' 
            });
        }

        const session = sessions.get(organization_id);

        if (!session || !session.sock) {
            return res.status(404).json({ 
                error: 'Sesión no encontrada. Inicie sesión primero escaneando el código QR',
                status: 'not_started'
            });
        }

        if (session.status !== 'connected') {
            return res.status(400).json({ 
                error: `WhatsApp no está conectado. Estado actual: ${session.status}`,
                status: session.status,
                hint: 'Escanea el código QR para conectar WhatsApp'
            });
        }

        const formattedPhone = formatPhoneNumber(phone);
        
        // Intentar enviar el mensaje
        try {
            await session.sock.sendMessage(formattedPhone, { text: message });
            
            logger.info(`Mensaje enviado a ${phone} (${organization_id})`);

            res.json({
                success: true,
                message: 'Mensaje enviado correctamente',
                phone: formattedPhone
            });
        } catch (sendError) {
            // Si falla el envío, marcar la sesión como desconectada
            session.status = 'disconnected';
            
            logger.error(`Error al enviar mensaje: ${sendError.message}`);
            
            return res.status(500).json({ 
                error: 'Error enviando mensaje. La conexión puede estar cerrada.',
                details: sendError.message,
                status: 'disconnected',
                hint: 'Vuelva a escanear el código QR para reconectar'
            });
        }
    } catch (error) {
        logger.error(`Error enviando mensaje: ${error.message}`);
        res.status(500).json({ 
            error: 'Error enviando mensaje',
            details: error.message 
        });
    }
});

// Cerrar sesión
app.post('/api/logout', authenticateAPI, async (req, res) => {
    try {
        const { organization_id } = req.body;

        if (!organization_id) {
            return res.status(400).json({ error: 'organization_id es requerido' });
        }

        const session = sessions.get(organization_id);

        if (!session) {
            return res.status(404).json({ error: 'Sesión no encontrada' });
        }

        // Cerrar socket
        if (session.sock) {
            await session.sock.logout();
        }

        // Eliminar sesión del mapa
        sessions.delete(organization_id);

        // Eliminar archivos de autenticación
        const authPath = path.join(AUTH_DIR, organization_id);
        if (fs.existsSync(authPath)) {
            fs.rmSync(authPath, { recursive: true, force: true });
        }

        logger.info(`Sesión cerrada para ${organization_id}`);

        res.json({
            success: true,
            message: 'Sesión cerrada'
        });
    } catch (error) {
        logger.error(`Error cerrando sesión: ${error.message}`);
        res.status(500).json({ error: error.message });
    }
});

// Endpoint para forzar limpieza de sesión corrupta
app.post('/api/force-clean-session', authenticateAPI, async (req, res) => {
    try {
        const { organization_id } = req.body;

        if (!organization_id) {
            return res.status(400).json({ error: 'organization_id es requerido' });
        }

        logger.info(`🔧 Forzando limpieza de sesión para ${organization_id}`);
        
        await clearCorruptedSession(organization_id);

        res.json({
            success: true,
            message: `Sesión limpiada para ${organization_id}. Se requiere escanear QR nuevamente.`
        });
    } catch (error) {
        logger.error(`Error forzando limpieza: ${error.message}`);
        res.status(500).json({ error: error.message });
    }
});

// Limpiar sesión corrupta manualmente
app.post('/api/clear-corrupted-session', authenticateAPI, async (req, res) => {
    try {
        const { organization_id } = req.body;

        if (!organization_id) {
            return res.status(400).json({ error: 'organization_id es requerido' });
        }

        logger.info(`🔧 Solicitud manual de limpieza de sesión para ${organization_id}`);
        
        await clearCorruptedSession(organization_id);

        res.json({
            success: true,
            message: 'Sesión limpiada exitosamente. Se requiere escanear QR nuevamente.'
        });
    } catch (error) {
        logger.error(`Error limpiando sesión: ${error.message}`);
        res.status(500).json({ error: error.message });
    }
});

// Listar todas las sesiones activas
app.get('/api/sessions', authenticateAPI, (req, res) => {
    try {
        const sessionsList = [];
        
        sessions.forEach((session, organizationId) => {
            sessionsList.push({
                organization_id: organizationId,
                status: session.status,
                connected: session.status === 'connected',
                has_qr: !!session.qr
            });
        });

        res.json({
            total: sessionsList.length,
            sessions: sessionsList
        });
    } catch (error) {
        logger.error(`Error listando sesiones: ${error.message}`);
        res.status(500).json({ error: error.message });
    }
});

// Restaurar sesiones existentes al iniciar el servidor
async function restoreExistingSessions() {
    try {
        const organizations = fs.readdirSync(AUTH_DIR);
        
        logger.info(`Restaurando ${organizations.length} sesiones existentes...`);

        for (const orgId of organizations) {
            const authPath = path.join(AUTH_DIR, orgId);
            const credsPath = path.join(authPath, 'creds.json');
            
            // Solo restaurar si tiene credenciales guardadas
            if (fs.existsSync(credsPath)) {
                logger.info(`Restaurando sesión para ${orgId}`);
                
                sessions.set(orgId, {
                    sock: null,
                    qr: null,
                    status: 'restoring',
                    retryCount: 0,
                    badMacErrors: null,
                    streamErrors: null
                });

                const sock = await createWhatsAppConnection(orgId);
                sessions.get(orgId).sock = sock;
            }
        }

        logger.info('Restauración de sesiones completada');
    } catch (error) {
        logger.error(`Error restaurando sesiones: ${error.message}`);
    }
}

// Iniciar servidor
app.listen(PORT, async () => {
    logger.info(`🚀 Servidor WhatsApp iniciado en puerto ${PORT}`);
    logger.info(`📱 API Key: ${API_KEY}`);
    logger.info(`📂 Sesiones guardadas en: ${AUTH_DIR}`);
    
    // Restaurar sesiones existentes
    await restoreExistingSessions();
});

// Manejo de cierre graceful
process.on('SIGINT', async () => {
    logger.info('Cerrando servidor...');
    
    // Cerrar todas las conexiones
    for (const [orgId, session] of sessions.entries()) {
        if (session.sock) {
            logger.info(`Cerrando sesión de ${orgId}`);
            await session.sock.end();
        }
    }
    
    process.exit(0);
});
