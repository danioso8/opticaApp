# 🚀 SINCRONIZACIÓN EN RENDER - GUÍA PASO A PASO

## ✅ Estado Actual
- ✅ Código subido a GitHub (commit: 2181814)
- ✅ Sistema multi-tenant completamente funcional
- ✅ Dashboard de notificaciones con UI moderna
- ✅ Render detectará el cambio automáticamente

---

## 📋 PARTE 1: Esperar Deploy Automático

### 1. Ve a tu Dashboard de Render
- https://dashboard.render.com/

### 2. Busca tu servicio web (OpticaApp)
- Click en tu servicio

### 3. Verifica el Deploy
En la pestaña "Events" verás:
```
Deploy started
Building...
Deploying...
Live ✅
```

**Tiempo estimado**: 5-10 minutos

⚠️ **NO CONTINÚES hasta que el deploy esté "Live"**

---

## 🔧 PARTE 2: Configurar Variables de Entorno

### Paso 1: Ir a Environment Variables
En tu servicio de Render:
1. Click en **"Environment"** (menú izquierdo)
2. Click en **"Add Environment Variable"**

### Paso 2: Agregar Variables OBLIGATORIAS

Ya debes tener estas (si no, agrégalas):

```plaintext
DATABASE_URL=postgresql://user:password@host/database
SECRET_KEY=tu_secret_key_aqui
DEBUG=False
ALLOWED_HOSTS=tu-app.onrender.com
```

### Paso 3: Configurar Email (GRATIS - Recomendado)

Para tener notificaciones funcionando de inmediato:

```plaintext
USE_EMAIL_NOTIFICATIONS=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=xxxx xxxx xxxx xxxx
DEFAULT_FROM_EMAIL=noreply@opticaapp.com
```

#### 📧 Cómo obtener App Password de Gmail:
1. Ve a: https://myaccount.google.com/apppasswords
2. Si no ves la opción, primero activa 2FA en tu cuenta
3. Selecciona:
   - **App**: Correo
   - **Device**: Otro (personalizado) → escribe "OpticaApp"
4. Click en **Generar**
5. Copia la contraseña de 16 dígitos (con espacios o sin espacios)
6. Úsala en `EMAIL_HOST_PASSWORD`

### Paso 4: Variables Opcionales (Información del Negocio)

```plaintext
BUSINESS_PHONE=+57 300 123 4567
WEBSITE_URL=https://tu-app.onrender.com
```

### Paso 5: Variables de Twilio (Opcional - para WhatsApp de pago)

**Solo si quieres usar Twilio como admin:**

```plaintext
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=tu_auth_token_aqui
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

#### 🔑 Cómo obtener credenciales de Twilio:
1. Regístrate: https://www.twilio.com/try-twilio
2. Obtienes **$15 USD gratis**
3. En el dashboard de Twilio:
   - Account SID: `ACxxxxxxx...`
   - Auth Token: Click en "Show" para verlo
4. Para WhatsApp:
   - Ve a: Console → Messaging → Try it out → WhatsApp
   - Usa el sandbox: `whatsapp:+14155238886`
   - Para activarlo: Envía "JOIN <código>" desde tu WhatsApp

### Paso 6: Guardar y Redeploy

1. Después de agregar TODAS las variables, click **"Save Changes"**
2. Render hará **redeploy automáticamente**
3. Espera 3-5 minutos

---

## 🗄️ PARTE 3: Ejecutar Comandos en Render

### Paso 1: Abrir Shell

En tu servicio de Render:
1. Click en **"Shell"** (menú superior derecho)
2. Se abrirá una terminal

### Paso 2: Verificar Migraciones

```bash
python manage.py showmigrations
```

Si ves `[ ]` (sin X), ejecuta:

```bash
python manage.py migrate
```

Deberías ver:
```
Running migrations:
  Applying appointments.0004_appointment_email... OK
  Applying appointments.0005_notificationsettings... OK
  Applying organizations.0002_auto_20251202_1020... OK
  Applying organizations.0003_auto_20251202_1024... OK
  Applying organizations.0004_organization_neighborhood... OK
  Applying users.0001_initial... OK
```

### Paso 3: Crear Configuraciones de Notificaciones

En el Shell de Render, ejecuta:

```bash
python manage.py shell
```

Luego copia y pega este código completo:

```python
from apps.organizations.models import Organization
from apps.appointments.models_notifications import NotificationSettings

# Crear configuraciones para todas las organizaciones
organizations = Organization.objects.all()
print(f"\n{'='*60}")
print(f"📊 Organizaciones encontradas: {organizations.count()}")
print(f"{'='*60}\n")

for org in organizations:
    settings, created = NotificationSettings.objects.get_or_create(
        organization=org,
        defaults={
            # Email habilitado por defecto (gratis)
            'email_enabled': True,
            'email_from': 'noreply@opticaapp.com',
            
            # Twilio deshabilitado (cada usuario lo configura)
            'twilio_enabled': False,
            'twilio_account_sid': '',
            'twilio_auth_token': '',
            'twilio_whatsapp_from': 'whatsapp:+14155238886',
            
            # WhatsApp Local deshabilitado (no funciona en Render)
            'local_whatsapp_enabled': False,
            'local_whatsapp_url': 'http://localhost:3000',
            
            # Todas las notificaciones automáticas activas
            'send_confirmation': True,
            'send_reminder': True,
            'send_cancellation': True,
        }
    )
    
    status = "✅ CREADA" if created else "ℹ️  EXISTENTE"
    print(f"{status} - {org.name}")
    print(f"    Owner: {org.owner.username}")
    print(f"    Método activo: {settings.get_active_method()}")
    print()

