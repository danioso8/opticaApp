# Guía Rápida: Despliegue del Sistema de Verificación de Email en Render

## ⚡ Pasos para Producción

### 1. Configurar Variables de Entorno en Render

Ve a tu servicio en Render → **Environment** y agrega/actualiza:

```bash
# Email Configuration (OBLIGATORIO)
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password_de_gmail
DEFAULT_FROM_EMAIL=OpticaApp <noreply@tudominio.com>

# Opcional - Si quieres cambiar el servidor SMTP
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
```

### 2. Obtener App Password de Gmail

Si usas Gmail, necesitas un **App Password**:

1. Ve a tu cuenta de Google: https://myaccount.google.com/security
2. Activa la verificación en 2 pasos (si no está activada)
3. Ve a "App passwords" (Contraseñas de aplicaciones)
4. Genera una nueva contraseña para "Mail"
5. Usa esa contraseña de 16 caracteres en `EMAIL_HOST_PASSWORD`

**⚠ Importante:** NO uses tu contraseña normal de Gmail, usa el App Password.

### 3. Ejecutar Migraciones en Render

Una vez que el código esté en Render:

```bash
# En el Shell de Render
python manage.py migrate users
```

Esto creará las tablas:
- `users_userprofile`
- `users_emailverificationtoken`

### 4. Migrar Usuarios Existentes

Si ya tienes usuarios en producción:

```bash
# En el Shell de Render
python migrate_users_verification.py

# Cuando pregunte, escribe 's' y Enter
```

Esto creará perfiles para todos los usuarios existentes y los marcará como verificados automáticamente.

### 5. Verificar que Todo Funciona

```bash
# En el Shell de Render
python test_email_verification.py
```

Deberías ver:
- ✓ Modelos creados correctamente
- ✓ EmailVerificationMiddleware activo
- ✓ Configuración de email correcta
- Todos los usuarios existentes con perfil verificado

## 🧪 Probar el Sistema

### Opción 1: Registro de Usuario Nuevo

1. Ve a `/organizations/register/`
2. Registra un nuevo usuario
3. Deberías ver: "Hemos enviado un correo a tu email"
4. Revisa la bandeja de entrada del email registrado
5. Haz clic en el enlace de verificación
6. Deberías ver: "¡Tu correo ha sido verificado!"
7. Inicia sesión normalmente

### Opción 2: Verificar Logs

Si el email no llega:

```bash
# En Render Shell
python manage.py shell

from django.core.mail import send_mail
send_mail(
    'Test Email',
    'This is a test',
    'noreply@tudominio.com',
    ['tu_email_real@gmail.com'],
    fail_silently=False,
)
```

Si hay error, verás el mensaje de error exacto.

## 🔧 Solución de Problemas

### Problema: "Email no se envía"

**Causa:** Credenciales incorrectas o App Password no configurado

**Solución:**
1. Verifica `EMAIL_HOST_USER` y `EMAIL_HOST_PASSWORD` en Render
2. Usa App Password, no contraseña normal de Gmail
3. Verifica que la cuenta de Gmail tenga verificación en 2 pasos activa

### Problema: "SMTPAuthenticationError"

**Causa:** Gmail bloqueando el acceso

**Solución:**
1. Ve a: https://myaccount.google.com/lesssecureapps
2. Activa "Permitir aplicaciones menos seguras" (solo si NO usas App Password)
3. **Mejor opción:** Usa App Password en lugar de esto

### Problema: "Usuarios no pueden acceder después de verificar"

**Causa:** `is_active` no se está actualizando

**Solución:**
```bash
# En Render Shell
python manage.py shell

from django.contrib.auth.models import User
user = User.objects.get(username='username_del_usuario')
user.is_active = True
user.save()
```

### Problema: "Token inválido"

**Causa:** Token expirado (más de 24 horas)

**Solución:**
- Usuario debe usar: `/users/verification/resend/`
- Ingresa su email y recibirá un nuevo token

## 📊 Monitoreo

### Ver usuarios no verificados

```python
# Render Shell
from django.contrib.auth.models import User
from apps.users.email_verification_models import UserProfile

unverified = User.objects.filter(
    profile__is_email_verified=False
).count()
print(f"Usuarios sin verificar: {unverified}")
```

### Ver tokens pendientes

```python
# Render Shell
from apps.users.email_verification_models import EmailVerificationToken

pending = EmailVerificationToken.objects.filter(
    is_used=False
).count()
print(f"Tokens pendientes: {pending}")
```

## 🚀 Mejores Prácticas

### 1. Backup de Base de Datos
Antes de desplegar, haz backup:
```bash
pg_dump DATABASE_URL > backup.sql
```

### 2. Probar en Local Primero
```bash
# En local
python test_email_verification.py
# Si todo está OK, despliega a Render
```

### 3. Despliegue Gradual
1. Despliega el código
2. Ejecuta migraciones
3. Migra usuarios existentes
4. Prueba con un usuario nuevo
5. Monitorea logs por 24 horas

### 4. Configurar Dominio Personalizado
Para emails profesionales, configura un dominio:
- Usa SendGrid, Mailgun o Amazon SES
- Configura SPF, DKIM, DMARC
- Mejora la entregabilidad de emails

## 📝 Checklist de Despliegue

- [ ] Variables de entorno configuradas en Render
- [ ] App Password de Gmail generado
- [ ] Código subido a GitHub/repositorio
- [ ] Migraciones ejecutadas (`migrate users`)
- [ ] Usuarios existentes migrados (`migrate_users_verification.py`)
- [ ] Test de email enviado exitosamente
- [ ] Registro de usuario nuevo probado
- [ ] Verificación de email probada
- [ ] Login después de verificación probado
- [ ] Logs monitoreados sin errores

## 🆘 Soporte

Si tienes problemas:

1. **Revisa logs de Render:** Render Dashboard → Logs
2. **Ejecuta test:** `python test_email_verification.py`
3. **Verifica configuración:** Revisa variables de entorno
4. **Prueba email manual:** Usa el ejemplo de shell de Django
5. **Revisa documentación completa:** `EMAIL_VERIFICATION_SYSTEM.md`

## 🔐 Seguridad en Producción

✅ **Configurado:**
- Tokens UUID imposibles de predecir
- Expiración de 24 horas
- Uso único de tokens
- Middleware protegiendo rutas
- HTTPS en Render (automático)

⚠ **Recomendaciones Adicionales:**
- Usa SendGrid/Mailgun para producción (más confiable que Gmail)
- Configura rate limiting para registro
- Monitorea intentos fallidos
- Configura alertas para errores de email

## 📧 Alternativas a Gmail

### SendGrid (Recomendado para producción)
```bash
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=tu_sendgrid_api_key
```

### Mailgun
```bash
EMAIL_HOST=smtp.mailgun.org
EMAIL_PORT=587
EMAIL_HOST_USER=postmaster@tu-dominio.mailgun.org
EMAIL_HOST_PASSWORD=tu_mailgun_password
```

### Amazon SES
```bash
EMAIL_HOST=email-smtp.us-east-1.amazonaws.com
EMAIL_PORT=587
EMAIL_HOST_USER=tu_aws_access_key
EMAIL_HOST_PASSWORD=tu_aws_secret_key
```

---

**¡Listo!** El sistema de verificación de email está configurado y funcionando en producción.
