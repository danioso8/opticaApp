# Documentación - Migración a Contabo VPS y Configuración WhatsApp

**Desarrollador:** Daniel Osorio  
**Fecha:** 5 de Enero de 2026  
**Proyecto:** OpticaApp - Sistema de Gestión Óptica

---

## 📋 Resumen de Migración

**Servidor Anterior:** Render.com (PostgreSQL + Django)  
**Servidor Nuevo:** Contabo VPS Ubuntu 24.04  
**IP del Servidor:** 84.247.129.180  
**Estado:** ✅ **MIGRACIÓN COMPLETADA Y FUNCIONAL**

---

## 🚀 Infraestructura Instalada

### Stack Tecnológico
- **Sistema Operativo:** Ubuntu 24.04 LTS
- **Servidor Web:** Nginx 1.24.0
- **Base de Datos:** PostgreSQL 15
- **Python:** 3.12.3
- **Node.js:** 20.19.6
- **Gestor de Procesos:** PM2 (para Django y WhatsApp server)
- **WSGI:** Gunicorn

### Servicios Activos (PM2)
```bash
┌────┬──────────────────┬─────────┬─────────┬──────────┐
│ id │ name             │ mode    │ pid     │ status   │
├────┼──────────────────┼─────────┼─────────┼──────────┤
│ 2  │ opticaapp        │ fork    │ 21967   │ online   │
│ 3  │ whatsapp-server  │ fork    │ 23493   │ online   │
└────┴──────────────────┴─────────┴─────────┴──────────┘
```

---

## 📊 Migración de Datos

### Datos Transferidos desde Render
- **8 usuarios** migrados exitosamente
- **7 organizaciones** (incluyendo CompuEasys ID: 23)
- **34 pacientes** con toda su información clínica
- **Credenciales** de superusuario mantenidas
- **Relaciones** entre organizaciones y usuarios preservadas

### Comando de Migración Utilizado
```bash
# Exportar desde Render
pg_dump -h <render_host> -U <user> -d <database> --no-owner --no-acl > backup.sql

# Importar a Contabo
psql -U opticaapp_user -d opticaapp_db < backup.sql
```

---

## 🔧 Configuración de WhatsApp Baileys

### Servidor WhatsApp Instalado
**Ubicación:** `/var/www/whatsapp-server/`  
**Puerto:** 3000  
**Librería:** @whiskeysockets/baileys  
**Autenticación:** API Key

### Variables de Entorno
**Django (.env):**
```env
WHATSAPP_SERVER_URL=http://localhost:3000
WHATSAPP_SERVER_API_KEY=opticaapp_2026_whatsapp_baileys_secret_key_12345
```

**WhatsApp Server (.env):**
```env
PORT=3000
API_KEY=opticaapp_2026_whatsapp_baileys_secret_key_12345
```

### Endpoints Configurados
- `POST /api/start-session` - Iniciar sesión (generar QR)
- `GET /api/qr/:organization_id` - Obtener código QR
- `GET /api/status/:organization_id` - Verificar estado de conexión
- `POST /api/send-message` - Enviar mensaje de WhatsApp
- `POST /api/logout` - Cerrar sesión de WhatsApp

---

## ✅ Correcciones Implementadas

### 1. Error 500 en Configuración de Notificaciones
**Problema:** Campo `whatsapp_enabled` con constraint NOT NULL
**Solución:**
- Creada migración: `0016_remove_notificationsettings_whatsapp_enabled.py`
- Removido campo obsoleto de la base de datos
- Verificado funcionamiento de la página de configuración

**Archivo:** `apps/appointments/migrations/0016_remove_notificationsettings_whatsapp_enabled.py`

### 2. Código QR no se mostraba en Frontend
**Problema:** Backend devolvía `qr: null` en endpoint de status

**Causa:** El endpoint `/api/status/` no incluía el QR en la respuesta

**Solución:**
Modificado `apps/dashboard/views_whatsapp_baileys.py` - función `whatsapp_get_status`:
```python
def whatsapp_get_status(request):
    # ... código existente ...
    
    # Si el status es qr_ready y has_qr es true, obtener el QR
    if status == 'qr_ready' and result.get('has_qr'):
        qr_result = whatsapp_baileys_client.get_qr(org_id)
        if qr_result and qr_result.get('qr'):
            qr_code = qr_result.get('qr')
    
    return JsonResponse({
        'success': True,
        'status': status,
        'phone_number': phone_number,
        'qr': qr_code  # Ahora incluye el QR completo
    })
```

### 3. Desconexiones Continuas de WhatsApp
**Problema:** Sesión se conectaba pero se cerraba inmediatamente

**Soluciones Implementadas:**

