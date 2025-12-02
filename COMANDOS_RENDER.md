# 🚀 COMANDOS PARA EJECUTAR EN RENDER

## 📋 Paso 1: Esperar el Deploy
Render detectará automáticamente el push y comenzará a hacer deploy. Espera a que termine (5-10 minutos).

## 🔧 Paso 2: Ejecutar Migraciones (Si no se ejecutaron automáticamente)

Ve a tu servicio en Render → Shell y ejecuta:

```bash
python manage.py migrate
```

## 🎯 Paso 3: Crear Configuraciones de Notificaciones

Ejecuta este comando en el Shell de Render:

```bash
python manage.py shell
```

Luego copia y pega este código:

```python
from apps.organizations.models import Organization
from apps.appointments.models_notifications import NotificationSettings

# Crear configuraciones para todas las organizaciones
organizations = Organization.objects.all()
print(f"Encontradas {organizations.count()} organizaciones")

for org in organizations:
    settings, created = NotificationSettings.objects.get_or_create(
        organization=org,
        defaults={
            'email_enabled': True,
            'email_from': 'noreply@opticaapp.com',
            'twilio_enabled': False,
            'local_whatsapp_enabled': False,
            'send_confirmation': True,
            'send_reminder': True,
            'send_cancellation': True,
        }
    )
    
    if created:
        print(f"✅ Configuración creada para {org.name}")
    else:
        print(f"ℹ️  Ya existe configuración para {org.name}")

print("\n✅ Setup completado")
exit()
```

## 📧 Paso 4: Configurar Variables de Entorno en Render

Ve a Environment → Add Environment Variable:

### Variables Obligatorias (ya las tienes):
```
DATABASE_URL=postgresql://...
SECRET_KEY=tu_secret_key
DEBUG=False
```

### Variables de Email (GRATIS - Recomendado para empezar):
```
USE_EMAIL_NOTIFICATIONS=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password_gmail
DEFAULT_FROM_EMAIL=noreply@tu-empresa.com
```

**Cómo obtener App Password de Gmail:**
1. Ve a: https://myaccount.google.com/apppasswords
2. Selecciona "Correo" y "Otro dispositivo"
3. Copia la contraseña de 16 dígitos
4. Úsala en `EMAIL_HOST_PASSWORD`

### Variables Opcionales (Información del negocio):
```
BUSINESS_PHONE=+57 300 123 4567
WEBSITE_URL=https://tu-app.onrender.com
```

### Variables de Twilio (Opcional - Para WhatsApp de pago):
```
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=tu_auth_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

## ✅ Paso 5: Redeploy

Después de agregar las variables, Render hará redeploy automáticamente.

## 🎉 Paso 6: Probar el Dashboard

1. Ve a: `https://tu-app.onrender.com/dashboard/login/`
2. Inicia sesión
3. Ve a: **Configuración → WhatsApp Twilio**
4. Verás la interfaz para configurar notificaciones

## 🔍 Paso 7: Verificar que Todo Funciona

Ejecuta en el Shell de Render:

```bash
python manage.py shell
```

```python
from apps.organizations.models import Organization
from apps.appointments.models_notifications import NotificationSettings

# Ver configuración de cada organización
for org in Organization.objects.all():
    settings = NotificationSettings.objects.filter(organization=org).first()
    if settings:
        print(f"\n{org.name}:")
        print(f"  Email: {settings.email_enabled}")
        print(f"  Twilio: {settings.twilio_enabled}")
        print(f"  Método activo: {settings.get_active_method()}")
    else:
        print(f"\n{org.name}: Sin configuración")

exit()
```

## 🚨 Si hay errores:

### Error: "No such table: notificationsettings"
```bash
python manage.py migrate appointments
```

### Error: "No module named 'apps.appointments.models_notifications'"
Verifica que el archivo existe:
```bash
ls -la apps/appointments/models_notifications.py
```

### Ver logs en tiempo real:
En el dashboard de Render, ve a "Logs" para ver qué está pasando.

## 📱 Configuración por Usuario (SaaS):

Cada usuario debe:
1. Ir a **Dashboard → Configuración → WhatsApp Twilio**
2. Elegir método de notificación:
   - **Email**: Gratis, ya funciona si configuraste SMTP
   - **WhatsApp Twilio**: Requiere cuenta Twilio ($15 gratis al registrarse)
3. Guardar configuración
4. Enviar mensaje de prueba

## 💡 Recomendación Inicial:

- **Para empezar**: Usa Email (100% gratis con Gmail)
- **Para producción**: Cada cliente usa su propia cuenta Twilio
- **Para desarrollo**: WhatsApp Local (Baileys) en localhost

## 🎯 Orden de Prioridad del Sistema:

1. **Twilio WhatsApp** (si está configurado y activo)
2. **WhatsApp Local** (solo funciona en desarrollo)
3. **Email SMTP** (fallback, siempre disponible)

---

¿Preguntas? Revisa los logs en Render o ejecuta los comandos de verificación.
