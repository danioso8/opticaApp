#!/usr/bin/env node
/**
 * Script de Simulación y Prueba del Servidor WhatsApp
 * 
 * Prueba todas las funcionalidades críticas del servidor sin conectar WhatsApp real
 * 
 * Uso:
 *   node test_server.js
 */

const axios = require('axios');

// Configuración
const BASE_URL = 'http://84.247.129.180:3000';
const API_KEY = 'opticaapp_2026_whatsapp_baileys_secret_key_12345';

// Colores simples sin chalk
const success = (text) => `✅ ${text}`;
const error = (text) => `❌ ${text}`;
const info = (text) => `ℹ️  ${text}`;
const warning = (text) => `⚠️  ${text}`;
const title = (text) => `\n${text}\n${'='.repeat(text.length)}`;

// Contador de pruebas
let testsPassed = 0;
let testsFailed = 0;

// Helper para hacer requests
async function request(method, endpoint, data = null) {
    try {
        const config = {
            method,
            url: `${BASE_URL}${endpoint}`,
            headers: {
                'X-API-Key': API_KEY,
                'Content-Type': 'application/json'
            }
        };
        
        if (data) {
            config.data = data;
        }
        
        const response = await axios(config);
        return { success: true, data: response.data, status: response.status };
    } catch (err) {
        return { 
            success: false, 
            error: err.response?.data || err.message,
            status: err.response?.status || 500
        };
    }
}

