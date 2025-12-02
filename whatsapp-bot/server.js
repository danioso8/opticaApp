const { default: makeWASocket, DisconnectReason, useMultiFileAuthState, fetchLatestBaileysVersion } = require('@whiskeysockets/baileys');
const express = require('express');
const qrcode = require('qrcode-terminal');
const pino = require('pino');
const fs = require('fs');
const path = require('path');

const app = express();
app.use(express.json());

let sock;
let qrCodeData = null;
let isConnected = false;

// Logger
const logger = pino({ level: 'silent' });

// Limpiar auth_info si está corrupto
const authPath = path.join(__dirname, 'auth_info');
if (fs.existsSync(authPath)) {
    const files = fs.readdirSync(authPath);
    if (files.length === 0 || files.some(f => f.includes('session'))) {
        console.log('🧹 Limpiando sesión anterior...');
        fs.rmSync(authPath, { recursive: true, force: true });
    }
}

async function connectToWhatsApp() {
    const { state, saveCreds } = await useMultiFileAuthState('auth_info');
    const { version } = await fetchLatestBaileysVersion();
    
    sock = makeWASocket({
        version,
        auth: state,
        printQRInTerminal: false,
        logger: logger,
        markOnlineOnConnect: false,
        syncFullHistory: false,
        browser: ['OCEANO OPTICO Bot', 'Chrome', '4.0.0'],
        defaultQueryTimeoutMs: undefined
    });

    sock.ev.on('connection.update', (update) => {
        const { connection, lastDisconnect, qr } = update;
        
        if (qr) {
            qrCodeData = qr;
            console.log('\n📱 ================================');
            console.log('   ESCANEA ESTE CÓDIGO QR CON');
            console.log('   TU WHATSAPP PARA CONECTAR');
            console.log('================================\n');
            qrcode.generate(qr, { small: true });
            console.log('\nO ve a: http://localhost:3000/qr\n');
        }

        if (connection === 'close') {
            const shouldReconnect = lastDisconnect?.error?.output?.statusCode !== DisconnectReason.loggedOut;
            const statusCode = lastDisconnect?.error?.output?.statusCode;
            
            console.log('❌ Conexión cerrada.');
            console.log('   Código:', statusCode);
            console.log('   Reconectando:', shouldReconnect);
            
            if (shouldReconnect) {
                setTimeout(() => {
                    connectToWhatsApp();
                }, 3000);
            }
            isConnected = false;
        } else if (connection === 'open') {
            console.log('✅ ¡Conectado a WhatsApp exitosamente!');
            console.log('🚀 Bot listo para enviar mensajes');
            qrCodeData = null;
            isConnected = true;
        }
    });

    sock.ev.on('creds.update', saveCreds);
}

// Iniciar conexión
connectToWhatsApp();

// ==================== API ENDPOINTS ====================

