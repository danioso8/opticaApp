# 📱 Configuración de Notificaciones por WhatsApp

## 🎯 Descripción
El sistema envía notificaciones automáticas por WhatsApp cuando:
- ✅ Un cliente agenda una cita (confirmación inmediata)
- 🔔 Recordatorio 1 día antes de la cita
- ❌ Se cancela una cita

## 📋 Requisitos Previos
1. Cuenta de Twilio (gratis para pruebas)
2. Número de WhatsApp Business (o usar Sandbox de Twilio para pruebas)

## 🚀 Configuración Paso a Paso

### 1️⃣ Crear Cuenta en Twilio
1. Ve a https://www.twilio.com/try-twilio
2. Regístrate con tu correo
3. Verifica tu cuenta
4. Obtendrás $15 USD de crédito gratis para pruebas

### 2️⃣ Configurar WhatsApp Sandbox (Para Pruebas)
1. En el Dashboard de Twilio, ve a: **Messaging** → **Try it out** → **Send a WhatsApp message**
2. Verás un número de WhatsApp (ej: `+1 415 523 8886`)
3. Desde tu WhatsApp personal, envía el código que te muestra (ej: "join shadow-hello")
4. Recibirás confirmación de que estás conectado al Sandbox

### 3️⃣ Obtener Credenciales
1. En el Dashboard de Twilio, ve a **Account Info**
2. Copia tu **Account SID** (empieza con AC...)
3. Copia tu **Auth Token** (haz clic en "Show" para verlo)

### 4️⃣ Configurar Variables de Entorno
Crea un archivo `.env` en la raíz del proyecto (copiando `.env.example`):

```env
# Twilio WhatsApp Configuration
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=tu_auth_token_aqui
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Business Information
BUSINESS_PHONE=300 123 4567
WEBSITE_URL=http://127.0.0.1:8000
```

**⚠️ IMPORTANTE:** El número `TWILIO_WHATSAPP_FROM` debe incluir el prefijo `whatsapp:+`

### 5️⃣ Instalar Dependencia
```bash
pip install twilio
```

### 6️⃣ Reiniciar el Servidor
```bash
python manage.py runserver
```

## 🧪 Probar las Notificaciones

### Opción 1: Agendar una Cita desde la Landing Page
1. Ve a http://127.0.0.1:8000/agendar/
2. Agenda una cita con TU número de WhatsApp
3. Deberías recibir el mensaje de confirmación

### Opción 2: Probar desde el Shell de Django
```python
python manage.py shell

from apps.appointments.models import Appointment
from apps.appointments.whatsapp import whatsapp_notifier

# Obtener una cita existente
cita = Appointment.objects.first()

# Enviar notificación de prueba
whatsapp_notifier.send_appointment_confirmation(cita)
```

## 📱 Formato de Números

El sistema acepta estos formatos:
- `3001234567` → Se convierte a `whatsapp:+573001234567`
- `573001234567` → Se convierte a `whatsapp:+573001234567`
- `+573001234567` → Se convierte a `whatsapp:+573001234567`

**Código de país por defecto:** Colombia (+57)

## 🌟 Para Producción (WhatsApp Business API)

Cuando tengas WhatsApp Business API aprobado:

1. En Twilio, solicita aprobar tu número para WhatsApp Business
2. Actualiza `TWILIO_WHATSAPP_FROM` con tu número aprobado:
   ```env
   TWILIO_WHATSAPP_FROM=whatsapp:+573001234567
   ```
3. Los usuarios NO necesitarán unirse a un Sandbox
4. Podrás enviar plantillas de mensajes aprobadas por WhatsApp

## 💰 Costos

### Twilio Sandbox (Pruebas)
- ✅ **GRATIS**
- Limitación: Los usuarios deben unirse al Sandbox primero
- $15 USD de crédito inicial

### Twilio con WhatsApp Business API
- 💵 **~$0.005 USD por mensaje** (varía por país)
- Sin límite de usuarios
- Mensajes instantáneos sin necesidad de Sandbox

## 🔍 Logs y Depuración

Los logs de WhatsApp se guardan en la consola del servidor:
- ✅ `WhatsApp enviado a 3001234567 - SID: SM...`
- ❌ `Error al enviar WhatsApp: ...`
- ⚠️ `Twilio no está configurado. Las notificaciones por WhatsApp están deshabilitadas.`

## 🛠️ Troubleshooting

### "Twilio no está configurado"
- Verifica que las variables `TWILIO_ACCOUNT_SID` y `TWILIO_AUTH_TOKEN` estén en el `.env`
- Reinicia el servidor después de agregar las variables

### "Error 21211: Invalid 'To' Phone Number"
- Asegúrate de que el número esté unido al Sandbox de Twilio
- Desde tu WhatsApp, envía el código de activación al número sandbox

### "Error 20003: Authentication Error"
- Verifica que tu `TWILIO_ACCOUNT_SID` y `TWILIO_AUTH_TOKEN` sean correctos
- No incluyas comillas en el archivo `.env`

### "No recibo mensajes"
- Verifica que hayas unido tu número al Sandbox
- Revisa los logs de Twilio en: https://www.twilio.com/console/sms/logs
- Verifica que el número tenga WhatsApp instalado

## 📚 Recursos Adicionales

- [Twilio WhatsApp API Docs](https://www.twilio.com/docs/whatsapp)
- [Twilio Python SDK](https://www.twilio.com/docs/libraries/python)
- [WhatsApp Business Policy](https://www.whatsapp.com/legal/business-policy)

## 🎨 Personalizar Mensajes

Los mensajes están en: `apps/appointments/whatsapp.py`

Puedes personalizar:
- `send_appointment_confirmation()` - Confirmación de cita
- `send_appointment_reminder()` - Recordatorio
- `send_appointment_cancelled()` - Cancelación

## ✅ Checklist de Configuración

- [ ] Cuenta de Twilio creada
- [ ] WhatsApp Sandbox activado
- [ ] Número personal unido al Sandbox
- [ ] Variables `TWILIO_*` configuradas en `.env`
- [ ] Dependencia `twilio` instalada
- [ ] Servidor reiniciado
- [ ] Cita de prueba agendada
- [ ] Mensaje de WhatsApp recibido ✨
