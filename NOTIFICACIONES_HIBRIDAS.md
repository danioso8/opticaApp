# 📧 Sistema de Notificaciones Híbrido - Configuración

## ✅ Sistema Configurado Correctamente

Tu aplicación ahora tiene un **sistema inteligente de notificaciones** que detecta automáticamente el entorno:

- **🏠 Local (Desarrollo)**: WhatsApp con Baileys (Gratis)
- **☁️ Render (Producción)**: Email con Gmail SMTP (Gratis)

---

## 🚀 Cómo Funciona

### Detección Automática

El sistema detecta automáticamente dónde está corriendo:

```python
# En settings.py
USE_EMAIL_NOTIFICATIONS = DEBUG == False  # Auto-detecta producción
```

**Local (`DEBUG=True`):**
- Usa WhatsApp Bot (Baileys)
- Necesitas iniciar: `cd whatsapp-bot && node server.js`
- Escanear QR una vez

**Producción (`DEBUG=False`):**
- Usa Email automáticamente
- No necesita WhatsApp Bot
- Totalmente gratis

---

## 📋 Configuración

### 1. Ejecutar Migración

```bash
python manage.py makemigrations
python manage.py migrate
```

Esto agrega el campo `email` al modelo `Appointment`.

### 2. Configurar Email (Para Producción)

#### Opción A: Gmail (Recomendado - Gratis)

1. **Crear contraseña de aplicación:**
   - Ve a tu cuenta de Google
   - Seguridad → Verificación en dos pasos → Contraseñas de aplicaciones
   - Genera una contraseña

2. **Agregar a `.env`:**
```env
# Email Configuration (Producción)
USE_EMAIL_NOTIFICATIONS=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_de_aplicacion
DEFAULT_FROM_EMAIL=OCEANO OPTICO <tu_email@gmail.com>
```

3. **En Render:**
   - Agregar las mismas variables de entorno
   - El sistema usará Email automáticamente

#### Opción B: SendGrid (Gratis - 100 emails/día)

```env
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=tu_api_key_de_sendgrid
DEFAULT_FROM_EMAIL=OCEANO OPTICO <noreply@tudominio.com>
```

#### Opción C: Mailgun (Gratis - 5000 emails/mes)

```env
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=postmaster@tu-dominio.mailgun.org
EMAIL_HOST_PASSWORD=tu_password_mailgun
DEFAULT_FROM_EMAIL=OCEANO OPTICO <noreply@tudominio.com>
```

---

## 🧪 Probar el Sistema

### Localmente (WhatsApp):

```bash
# Terminal 1 - Iniciar WhatsApp Bot
cd whatsapp-bot
node server.js
# Escanear QR en http://localhost:3000/qr

# Terminal 2 - Iniciar Django
python manage.py runserver
```

**Crear cita de prueba:**
- Ve a: `http://127.0.0.1:8000/agendar/`
- Ingresa tu número de WhatsApp
- ¡Recibirás el mensaje!

### En Producción (Email):

1. **Configurar variables de entorno en Render**
2. **Deploy**
3. **Crear cita con email**
4. **¡Recibirás el email!**

---

## 📱 Actualizar Formulario de Citas

El formulario en tu landing page ahora debe incluir el campo `email`:

```html
<form method="post" action="/api/appointments/book/">
    <input type="text" name="full_name" placeholder="Nombre completo" required>
    <input type="tel" name="phone_number" placeholder="Celular" required>
    <input type="email" name="email" placeholder="Email (opcional)">
    <input type="date" name="appointment_date" required>
    <input type="time" name="appointment_time" required>
    <button type="submit">Agendar Cita</button>
</form>
```

**Nota:** El email es opcional. Si se proporciona, se usará para notificaciones por email. Si no, solo se usará WhatsApp en local.

---

## 🔄 Comportamiento del Sistema

### Cuando se agenda una cita:

**LOCAL:**
```
1. Usuario agenda cita
2. Sistema detecta DEBUG=True
3. Envía WhatsApp al número proporcionado
4. ✅ Cliente recibe WhatsApp
```

**PRODUCCIÓN (Render):**
```
1. Usuario agenda cita con email
2. Sistema detecta DEBUG=False
3. Envía Email a la dirección proporcionada
4. ✅ Cliente recibe Email HTML bonito
```

### Cuando se cancela una cita:

- **Local**: WhatsApp de cancelación
- **Producción**: Email de cancelación

---

## 📊 Ventajas de este Sistema

### ✅ Para Desarrollo:
- WhatsApp gratis con Baileys
- Pruebas realistas
- Sin configuración complicada

### ✅ Para Producción:
- Email 100% gratis
- No necesita bot corriendo
- Profesional y confiable
- Funciona en Render sin problema

### ✅ Escalable:
- Cuando tengas presupuesto, puedes agregar:
  - Twilio WhatsApp ($0.005/mensaje)
  - SendGrid Premium
  - SMS con Twilio

---

## 🎯 Configuración en Render

### Variables de Entorno a Agregar:

```env
# Base
DEBUG=False
USE_EMAIL_NOTIFICATIONS=True

# Email (Gmail - Gratis)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_contraseña_aplicacion
DEFAULT_FROM_EMAIL=OCEANO OPTICO <tu_email@gmail.com>

# Business
BUSINESS_PHONE=300 123 4567
WEBSITE_URL=https://tu-app.onrender.com
```

---

## 🆘 Solución de Problemas

### Email no llega:

1. **Verificar spam/correo no deseado**
2. **Verificar credenciales Gmail:**
   - ¿Tienes verificación en dos pasos activada?
   - ¿Usaste contraseña de aplicación (no tu contraseña normal)?
3. **Ver logs en Render:**
   - Dashboard → Logs
   - Buscar errores de SMTP

### WhatsApp no funciona en local:

1. **Bot corriendo?** `node server.js`
2. **QR escaneado?** `http://localhost:3000/qr`
3. **Número válido?** Formato: 3001234567

---

## 📈 Próximos Pasos (Opcional)

### 1. Recordatorios Automáticos

Configurar Celery para enviar recordatorios 1 día antes:

```python
# En celery.py
@shared_task
def send_appointment_reminders():
    tomorrow = timezone.now().date() + timedelta(days=1)
    appointments = Appointment.objects.filter(
        appointment_date=tomorrow,
        status='confirmed'
    )
    for appointment in appointments:
        notify_appointment_reminder(appointment)
```

### 2. Dual Notification

Enviar AMBOS (Email + WhatsApp):

```python
# En notifications.py
def notify_new_appointment(appointment):
    # Enviar email siempre
    email_notifier.send_appointment_confirmation(appointment)
    
    # Enviar WhatsApp si está disponible
    try:
        whatsapp_notifier.send_appointment_confirmation(appointment)
    except:
        pass
```

---

## ✨ ¡Sistema Completo!

Ahora tienes:
- ✅ WhatsApp gratis en desarrollo
- ✅ Email gratis en producción
- ✅ Auto-detección de entorno
- ✅ Emails HTML bonitos
- ✅ Sin costos adicionales
- ✅ Listo para Render

**¡Tu sistema de notificaciones está 100% operativo!** 🎉
