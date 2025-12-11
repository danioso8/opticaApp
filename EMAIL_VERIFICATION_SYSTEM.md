# Sistema de Verificación de Email

## Descripción General

El sistema de verificación de email garantiza que los usuarios que se registran en OpticaApp tengan acceso a la dirección de correo electrónico que proporcionaron. Los usuarios no pueden acceder al dashboard hasta que verifiquen su email.

## Características

### 1. **Registro con Verificación**
- Al registrarse, el usuario recibe un correo con un enlace de verificación
- El usuario es creado con `is_active=False`
- No se permite login automático hasta verificar el email
- El token de verificación expira en 24 horas

### 2. **Modelos de Base de Datos**

#### UserProfile
```python
- user: OneToOneField (User)
- is_email_verified: Boolean
- email_verified_at: DateTime
- phone: CharField (opcional)
```

#### EmailVerificationToken
```python
- user: ForeignKey (User)
- token: UUID (único, auto-generado)
- created_at: DateTime
- expires_at: DateTime (24 horas desde creación)
- is_used: Boolean
```

### 3. **Flujo de Verificación**

```
1. Usuario se registra → Cuenta creada (inactiva)
2. Sistema envía email con enlace único
3. Usuario hace clic en el enlace
4. Sistema valida el token:
   - ¿Existe el token?
   - ¿Ya fue usado?
   - ¿Está expirado?
5. Si es válido:
   - Marca token como usado
   - Activa el usuario (is_active=True)
   - Actualiza perfil (is_email_verified=True)
   - Registra fecha de verificación
6. Usuario puede iniciar sesión
```

### 4. **Middleware de Protección**

**EmailVerificationMiddleware** bloquea el acceso a áreas protegidas si el email no está verificado.

**URLs Exentas:**
- `/users/verify/*` - Proceso de verificación
- `/users/verification/*` - Páginas de estado
- `/accounts/logout/` - Cerrar sesión
- `/organizations/logout/` - Cerrar sesión
- `/static/*` - Archivos estáticos
- `/media/*` - Archivos multimedia
- `/admin/*` - Panel de administración
- `/api/*` - APIs (manejan su propia lógica)

### 5. **Vistas Disponibles**

#### verify_email(request, token)
**URL:** `/users/verify/<uuid>/`
- Verifica el token UUID
- Activa la cuenta del usuario
- Redirige al login con mensaje de éxito

#### verification_pending(request)
**URL:** `/users/verification/pending/`
- Muestra página informativa post-registro
- Instrucciones para verificar email
- Opción para reenviar email

#### resend_verification_email(request)
**URL:** `/users/verification/resend/`
- Formulario para reenviar email de verificación
- Invalida tokens anteriores
- Genera nuevo token y envía email

### 6. **Plantilla de Email**

**Template:** `apps/users/templates/users/emails/verify_email.html`

**Contenido:**
- Diseño responsive con gradiente moderno
- Botón principal de verificación
- Enlace alternativo para copiar/pegar
- Advertencia de expiración (24 horas)
- Información de contacto

**Variables de contexto:**
```python
{
    'user': User object,
    'verification_url': URL completa de verificación,
    'site_name': 'OpticaApp'
}
```

### 7. **Configuración SMTP Requerida**

En `config/settings.py`:

```python
# Configuración de Email
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'  # O tu servidor SMTP
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'tu-email@gmail.com'
EMAIL_HOST_PASSWORD = 'tu-password-o-app-password'
DEFAULT_FROM_EMAIL = 'OpticaApp <noreply@opticaapp.com>'
```

**Variables de entorno (.env):**
```bash
EMAIL_HOST_USER=tu-email@gmail.com
EMAIL_HOST_PASSWORD=tu-password
```

### 8. **Integración con Registro**

La vista `user_register` en `apps/organizations/views.py` fue modificada:

**Cambios principales:**
```python
# Usuario inactivo hasta verificar
user = User.objects.create_user(
    ...,
    is_active=False
)

# Crear perfil
UserProfile.objects.create(
    user=user,
    is_email_verified=False
)

# Enviar email de verificación
send_verification_email(user, request)

# NO hacer login automático
# Redirigir a página de verificación pendiente
return redirect('users:verification_pending')
```

### 9. **Panel de Administración**

**UserProfileAdmin:**
- Ver estado de verificación de usuarios
- Buscar por usuario, email, teléfono
- Filtrar por verificados/no verificados
- Ver fecha de verificación

**EmailVerificationTokenAdmin:**
- Ver todos los tokens generados
- Estado: usado/no usado, expirado/válido
- Búsqueda por usuario, token
- No permite crear tokens manualmente (seguridad)

### 10. **Mensajes al Usuario**

**Registro exitoso:**
```
¡Cuenta creada exitosamente! Hemos enviado un correo a email@ejemplo.com para verificar tu cuenta.
```

**Email no enviado:**
```
Cuenta creada, pero hubo un error al enviar el email. Por favor contacta a soporte.
```

**Verificación exitosa:**
```
¡Tu correo electrónico ha sido verificado exitosamente! Ahora puedes iniciar sesión.
```

