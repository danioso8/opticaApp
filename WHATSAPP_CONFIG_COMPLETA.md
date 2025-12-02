# 🌊 OCEANO OPTICO - Configuración WhatsApp Bot 👓

## ✅ Sistema Configurado

El bot de WhatsApp ya está configurado y listo para enviar notificaciones automáticas.

---

## 🚀 Inicio Rápido

### 1️⃣ Iniciar el Bot de WhatsApp

```powershell
cd whatsapp-bot
npm start
```

### 2️⃣ Conectar tu WhatsApp

1. Abre en el navegador: **http://localhost:3000/qr**
2. Escanea el código QR con tu WhatsApp:
   - Abre WhatsApp en tu celular
   - Ve a **Menú (⋮) → Dispositivos vinculados**
   - Toca **Vincular un dispositivo**
   - Escanea el código QR

### 3️⃣ Probar el Envío

```powershell
python test_whatsapp.py
```

---

## 📋 Notificaciones Automáticas Configuradas

El sistema ahora envía WhatsApp automáticamente en estos casos:

### ✅ Nueva Cita Agendada
**Cuándo:** Al crear una cita desde la landing page o dashboard
**Mensaje:** Confirmación con fecha, hora y dirección

```
👓 OCEANO OPTICO

¡Hola Juan Pérez!

✅ Tu cita ha sido agendada exitosamente:

📅 Fecha: 02/12/2025
🕐 Hora: 10:00 AM
📍 Dirección: Calle 123, Barrio Centro, Bogotá

💡 Recomendaciones:
• Llega 10 minutos antes
• Trae tu documento de identidad
• Si usas lentes, tráelos contigo

❓ ¿Necesitas cancelar o reagendar?
Llámanos al: 300 123 4567

¡Te esperamos! 😊
```

### ❌ Cita Cancelada
**Cuándo:** Al cambiar el estado de una cita a "Cancelada"
**Mensaje:** Notificación de cancelación con opciones para reagendar

```
👓 OCEANO OPTICO

Hola Juan Pérez,

Tu cita del día 02/12/2025 a las 10:00 AM ha sido cancelada.

Si deseas reagendar, contáctanos:
📞 300 123 4567

O agenda en línea:
🌐 http://127.0.0.1:8000/agendar/

¡Gracias! 😊
```

### 🔔 Recordatorio (Próximamente)
**Cuándo:** 1 día antes de la cita
**Mensaje:** Recordatorio amigable

---

## 🧪 Probar Notificaciones

### Opción 1: Script de Prueba
```powershell
python test_whatsapp.py
```

Opciones disponibles:
1. **Enviar mensaje de prueba** - Envía un mensaje simple a tu número
2. **Enviar notificación de cita** - Simula una notificación de cita real
3. **Verificar conexión** - Verifica el estado del bot

### Opción 2: Crear una Cita de Prueba

1. Inicia Django:
```powershell
python manage.py runserver
```

2. Ve a: **http://127.0.0.1:8000/agendar/**

3. Agenda una cita con TU número de WhatsApp

4. ¡Recibirás el mensaje automáticamente! 📱

---

## ⚙️ Configuración

### Variables de Entorno (.env)

```env
# WhatsApp Bot Local (Gratuito)
WHATSAPP_API_URL=http://localhost:3000

# Datos de tu negocio (aparecen en los mensajes)
BUSINESS_PHONE=300 123 4567
WEBSITE_URL=http://127.0.0.1:8000
```

### Formato de Números

El sistema acepta números en estos formatos:
- `3001234567` → Se convierte a `573001234567@c.us`
- `573001234567` → Se usa directamente
- `+573001234567` → Se limpia y usa

**Código de país:** Por defecto Colombia (57)

---

## 🔍 Verificar Estado del Bot

### Ver logs en tiempo real:
El terminal donde ejecutaste `npm start` mostrará:

```
✅ ¡Conectado a WhatsApp exitosamente!
🚀 Bot listo para enviar mensajes
✅ Mensaje enviado a 573001234567@c.us
```

