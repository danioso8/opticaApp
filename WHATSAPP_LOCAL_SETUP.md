# 📱 WhatsApp Bot Gratuito - Sin Servicios de Pago

## 🎯 Ventajas de Esta Solución

✅ **100% GRATIS** - No necesitas Twilio ni servicios de pago
✅ **Tu propio número** - Usa cualquier número de WhatsApp
✅ **Sin límites** - Envía mensajes ilimitados
✅ **Auto-hospedado** - Todo corre en tu servidor
✅ **Código abierto** - Usa la librería Baileys

## 📋 Requisitos

- Node.js 16 o superior
- Un número de WhatsApp (puede ser tu número personal o uno nuevo)
- Python 3.7+

## 🚀 Instalación y Configuración

### 1️⃣ Instalar Node.js

Si no tienes Node.js, descárgalo de: https://nodejs.org/

Verifica la instalación:
```bash
node --version
npm --version
```

### 2️⃣ Instalar Dependencias del Bot

```bash
cd whatsapp-bot
npm install
```

### 3️⃣ Iniciar el Bot de WhatsApp

```bash
npm start
```

Verás algo como:
```
🚀 ================================
   Servidor WhatsApp Bot iniciado
   http://localhost:3000
================================

📱 Para conectar WhatsApp, ve a:
   http://localhost:3000/qr
```

### 4️⃣ Conectar tu WhatsApp

1. Abre tu navegador y ve a: **http://localhost:3000/qr**
2. Se mostrará un código QR
3. En tu teléfono:
   - Abre WhatsApp
   - Ve a **⋮ Menú** → **Dispositivos vinculados**
   - Toca **Vincular un dispositivo**
   - Escanea el código QR

¡Listo! Verás: **✅ ¡Conectado a WhatsApp exitosamente!**

### 5️⃣ Configurar Django para Usar el Bot Local

Edita `apps/appointments/whatsapp_local.py` (ya está creado) y asegúrate de que esté configurado:

```python
# En settings.py
WHATSAPP_API_URL = 'http://localhost:3000'
```

### 6️⃣ Actualizar el Serializer

Cambia en `apps/appointments/serializers.py`:

```python
# ANTES (Twilio):
from .whatsapp import notify_new_appointment as send_whatsapp

# DESPUÉS (Bot local):
from .whatsapp_local import notify_new_appointment as send_whatsapp
```

## 🧪 Probar el Sistema

### Opción 1: Desde el Dashboard
1. Ve a http://127.0.0.1:8000/agendar/
2. Agenda una cita con tu número de WhatsApp
3. Recibirás el mensaje automáticamente

### Opción 2: Desde la Consola de Django
```python
python manage.py shell

from apps.appointments.models import Appointment
from apps.appointments.whatsapp_local import whatsapp_notifier

# Obtener una cita
cita = Appointment.objects.first()

# Enviar notificación
whatsapp_notifier.send_appointment_confirmation(cita)
```

### Opción 3: Enviar Mensaje de Prueba Directo
```bash
# Con curl (PowerShell)
Invoke-RestMethod -Uri "http://localhost:3000/send-message" -Method POST -ContentType "application/json" -Body '{"chatId":"573001234567@c.us","message":"Hola desde OCEANO OPTICO"}'

# Con Postman
POST http://localhost:3000/send-message
Body (JSON):
{
  "chatId": "573001234567@c.us",
  "message": "Mensaje de prueba"
}
```

## 📊 API del Bot

El servidor Node.js expone estos endpoints:

### `GET /qr`
Muestra el código QR para vincular WhatsApp

### `GET /status`
```json
{
  "connected": true,
  "hasQR": false
}
```

### `POST /send-message`
```json
{
  "chatId": "573001234567@c.us",
  "message": "Tu mensaje aquí"
}
```

### `GET /health`
```json
{
  "status": "ok",
  "connected": true,
  "timestamp": "2025-11-29T18:30:00.000Z"
}
```

## 🔧 Mantener el Bot Corriendo

### En Desarrollo
Simplemente ejecuta:
```bash
npm start
```

### En Producción (Linux/Mac)
Usa PM2 para mantener el proceso corriendo:
```bash
npm install -g pm2
pm2 start server.js --name whatsapp-bot
pm2 startup
pm2 save
```

### En Producción (Windows)
Usa pm2-windows-service:
```bash
npm install -g pm2
npm install -g pm2-windows-service
pm2-service-install
pm2 start server.js --name whatsapp-bot
```

## 🛠️ Troubleshooting

### "Servidor WhatsApp no está corriendo"
- Asegúrate de que `npm start` esté ejecutándose en la carpeta `whatsapp-bot/`
- Verifica que el puerto 3000 esté libre

### "WhatsApp no está conectado"
- Ve a http://localhost:3000/qr y escanea el código QR nuevamente
- Si el código QR no aparece, elimina la carpeta `auth_info/` y reinicia

### "Error al enviar mensaje"
- Verifica que el número tenga WhatsApp instalado
- El formato del número debe ser: `573001234567@c.us`
- Asegúrate de que el bot esté conectado: http://localhost:3000/status

### "Session closed"
- Si WhatsApp cierra la sesión, simplemente escanea el QR de nuevo
- Esto puede pasar si cierras WhatsApp o desvinculas el dispositivo

## 🔒 Seguridad

⚠️ **Importante:**
- La carpeta `auth_info/` contiene las credenciales de tu WhatsApp
- NO compartas esta carpeta con nadie
- NO la subas a Git (ya está en `.gitignore`)
- Si pierdes esta carpeta, tendrás que volver a escanear el QR

## 📱 Formato de Números

El bot acepta automáticamente estos formatos:
- `3001234567` → Se convierte a `573001234567@c.us`
- `573001234567` → Se convierte a `573001234567@c.us`

Para otros países, cambia el código `57` (Colombia) por el tuyo en `whatsapp_local.py`.

## 🆚 Comparación: Twilio vs Bot Local

| Característica | Twilio | Bot Local |
|---|---|---|
| **Costo** | ~$0.005/mensaje | ✅ **GRATIS** |
| **Límites** | Según tu plan | ✅ **Ilimitado** |
| **Setup** | Complejo | ✅ **Simple** |
| **Tu número** | ❌ Sandbox | ✅ **Sí** |
| **Requiere internet** | ✅ Sí | ✅ Sí |
| **Hosting** | Cloud | Tu servidor |

## 🎉 ¡Listo para Usar!

Ahora cuando alguien agende una cita en http://127.0.0.1:8000/agendar/, recibirá automáticamente un mensaje de WhatsApp sin costos adicionales.

## 📚 Recursos

- [Baileys GitHub](https://github.com/WhiskeySockets/Baileys)
- [Express.js Docs](https://expressjs.com/)
- [PM2 Docs](https://pm2.keymetrics.io/)