**a) Mejor manejo de reconexiones** (`whatsapp-server/server.js`):
```javascript
if (connection === 'close') {
    const statusCode = lastDisconnect?.error?.output?.statusCode;
    const shouldReconnect = statusCode !== DisconnectReason.loggedOut;
    
    // Limitar reintentos a 3 antes de requerir nuevo QR
    if (shouldReconnect && retryCount <= 3) {
        const delay = Math.min(1000 * Math.pow(2, retryCount), 10000);
        setTimeout(() => createWhatsAppConnection(organizationId), delay);
    }
}
```

**b) Captura de número de teléfono:**
```javascript
else if (connection === 'open') {
    logger.info(`✅ WhatsApp conectado exitosamente para ${organizationId}`);
    const session = sessions.get(organizationId);
    if (session) {
        session.status = 'connected';
        session.qr = null;
        session.retryCount = 0;
        
        // Guardar número de teléfono
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
```

**c) Logging mejorado:**
- Muestra código de error específico
- Razón de desconexión detallada
- Contador de reintentos visible

### 4. Sesión se Reiniciaba en Cada Recarga
**Problema:** Al eliminar credenciales antiguas, sesión no persistía

**Solución:**
- Credenciales guardadas en `/var/www/whatsapp-server/auth_sessions/{organization_id}/`
- Restauración automática de sesiones al reiniciar servidor:
```javascript
async function restoreExistingSessions() {
    const organizations = fs.readdirSync(AUTH_DIR);
    
    for (const orgId of organizations) {
        const credsPath = path.join(AUTH_DIR, orgId, 'creds.json');
        if (fs.existsSync(credsPath)) {
            logger.info(`Restaurando sesión para ${orgId}`);
            const sock = await createWhatsAppConnection(orgId);
            sessions.get(orgId).sock = sock;
        }
    }
}
```

---

## 🧪 Pruebas Realizadas

### ✅ WhatsApp Funcionando
1. **Generación de QR:** ✅ QR se muestra correctamente en frontend
2. **Escaneo con móvil:** ✅ Conexión exitosa
3. **Estado conectado:** ✅ Muestra número de teléfono
4. **Envío de mensajes:** ✅ Mensaje de prueba recibido
5. **Persistencia:** ✅ Sesión se mantiene tras recargar página

### Prueba de Envío de Mensaje
**Endpoint probado:**
```bash
curl -X POST http://localhost:3000/api/send-message \
  -H "Content-Type: application/json" \
  -H "X-API-Key: opticaapp_2026_whatsapp_baileys_secret_key_12345" \
  -d '{
    "organization_id": "23",
    "phone": "3001234567",
    "message": "Hola prueba"
  }'
```

**Resultado:** ✅ Mensaje recibido exitosamente en WhatsApp

---

## 📝 Archivos Modificados

### Backend Django
1. `apps/dashboard/views_whatsapp_baileys.py`
   - `whatsapp_get_status()` - Ahora obtiene QR cuando está disponible
   - `whatsapp_test_message()` - Mejorado logging de mensajes

2. `apps/appointments/migrations/0016_remove_notificationsettings_whatsapp_enabled.py`
   - Migración para eliminar campo obsoleto

### Servidor WhatsApp
1. `/var/www/whatsapp-server/server.js`
   - Manejo mejorado de reconexiones
   - Límite de 3 reintentos
   - Captura de número de teléfono
   - Logging detallado de errores
   - Endpoint `/api/status/` devuelve `phone_number`

### Frontend
1. `apps/dashboard/templates/dashboard/whatsapp_baileys_config.html`
   - Función `checkStatus()` - Debugging mejorado
   - Función `displayQR()` - Validación de datos
   - Console logs para debugging

---

## 🔐 Seguridad

### API Key Configurada
- **Django y WhatsApp Server:** Misma API Key sincronizada
- **Autenticación:** Middleware en todas las rutas
- **Header requerido:** `X-API-Key`

### PostgreSQL
- **Usuario:** opticaapp_user (sin privilegios de superusuario)
- **Base de datos:** opticaapp_db
- **Permisos:** Solo acceso a su propia base de datos

---

## 📦 Dependencias Instaladas (Servidor)

### Sistema
```bash
sudo apt update
sudo apt install -y python3 python3-pip python3-venv postgresql nginx git curl
```

### Node.js y PM2
```bash
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs
sudo npm install -g pm2
```

### Python (venv)
```bash
python3 -m venv /var/www/opticaapp/venv
source /var/www/opticaapp/venv/bin/activate
pip install -r requirements.txt
```

### WhatsApp Server
```bash
cd /var/www/whatsapp-server
npm install
# Dependencias principales:
# - @whiskeysockets/baileys
# - express
# - qrcode
# - pino (logging)
# - cors
```

---

## 🚦 Estado de Servicios

### Nginx
```bash
sudo systemctl status nginx
# ● nginx.service - A high performance web server
#    Active: active (running)
```

**Configuración:** `/etc/nginx/sites-available/opticaapp`
- Proxy reverso a Django (puerto 8000)
- Archivos estáticos servidos directamente

