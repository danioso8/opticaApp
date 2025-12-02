# 🚀 Configuración de Twilio en Render

## 📋 Pasos para configurar WhatsApp con Twilio en Producción

### 1️⃣ Obtener Credenciales de Twilio

1. Ve a [Twilio Console](https://console.twilio.com/)
2. Copia tu **Account SID**
3. Copia tu **Auth Token** (haz clic en "Show")
4. Ve a **WhatsApp Sandbox** o configura un número verificado

### 2️⃣ Configurar Variables de Entorno en Render

Ve a tu servicio en Render → Environment → Add Environment Variable

Agrega las siguientes variables:

```bash
# Base de datos y configuración general
DEBUG=False
SECRET_KEY=tu-secret-key-super-segura-aqui
ALLOWED_HOSTS=tu-app.onrender.com,tudominio.com
DATABASE_URL=postgresql://...  # Ya configurado

# Email (Gmail SMTP - Gratis)
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-app-password-de-gmail
DEFAULT_FROM_EMAIL=OCEANO OPTICO <noreply@oceanooptico.com>

# Twilio WhatsApp (Producción)
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=tu_auth_token_aqui
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Información del negocio
BUSINESS_PHONE=300 123 4567
WEBSITE_URL=https://tu-app.onrender.com
```

### 3️⃣ Configurar WhatsApp Sandbox de Twilio (Desarrollo)

Si estás usando el Sandbox gratuito de Twilio:

1. Ve a [WhatsApp Sandbox](https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)
2. Escanea el código QR con WhatsApp
3. Envía el código de activación que te aparece (ej: `join <codigo>`)
4. Usa el número: `whatsapp:+14155238886`

**Limitaciones del Sandbox:**
- Solo puedes enviar a números que se hayan unido al sandbox
- Debes renovar la conexión cada 24 horas
- Los mensajes tienen el prefijo "Sent from your Twilio trial account"

### 4️⃣ Usar un Número Verificado (Producción Real)

Para producción sin limitaciones:

1. Compra un número de Twilio con capacidades de WhatsApp
2. Verifica tu cuenta de negocio de WhatsApp
3. Configura tu plantilla de mensajes
4. Actualiza `TWILIO_WHATSAPP_FROM` con tu número: `whatsapp:+1234567890`

**Costos:**
- Mensajes salientes: ~$0.005 USD por mensaje
- Número mensual: ~$15 USD/mes

### 5️⃣ Configurar desde el Dashboard

Después del deploy, entra a tu dashboard:

1. Ve a **Configuración** → **WhatsApp Twilio**
2. Activa **WhatsApp con Twilio**
3. Ingresa:
   - Account SID
   - Auth Token
   - Número WhatsApp (formato: `whatsapp:+14155238886`)
4. Haz clic en **Sincronizar WhatsApp**
5. Prueba enviando un mensaje de prueba

### 6️⃣ Verificar que Funciona

```bash
# Ver logs en Render
# Ve a tu servicio → Logs

# Busca mensajes como:
WhatsApp enviado a 3001234567 - SID: SMxxxxxxxxx
Notificación de confirmación enviada para cita #123
```

### 7️⃣ Sistema de Prioridad

El sistema usa notificaciones en este orden:

1. **Twilio WhatsApp** (si está configurado y activado)
2. **Email** (si está configurado)
3. **WhatsApp Local** (solo desarrollo)

### 8️⃣ Costos Estimados

**Opción 1 - Solo Email (GRATIS):**
- Email SMTP con Gmail: $0
- Ilimitado

**Opción 2 - Twilio Sandbox (GRATIS con límites):**
- $15 de crédito gratis al registrarte
- ~3,000 mensajes gratis
- Solo a números del sandbox

**Opción 3 - Twilio Producción:**
- $15/mes por número de WhatsApp
- $0.005 por mensaje saliente
- Sin limitaciones
- Para 1000 mensajes/mes: ~$20 USD total

### 9️⃣ Alternativas Gratuitas para Producción

Si no quieres usar Twilio, el sistema automáticamente usará **Email** que es:
- ✅ 100% Gratis
- ✅ Funciona en Render
- ✅ Plantillas HTML bonitas
- ✅ Sin límites (con Gmail SMTP)

## 🔧 Comandos Útiles

```bash
# Ver configuración actual
python manage.py shell
>>> from apps.appointments.models_notifications import NotificationSettings
>>> settings = NotificationSettings.objects.first()
>>> print(settings.get_active_method())

# Probar notificaciones
python manage.py shell
>>> from apps.appointments.notifications import get_notifier
>>> notifier = get_notifier()
>>> print(f"Método activo: {notifier.__class__.__name__}")
```

## ⚠️ Importante

- **Nunca** commits las credenciales de Twilio en el código
- Usa variables de entorno en Render
- El sistema detecta automáticamente si está en desarrollo o producción
- En desarrollo usa WhatsApp Local (gratis)
- En producción usa Twilio o Email según configuración

## 📞 Soporte

Si tienes problemas:
1. Revisa los logs en Render
2. Verifica que las variables de entorno estén correctas
3. Prueba enviando un mensaje de prueba desde el dashboard
4. Verifica que tu cuenta de Twilio tenga crédito