### API de Estado:
```
GET http://localhost:3000/status
```

Respuesta:
```json
{
  "connected": true,
  "hasQR": false
}
```

### API de Salud:
```
GET http://localhost:3000/health
```

---

## 📱 Endpoints del Bot

### 1. Ver Código QR
```
GET http://localhost:3000/qr
```

### 2. Verificar Estado
```
GET http://localhost:3000/status
```

### 3. Enviar Mensaje
```
POST http://localhost:3000/send-message
Content-Type: application/json

{
  "chatId": "573001234567@c.us",
  "message": "Hola desde el bot"
}
```

---

## 🐛 Solución de Problemas

### ❌ "Servidor WhatsApp no está corriendo"

**Solución:**
```powershell
cd whatsapp-bot
npm start
```

### ❌ "WhatsApp no está conectado"

**Solución:**
1. Ve a: http://localhost:3000/qr
2. Escanea el código QR con tu WhatsApp
3. Espera el mensaje: "✅ ¡Conectado a WhatsApp exitosamente!"

### ❌ "Conexión cerrada. Reconectando: true"

**Causa:** El bot no ha sido autenticado aún

**Solución:** Escanea el código QR (paso 2)

### ⚠️ El mensaje no llega

Verifica:
1. ✅ Bot conectado (ver logs)
2. ✅ Número válido de WhatsApp
3. ✅ Número tiene WhatsApp activo
4. ✅ No bloqueaste el número del bot

### ⚠️ Error de formato de número

El sistema acepta:
- ✅ `3001234567`
- ✅ `573001234567`
- ✅ `+573001234567`
- ❌ `300-123-4567`
- ❌ `300 123 4567`

---

## 🔧 Mantenimiento

### Reiniciar el Bot

Si necesitas reiniciar:
```powershell
# Ctrl+C para detener
cd whatsapp-bot
npm start
```

El bot recordará la sesión (no necesitas escanear QR nuevamente).

### Desconectar WhatsApp

Para desconectar permanentemente:
```powershell
cd whatsapp-bot
rm -rf auth_info
npm start
# Escanear QR nuevamente
```

### Ver Logs de Django

Para ver si se envían los mensajes:
```powershell
python manage.py runserver
```

Verás en consola:
```
WhatsApp enviado a 3001234567
WhatsApp de confirmación enviado a 3001234567
```

---

## 🎯 Flujo Completo

```
1. Cliente agenda cita
   ↓
2. Django guarda cita
   ↓
3. Signal detecta nueva cita
   ↓
4. whatsapp_local.py envía mensaje
   ↓
5. Bot de Node.js (Baileys) envía a WhatsApp
   ↓
6. Cliente recibe confirmación 📱
```

---

## 📝 Archivos Clave

```
whatsapp-bot/
  ├── server.js          # Servidor del bot
  ├── package.json       # Dependencias
  └── auth_info/         # Sesión guardada (no subir a git)

apps/appointments/
  ├── whatsapp_local.py  # Cliente Python
  ├── signals.py         # Envío automático
  └── views.py          # Integración en vistas

test_whatsapp.py        # Script de pruebas
```

---

## ✨ Próximas Mejoras

- [ ] Recordatorios automáticos (1 día antes)
- [ ] Recordatorios matutinos (día de la cita)
- [ ] Mensajes personalizados por organización
- [ ] Botón de confirmación de asistencia
- [ ] Integración con Django Admin

---

## 🆘 Soporte

¿Problemas? Ejecuta:
```powershell
python test_whatsapp.py
```

Selecciona opción 3 para diagnóstico completo.

---

## 🎉 ¡Listo!

Tu sistema de notificaciones WhatsApp está completamente configurado y funcionando.

**Pasos finales:**
1. ✅ Bot iniciado: `cd whatsapp-bot && npm start`
2. ✅ QR escaneado: http://localhost:3000/qr
3. ✅ Prueba realizada: `python test_whatsapp.py`
4. ✅ Cita de prueba creada

**¡Todo funcionando! 🚀**