print(f"{'='*60}")
print("✅ Configuración completada!")
print(f"{'='*60}\n")

# Salir
exit()
```

### Paso 4: Verificar que Todo Funciona

En el Shell, ejecuta:

```bash
python manage.py shell
```

```python
from apps.organizations.models import Organization
from apps.appointments.models_notifications import NotificationSettings

print("\n" + "="*60)
print("🔍 VERIFICACIÓN FINAL")
print("="*60 + "\n")

for org in Organization.objects.all():
    settings = NotificationSettings.objects.filter(organization=org).first()
    if settings:
        print(f"✅ {org.name}:")
        print(f"    Email: {'ON' if settings.email_enabled else 'OFF'}")
        print(f"    Twilio: {'ON' if settings.twilio_enabled else 'OFF'}")
        print(f"    Método: {settings.get_active_method()}")
        print()
    else:
        print(f"❌ {org.name}: Sin configuración\n")

print("="*60 + "\n")
exit()
```

---

## 🌐 PARTE 4: Probar el Dashboard en Producción

### Paso 1: Acceder al Dashboard

Abre tu navegador:
```
https://tu-app.onrender.com/dashboard/login/
```

### Paso 2: Iniciar Sesión

Usa tus credenciales de admin o usuario

### Paso 3: Ir a Configuración de Notificaciones

**Opción A**: Desde el menú
- Sidebar → **Configuración** → **WhatsApp Twilio**

**Opción B**: URL directa
```
https://tu-app.onrender.com/dashboard/configuracion/notificaciones/
```

### Paso 4: Verificar la Interfaz

Deberías ver:
- ✅ 3 tarjetas de colores (Verde, Azul, Cyan)
- ✅ Estado de Conexión arriba
- ✅ Configuración de notificaciones automáticas
- ✅ Método activo mostrando "Email" (si configuraste SMTP)

### Paso 5: Probar Email

1. En la sección **Email (Cyan)**
2. Debe mostrar **"Activo"** en el badge verde
3. Click en **"Enviar Email de Prueba"**
4. Ingresa tu email
5. Click **"Enviar"**
6. Revisa tu bandeja de entrada

**Si llega el email** → ✅ ¡Todo funciona!

---

## 👥 PARTE 5: Configuración por Usuario (SaaS)

### Para que CADA USUARIO configure su propio WhatsApp:

1. **Usuario se registra** en tu app
2. **Va a su Dashboard** → Configuración → WhatsApp Twilio
3. **Activa el método que prefiera**:
   - **Email**: Usa el SMTP global (gratis, ya funciona)
   - **Twilio**: Ingresa SUS credenciales de Twilio
4. **Guarda la configuración**
5. **Sus clientes reciben notificaciones** desde SU cuenta

### Esto significa:
- ✅ Cada usuario tiene su propia tabla `NotificationSettings`
- ✅ Cada uno ingresa sus credenciales de Twilio
- ✅ Las notificaciones usan la cuenta de cada usuario
- ✅ Completamente aislado entre usuarios (multi-tenant)

---

## 🎯 RESUMEN DE LO QUE TIENES

### En Render (Producción):
1. ✅ Email SMTP funcionando (gratis con Gmail)
2. ✅ Sistema multi-tenant configurado
3. ✅ Dashboard de notificaciones moderno
4. ✅ Cada usuario puede configurar su Twilio

### Métodos Disponibles:
- 📧 **Email**: 100% gratis, ya funciona si configuraste SMTP
- 📱 **Twilio WhatsApp**: $0.005/mensaje ($15 gratis al registrarse)
- 💻 **WhatsApp Local**: Solo para desarrollo (localhost)

### Prioridad del Sistema:
1. **Twilio** (si el usuario lo configuró)
2. **WhatsApp Local** (solo local, no en Render)
3. **Email** (fallback, siempre disponible)

---

## 🚨 Troubleshooting

### Error: "No such table: notificationsettings"
```bash
python manage.py migrate appointments
```

### Error: "relation does not exist"
```bash
python manage.py migrate --run-syncdb
```

### El dashboard no carga
1. Verifica que el deploy esté "Live"
2. Checa los logs: Dashboard → Logs
3. Busca errores de importación

### Email no llega
1. Verifica `EMAIL_HOST_PASSWORD` (debe ser App Password, no tu contraseña normal)
2. Verifica que 2FA esté activo en Gmail
3. Checa el log de Render para ver errores SMTP

### Las notificaciones no se envían
1. Ve a: Dashboard → Configuración → WhatsApp Twilio
2. Verifica que al menos un método esté en "Activo" (verde)
3. Verifica que "Enviar confirmación" esté activado
4. Prueba con "Enviar Prueba"

---

## 📞 Soporte

Si algo no funciona:
1. Revisa los **logs en Render**: Dashboard → Logs
2. Ejecuta comandos de verificación en el Shell
3. Prueba localmente primero: `python manage.py runserver`

---

## ✅ Checklist Final

- [ ] Deploy en Render completado (Live)
- [ ] Variables de entorno configuradas
- [ ] Email SMTP funcionando (Gmail App Password)
- [ ] Migraciones ejecutadas
- [ ] NotificationSettings creados
- [ ] Dashboard accesible
- [ ] Interfaz de notificaciones carga correctamente
- [ ] Test de email exitoso
- [ ] Usuarios pueden configurar su Twilio

---

¡Listo! Tu sistema SaaS multi-tenant con notificaciones está **100% operacional** 🚀

Cada usuario podrá configurar su propio método de notificación desde el dashboard.