### PostgreSQL
```bash
sudo systemctl status postgresql
# ● postgresql.service - PostgreSQL RDBMS
#    Active: active (running)
```

### PM2
```bash
pm2 status
# opticaapp: online (Gunicorn en puerto 8000)
# whatsapp-server: online (Node.js en puerto 3000)
```

---

## ⏭️ Próximos Pasos Pendientes

### Alta Prioridad
1. **SSL/HTTPS** - Instalar certificado Let's Encrypt con certbot
2. **Dominio** - Configurar DNS en Hostinger apuntando a 84.247.129.180
3. **DEBUG=False** - Cambiar en producción
4. **Media Files** - Migrar archivos de Render a `/var/www/opticaapp/media/`

### Media Prioridad
1. **Backups automáticos** - Configurar cron para backup diario de PostgreSQL
2. **Monitoreo** - Configurar alertas de PM2
3. **Logs** - Rotar logs de Nginx y Django

### Baja Prioridad
1. **Optimización** - Configurar cache de Django
2. **CDN** - Evaluar uso de CDN para archivos estáticos
3. **Firewall** - Configurar UFW con reglas específicas

---

## 🐛 Problemas Conocidos y Soluciones

### Problema: "Connection Closed" al enviar mensaje
**Causa:** Sesión de WhatsApp se cerró antes de enviar
**Solución:** Reconectar escaneando QR nuevamente
**Prevención:** Mantener página abierta, no cerrar sesión manualmente

### Problema: QR no aparece tras hacer clic
**Causa:** Frontend polling no captura QR a tiempo
**Solución:** Esperar 2-3 segundos, el QR aparecerá automáticamente
**Debugging:** Abrir consola (F12) para ver logs

### Problema: "Bad escaped character in JSON"
**Causa:** Emojis en mensajes no escapados correctamente
**Solución:** Evitar emojis en mensaje por defecto (ya corregido)
**Archivo:** `apps/dashboard/views_whatsapp_baileys.py` línea 172

---

## 📊 Métricas de Migración

### Tiempo de Migración
- **Planificación y backup:** 30 minutos
- **Instalación de servidor:** 45 minutos
- **Migración de datos:** 15 minutos
- **Configuración de WhatsApp:** 2 horas (debugging incluido)
- **Pruebas y validación:** 45 minutos
- **TOTAL:** ~4.5 horas

### Disponibilidad
- **Downtime planificado:** 0 (servidor Render sigue activo)
- **Tiempo hasta producción:** 4.5 horas
- **Disponibilidad actual:** 100%

---

## 🔄 Comandos Útiles de Mantenimiento

### PM2
```bash
# Ver logs en tiempo real
pm2 logs opticaapp --lines 100
pm2 logs whatsapp-server --lines 100

# Reiniciar servicios
pm2 restart opticaapp --update-env
pm2 restart whatsapp-server

# Guardar configuración PM2
pm2 save
pm2 startup
```

### Django
```bash
# Activar entorno virtual
source /var/www/opticaapp/venv/bin/activate

# Aplicar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Recolectar archivos estáticos
python manage.py collectstatic --noinput
```

### PostgreSQL
```bash
# Conectar a base de datos
sudo -u postgres psql opticaapp_db

# Backup manual
pg_dump -U opticaapp_user opticaapp_db > backup_$(date +%Y%m%d).sql

# Restaurar backup
psql -U opticaapp_user opticaapp_db < backup_YYYYMMDD.sql
```

### Nginx
```bash
# Verificar configuración
sudo nginx -t

# Recargar configuración
sudo systemctl reload nginx

# Ver logs de error
sudo tail -f /var/log/nginx/error.log
```

---

## 📞 Información de Contacto y Acceso

### Credenciales de Acceso
**Servidor SSH:**
- IP: 84.247.129.180
- Usuario: root
- Puerto: 22

**Base de Datos:**
- Host: localhost
- Puerto: 5432
- Database: opticaapp_db
- Usuario: opticaapp_user

**Django Admin:**
- URL: http://84.247.129.180/admin/
- Superusuario: (mantiene credenciales originales)

---

## ✅ Checklist de Finalización

- [x] Servidor Contabo configurado
- [x] PostgreSQL instalado y configurado
- [x] Nginx funcionando como proxy reverso
- [x] Django corriendo con PM2
- [x] Datos migrados desde Render
- [x] WhatsApp Baileys instalado
- [x] API Keys configuradas
- [x] QR Code funcionando
- [x] Envío de mensajes probado exitosamente
- [x] Sesión persiste correctamente
- [x] Logs configurados
- [ ] SSL/HTTPS instalado (PENDIENTE)
- [ ] Dominio configurado (PENDIENTE)
- [ ] DEBUG=False (PENDIENTE)
- [ ] Media files migrados (PENDIENTE)

---

**Fin de la documentación - 5 de Enero de 2026**