**Token expirado:**
```
Este enlace de verificación ha expirado. Por favor solicita uno nuevo.
```

**Token ya usado:**
```
Este enlace de verificación ya fue utilizado.
```

**Intento de acceso sin verificar:**
```
Debes verificar tu correo electrónico para acceder a esta área.
```

### 11. **Casos de Uso Especiales**

#### Usuario antiguo sin perfil
El middleware crea automáticamente el perfil si no existe:
```python
profile, created = UserProfile.objects.get_or_create(user=request.user)
```

#### Reenvío de verificación
- Invalida tokens anteriores no usados
- Genera nuevo token
- Envía nuevo email
- No revela si el email existe (seguridad)

#### Verificación manual por admin
El administrador puede marcar manualmente como verificado desde el panel admin.

### 12. **Seguridad**

✅ **Tokens UUID:** Imposibles de predecir
✅ **Expiración:** 24 horas
✅ **Uso único:** Token inválido después de verificar
✅ **No revela información:** Los errores no indican si un email existe
✅ **HTTPS requerido:** Para enlaces de verificación en producción
✅ **Middleware protege rutas:** Bloquea acceso no autorizado

### 13. **Testing Manual**

#### Probar flujo completo:
```bash
1. Ir a /organizations/register/
2. Registrar nuevo usuario
3. Verificar que se redirige a /users/verification/pending/
4. Revisar consola del servidor para ver el email
5. Copiar URL de verificación
6. Visitar URL de verificación
7. Verificar redirección a login con mensaje de éxito
8. Iniciar sesión → Debe permitir acceso
```

#### Probar token expirado:
```python
# En Django shell
from apps.users.email_verification_models import EmailVerificationToken
from datetime import timedelta
from django.utils import timezone

token = EmailVerificationToken.objects.last()
token.expires_at = timezone.now() - timedelta(hours=1)
token.save()

# Ahora intentar verificar con ese token
```

#### Probar reenvío:
```bash
1. Ir a /users/verification/resend/
2. Ingresar email del usuario registrado
3. Verificar que se genera nuevo token
4. Verificar que tokens anteriores están invalidados
```

### 14. **Comandos Útiles**

```bash
# Ver usuarios sin verificar
python manage.py shell
>>> from django.contrib.auth.models import User
>>> from apps.users.email_verification_models import UserProfile
>>> unverified = User.objects.filter(profile__is_email_verified=False)

# Ver tokens pendientes
>>> from apps.users.email_verification_models import EmailVerificationToken
>>> pending_tokens = EmailVerificationToken.objects.filter(is_used=False)

# Verificar usuario manualmente (emergencia)
>>> user = User.objects.get(username='username')
>>> user.is_active = True
>>> user.save()
>>> profile = user.profile
>>> profile.is_email_verified = True
>>> profile.save()
```

### 15. **Troubleshooting**

**Problema:** Email no se envía
**Solución:** 
- Verificar configuración SMTP en settings.py
- Revisar logs del servidor
- Para Gmail, usar "App Password" en lugar de contraseña normal

**Problema:** Token dice "No válido" pero existe
**Solución:**
- Verificar que no esté expirado (24 horas)
- Verificar que no esté marcado como usado
- Revisar logs de errores

**Problema:** Usuario no puede acceder después de verificar
**Solución:**
- Verificar que `user.is_active = True`
- Verificar que `user.profile.is_email_verified = True`
- Limpiar caché del navegador
- Cerrar sesión y volver a iniciar

**Problema:** Middleware bloquea admin
**Solución:**
- El admin está en las URLs exentas
- Verificar orden de middleware en settings.py
- EmailVerificationMiddleware debe estar DESPUÉS de AuthenticationMiddleware

### 16. **Próximas Mejoras**

- [ ] Rate limiting para reenvío de emails
- [ ] Logs de intentos de verificación
- [ ] Notificaciones push además de email
- [ ] Verificación en dos pasos (2FA)
- [ ] Soporte para múltiples emails
- [ ] Personalización de templates por tenant

## Archivos Creados/Modificados

### Archivos Nuevos:
- `apps/users/email_verification_models.py`
- `apps/users/email_views.py`
- `apps/users/email_verification_middleware.py`
- `apps/users/templates/users/emails/verify_email.html`
- `apps/users/templates/users/verification_pending.html`
- `apps/users/templates/users/resend_verification.html`
- `apps/users/migrations/0003_emailverificationtoken_userprofile.py`

### Archivos Modificados:
- `apps/users/urls.py` - Agregadas rutas de verificación
- `apps/users/admin.py` - Agregados admin para UserProfile y EmailVerificationToken
- `apps/users/models.py` - Import de modelos de verificación
- `apps/organizations/views.py` - Modificada vista user_register
- `config/settings.py` - Agregado EmailVerificationMiddleware

## Conclusión

El sistema de verificación de email está completamente integrado y protege el acceso a la aplicación. Los usuarios deben verificar su email antes de poder acceder al dashboard, mejorando la seguridad y asegurando contactabilidad real.
