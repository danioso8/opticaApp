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
const sessions = new Map(); // organizationId -> { sock, qr, status, retryCount }
const AUTH_DIR = path.join(__dirname, 'auth_sessions');

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
                logger.warn(`Razón de desconexión: ${lastDisconnect?.error?.message || 'Desconocida'}`);

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
            retryCount: 0
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
                    retryCount: 0
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

// Función para detectar y restaurar nuevas sesiones que no están cargadas
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

// Iniciar servidor
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