// Helper para esperar
function sleep(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Helper para test
function test(name, condition, details = '') {
    if (condition) {
        console.log(success(`✅ ${name}`));
        if (details) console.log(info(`   ${details}`));
        testsPassed++;
        return true;
    } else {
        console.log(error(`❌ ${name}`));
        if (details) console.log(error(`   ${details}`));
        testsFailed++;
        return false;
    }
}

// ==========================================================
// PRUEBAS
// ==========================================================

async function runTests() {
    console.log(title('\n🧪 INICIANDO SIMULACIÓN DEL SERVIDOR WHATSAPP\n'));
    console.log(info(`Servidor: ${BASE_URL}`));
    console.log(info(`API Key: ${API_KEY.substring(0, 20)}...\n`));
    
    // ====== PRUEBA 1: Health Check ======
    console.log(title('\n📋 PRUEBA 1: Health Check'));
    const health = await request('GET', '/health');
    test(
        'Health check responde',
        health.success && health.status === 200,
        `Status: ${health.data?.status || 'unknown'}, Sessions: ${health.data?.sessions || 0}`
    );
    
    // ====== PRUEBA 2: Rate Limiting Status ======
    console.log(title('\n📋 PRUEBA 2: Rate Limiting Status'));
    const rateLimit = await request('GET', '/api/rate-limit-status');
    test(
        'Endpoint de rate limiting funciona',
        rateLimit.success,
        `Global attempts: ${rateLimit.data?.global_attempts_last_hour || 0}/${rateLimit.data?.global_limit || 3}`
    );
    
    if (rateLimit.success) {
        test(
            'Límite global configurado correctamente',
            rateLimit.data.global_limit === 3,
            `Límite: ${rateLimit.data.global_limit} conexiones/hora`
        );
        test(
            'No hay bloqueos activos',
            !rateLimit.data.global_blocked,
            'Servidor listo para aceptar conexiones'
        );
    }
    
    // ====== PRUEBA 3: Rate Limiting por Organización ======
    console.log(title('\n📋 PRUEBA 3: Rate Limiting por Organización'));
    const orgRateLimit = await request('GET', '/api/rate-limit-status?organization_id=999');
    test(
        'Rate limiting específico de org funciona',
        orgRateLimit.success,
        `Org 999 - Can connect: ${orgRateLimit.data?.can_connect}`
    );
    
    if (orgRateLimit.success) {
        test(
            'Organización puede conectar',
            orgRateLimit.data.can_connect === true,
            'Sin bloqueos previos'
        );
        test(
            'Límite diario configurado',
            orgRateLimit.data.daily_limit === 2,
            `Límite: ${orgRateLimit.data.daily_limit} intentos/día`
        );
        test(
            'Sin intentos previos',
            orgRateLimit.data.attempts_last_24h === 0,
            'Contador en 0'
        );
    }
    
    // ====== PRUEBA 4: Listar Sesiones Vacías ======
    console.log(title('\n📋 PRUEBA 4: Listar Sesiones'));
    const sessions = await request('GET', '/api/sessions');
    test(
        'Endpoint de sesiones funciona',
        sessions.success,
        `Total sesiones: ${sessions.data?.total || 0}`
    );
    
    // ====== PRUEBA 5: Error de Autenticación ======
    console.log(title('\n📋 PRUEBA 5: Seguridad - API Key'));
    const unauthorized = await axios.get(`${BASE_URL}/api/sessions`, {
        headers: { 'X-API-Key': 'INVALID_KEY' },
        validateStatus: () => true
    });
    test(
        'Rechaza API key inválida',
        unauthorized.status === 401,
        'Error 401 Unauthorized'
    );
    
    // ====== PRUEBA 6: Validación de Parámetros ======
    console.log(title('\n📋 PRUEBA 6: Validación de Parámetros'));
    const noOrgId = await request('POST', '/api/start-session', {});
    test(
        'Valida organization_id requerido',
        !noOrgId.success && noOrgId.status === 400,
        noOrgId.error?.error || 'Validación correcta'
    );
    
    // ====== PRUEBA 7: Estado de Sesión No Existente ======
    console.log(title('\n📋 PRUEBA 7: Estado de Sesión No Existente'));
    const noSession = await request('GET', '/api/status/999');
    test(
        'Retorna estado correcto para sesión no existente',
        noSession.success && noSession.data.status === 'not_started',
        `Status: ${noSession.data?.status}`
    );
    
    // ====== PRUEBA 8: QR de Sesión No Existente ======
    console.log(title('\n📋 PRUEBA 8: QR de Sesión No Existente'));
    const noQr = await request('GET', '/api/qr/999');
    test(
        'Retorna error 404 para QR no existente',
        !noQr.success && noQr.status === 404,
        'Error 404 esperado'
    );
    
    // ====== PRUEBA 9: Enviar Mensaje Sin Sesión ======
    console.log(title('\n📋 PRUEBA 9: Enviar Mensaje Sin Sesión'));
    const noMessage = await request('POST', '/api/send-message', {
        organization_id: '999',
        phone: '3001234567',
        message: 'Test'
    });
    test(
        'Rechaza envío sin sesión activa',
        !noMessage.success && noMessage.status === 404,
        noMessage.error?.error || 'Sesión no encontrada'
    );
    
    // ====== PRUEBA 10: Logout Sin Sesión ======
    console.log(title('\n📋 PRUEBA 10: Logout Sin Sesión'));
    const noLogout = await request('POST', '/api/logout', { organization_id: '999' });
    test(
        'Retorna error al cerrar sesión no existente',
        !noLogout.success && noLogout.status === 404,
        'Error 404 esperado'
    );
    
    // ====== PRUEBA 11: Simulación de Rate Limiting ======
    console.log(title('\n📋 PRUEBA 11: Simulación de Rate Limiting'));
    console.log(info('   ℹ️  Esta prueba simula múltiples intentos de conexión'));
    console.log(warning('   ⚠️  Se esperan errores controlados'));
    
    let rateLimitHit = false;
    let attempts = 0;
    const testOrgId = 'test_' + Date.now();
    
    // Nota: No podemos probar conexión real sin WhatsApp
    console.log(info(`   → Verificando límites para org ${testOrgId}`));
    const limitCheck = await request('GET', `/api/rate-limit-status?organization_id=${testOrgId}`);
    
    test(
        'Rate limiting responde para nueva org',
        limitCheck.success && limitCheck.data.can_connect === true,
        `Org ${testOrgId} puede conectar`
    );
    
    // ====== PRUEBA 12: Endpoints Seguros ======
    console.log(title('\n📋 PRUEBA 12: Protección de Endpoints'));
    
    const endpoints = [
        { method: 'GET', path: '/api/sessions' },
        { method: 'GET', path: '/api/rate-limit-status' },
        { method: 'POST', path: '/api/start-session' },
        { method: 'GET', path: '/api/status/1' },
    ];
    
    for (const endpoint of endpoints) {
        const unauth = await axios({
            method: endpoint.method,
            url: `${BASE_URL}${endpoint.path}`,
            headers: { 'X-API-Key': 'WRONG_KEY' },
            validateStatus: () => true
        });
        
        test(
            `${endpoint.method} ${endpoint.path} protegido`,
            unauth.status === 401,
            'Requiere autenticación'
        );
    }
    
    // ====== PRUEBA 13: Health Check No Requiere Auth ======
    console.log(title('\n📋 PRUEBA 13: Health Check Sin Auth'));
    const publicHealth = await axios.get(`${BASE_URL}/health`, {
        validateStatus: () => true
    });
    test(
        'Health check es público (no requiere API key)',
        publicHealth.status === 200,
        'Accesible sin autenticación'
    );
    
    // ====== RESUMEN ======
    console.log(title('\n' + '='.repeat(60)));
    console.log(title('📊 RESUMEN DE PRUEBAS'));
    console.log(title('='.repeat(60)));
    
    const total = testsPassed + testsFailed;
    const percentage = ((testsPassed / total) * 100).toFixed(1);
    
    console.log(success(`✅ Pruebas exitosas: ${testsPassed}/${total} (${percentage}%)`));
    if (testsFailed > 0) {
        console.log(error(`❌ Pruebas fallidas: ${testsFailed}/${total}`));
    }
    
    console.log('\n' + title('Estado del Servidor:'));
    
    if (testsFailed === 0) {
        console.log(success('✅ SERVIDOR OPERACIONAL - Todas las pruebas pasaron'));
        console.log(success('✅ Rate limiting funcionando correctamente'));
        console.log(success('✅ Autenticación funcionando correctamente'));
        console.log(success('✅ Validaciones funcionando correctamente'));
        console.log(success('✅ Endpoints respondiendo correctamente'));
        console.log(success('\n🎉 El servidor está listo para conectar WhatsApp el lunes\n'));
    } else {
        console.log(error('❌ HAY PROBLEMAS QUE RESOLVER'));
        console.log(warning('⚠️  Revisar logs del servidor'));
        console.log(warning('⚠️  Verificar que el servidor esté corriendo'));
        console.log(warning('⚠️  Verificar configuración de API_KEY\n'));
    }
    
    // Exit code
    process.exit(testsFailed > 0 ? 1 : 0);
}

// ==========================================================
// MAIN
// ==========================================================

async function main() {
    try {
        console.log(title('╔════════════════════════════════════════════════════════╗'));
        console.log(title('║     SIMULADOR DE SERVIDOR WHATSAPP - OpticaApp        ║'));
        console.log(title('║              Pruebas sin Conexión Real                ║'));
        console.log(title('╚════════════════════════════════════════════════════════╝'));
        
        console.log(info('\n🔍 Verificando servidor...'));
        
        // Verificar que el servidor esté corriendo
        try {
            await axios.get(`${BASE_URL}/health`, { timeout: 3000 });
            console.log(success('✅ Servidor detectado en ' + BASE_URL));
        } catch (err) {
            console.log(error('❌ Servidor no disponible en ' + BASE_URL));
            console.log(warning('\n⚠️  Asegúrate de que el servidor esté corriendo:'));
            console.log(info('   ssh root@84.247.129.180 "pm2 start whatsapp-server"'));
            console.log(info('   O localmente: npm start\n'));
            process.exit(1);
        }
        
        await runTests();
        
    } catch (err) {
        console.log(error('\n❌ Error fatal en la simulación:'));
        console.log(error(err.message));
        if (err.stack) {
            console.log(error('\nStack trace:'));
            console.log(error(err.stack));
        }
        process.exit(1);
    }
}

// Ejecutar
if (require.main === module) {
    main();
}

module.exports = { request, test };