// Endpoint para obtener el código QR
app.get('/qr', (req, res) => {
    if (qrCodeData) {
        res.send(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>WhatsApp QR Code - OCEANO OPTICO</title>
                <meta charset="UTF-8">
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        display: flex;
                        flex-direction: column;
                        align-items: center;
                        justify-content: center;
                        min-height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                        color: white;
                    }
                    .container {
                        background: white;
                        padding: 40px;
                        border-radius: 20px;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                        text-align: center;
                        color: #333;
                    }
                    h1 { color: #667eea; margin-bottom: 20px; }
                    #qrcode { margin: 30px 0; }
                    .instructions {
                        text-align: left;
                        margin-top: 30px;
                        padding: 20px;
                        background: #f5f5f5;
                        border-radius: 10px;
                    }
                    .instructions ol { margin: 10px 0; padding-left: 20px; }
                    .instructions li { margin: 10px 0; }
                    .status {
                        padding: 10px 20px;
                        background: #4CAF50;
                        color: white;
                        border-radius: 5px;
                        margin-top: 20px;
                    }
                </style>
                <script src="https://cdn.jsdelivr.net/npm/qrcode@1.5.1/build/qrcode.min.js"></script>
            </head>
            <body>
                <div class="container">
                    <h1>🌊 OCEANO OPTICO 👓</h1>
                    <h2>Conectar WhatsApp Bot</h2>
                    <canvas id="qrcode"></canvas>
                    <div class="instructions">
                        <h3>📱 Instrucciones:</h3>
                        <ol>
                            <li>Abre WhatsApp en tu teléfono</li>
                            <li>Ve a <strong>Menú (⋮)</strong> > <strong>Dispositivos vinculados</strong></li>
                            <li>Toca <strong>Vincular un dispositivo</strong></li>
                            <li>Escanea este código QR</li>
                        </ol>
                    </div>
                    <div class="status" id="status">⏳ Esperando escaneo...</div>
                </div>
                <script>
                    const qrData = ${JSON.stringify(qrCodeData)};
                    const canvas = document.getElementById('qrcode');
                    QRCode.toCanvas(canvas, qrData, {
                        width: 300,
                        margin: 2,
                        color: {
                            dark: '#000000',
                            light: '#FFFFFF'
                        }
                    }, function (error) {
                        if (error) console.error(error);
                        console.log('QR generado correctamente');
                    });
                    
                    // Verificar conexión cada 2 segundos
                    setInterval(async () => {
                        const response = await fetch('/status');
                        const data = await response.json();
                        const statusDiv = document.getElementById('status');
                        
                        if (data.connected) {
                            statusDiv.innerHTML = '✅ ¡Conectado exitosamente!';
                            statusDiv.style.background = '#4CAF50';
                            setTimeout(() => {
                                window.close();
                            }, 2000);
                        }
                    }, 2000);
                </script>
            </body>
            </html>
        `);
    } else if (isConnected) {
        res.send(`
            <!DOCTYPE html>
            <html>
            <head>
                <title>WhatsApp Bot - OCEANO OPTICO</title>
                <meta charset="UTF-8">
                <style>
                    body {
                        font-family: Arial, sans-serif;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        min-height: 100vh;
                        margin: 0;
                        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                    }
                    .container {
                        background: white;
                        padding: 60px;
                        border-radius: 20px;
                        box-shadow: 0 20px 60px rgba(0,0,0,0.3);
                        text-align: center;
                    }
                    h1 { color: #4CAF50; font-size: 48px; margin: 0; }
                    p { color: #666; font-size: 20px; margin-top: 20px; }
                    .icon { font-size: 80px; margin-bottom: 20px; }
                </style>
            </head>
            <body>
                <div class="container">
                    <div class="icon">✅</div>
                    <h1>¡Ya estás conectado!</h1>
                    <p>El bot de WhatsApp está funcionando correctamente</p>
                </div>
            </body>
            </html>
        `);
    } else {
        res.send('<h1>⏳ Esperando conexión a WhatsApp...</h1><p>Recarga la página en unos segundos</p>');
    }
});

// Endpoint para verificar estado
app.get('/status', (req, res) => {
    res.json({
        connected: isConnected,
        hasQR: qrCodeData !== null
    });
});

// Endpoint para enviar mensajes
app.post('/send-message', async (req, res) => {
    const { chatId, message } = req.body;

    if (!isConnected) {
        return res.status(503).json({
            success: false,
            error: 'WhatsApp no está conectado. Escanea el código QR primero.'
        });
    }

    if (!chatId || !message) {
        return res.status(400).json({
            success: false,
            error: 'Se requiere chatId y message'
        });
    }

    try {
        await sock.sendMessage(chatId, { text: message });
        console.log(`✅ Mensaje enviado a ${chatId}`);
        
        res.json({
            success: true,
            message: 'Mensaje enviado exitosamente'
        });
    } catch (error) {
        console.error('❌ Error al enviar mensaje:', error);
        res.status(500).json({
            success: false,
            error: error.message
        });
    }
});

// Endpoint de salud
app.get('/health', (req, res) => {
    res.json({
        status: 'ok',
        connected: isConnected,
        timestamp: new Date().toISOString()
    });
});

// Iniciar servidor
const PORT = process.env.PORT || 3000;
app.listen(PORT, () => {
    console.log('\n🚀 ================================');
    console.log('   Servidor WhatsApp Bot iniciado');
    console.log(`   http://localhost:${PORT}`);
    console.log('================================\n');
    console.log('📱 Para conectar WhatsApp, ve a:');
    console.log(`   http://localhost:${PORT}/qr\n`);
});
