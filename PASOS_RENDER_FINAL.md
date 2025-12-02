# 🚀 INSTRUCCIONES PARA CONFIGURAR RENDER

## ✅ CÓDIGO YA ESTÁ EN GITHUB
El código se ha subido exitosamente a GitHub y Render debería estar haciendo el deploy automáticamente.

---

## 📋 PASOS PARA COMPLETAR LA CONFIGURACIÓN

### PASO 1: Esperar el Deploy Automático

1. Ve a tu dashboard de Render: https://dashboard.render.com/
2. Busca tu servicio web (oceano-optico o similar)
3. Espera a que termine el deploy (verás un check verde ✅)
4. Si hay errores, revisa los logs

### PASO 2: Ejecutar Migraciones en Shell de Render

1. **Abrir el Shell:**
   - En tu servicio de Render, ve a la pestaña **"Shell"**
   - Espera a que se cargue el terminal

2. **Ejecutar las migraciones:**
   ```bash
   python manage.py migrate
   ```
   
   Deberías ver algo como:
   ```
   Running migrations:
     Applying organizations.0001_initial... OK
     Applying appointments.0001_initial... OK
     ...
   ```

### PASO 3: Crear Superuser y Planes AUTOMÁTICAMENTE

En el mismo Shell de Render, ejecuta:

```bash
python setup_render_superuser.py
```

Este script hace TODO automáticamente:
- ✅ Crea el superuser: `admin` / `Admin2025!`
- ✅ Crea 4 planes de suscripción
- ✅ Crea la organización admin
- ✅ Asigna el superuser a la organización

**OUTPUT ESPERADO:**
```
============================================================
🚀 CONFIGURACIÓN INICIAL DE RENDER
============================================================

👤 PASO 1: Crear Superuser para Dashboard Admin
------------------------------------------------------------
✅ Superuser creado exitosamente!
   Username: admin
   Email: admin@oceanoptico.com
   Password: Admin2025!

📋 PASO 2: Crear Planes de Suscripción
------------------------------------------------------------
✨ Creando planes de suscripción...

✅ Plan Gratuito creado - $0.0/mes
✅ Plan Básico creado - $29.99/mes
✅ Plan Profesional creado - $59.99/mes
✅ Plan Empresarial creado - $99.99/mes

✅ Total: 4 planes creados

🏢 PASO 3: Crear Organización Admin
------------------------------------------------------------
✅ Organización 'Administración OCEANO OPTICO' creada
   Slug: admin-org
   Plan: Plan Gratuito

============================================================
✅ CONFIGURACIÓN COMPLETADA
============================================================

📊 RESUMEN:
   • Superusers: 1
   • Planes: 4
   • Organizaciones: 1

🔐 ACCESO AL DASHBOARD ADMIN:
   URL: https://tu-app.onrender.com/admin/
   Username: admin
   Password: Admin2025!

   ⚠️  CAMBIA LA CONTRASEÑA INMEDIATAMENTE!

🎉 ¡Sistema listo para producción!
============================================================
```

---

## 🔐 CREDENCIALES INICIALES

### Dashboard Admin (Superuser)
- **URL:** `https://tu-app.onrender.com/admin/`
- **Username:** `admin`
- **Password:** `Admin2025!`

⚠️ **IMPORTANTE:** Cambia la contraseña después del primer login

---

## 🎯 VERIFICAR QUE TODO FUNCIONA

### 1. Acceder al Admin
```
https://tu-app.onrender.com/admin/
```
- Login con: `admin` / `Admin2025!`
- Verás el Django Admin

### 2. Verificar Planes de Suscripción
En el admin, ve a:
```
Organizations > Subscription Plans
```
Deberías ver 4 planes:
- Plan Gratuito ($0/mes)
- Plan Básico ($29.99/mes)
- Plan Profesional ($59.99/mes)
- Plan Empresarial ($99.99/mes)

### 3. Probar Registro de Usuario
```
https://tu-app.onrender.com/organizations/register/
```
- Deberías poder seleccionar un plan
- Completar el formulario de registro
- Crear una cuenta nueva

### 4. Dashboard de Notificaciones
```
https://tu-app.onrender.com/dashboard/configuracion/notificaciones/
```
- Login con tu cuenta nueva
- Deberías ver el panel de configuración de WhatsApp/Email

---

## ⚙️ CONFIGURAR VARIABLES DE ENTORNO EN RENDER

Ve a tu servicio en Render > Environment Variables y añade:

```bash
# Django
SECRET_KEY=tu-secret-key-super-segura-aqui
DEBUG=False
ALLOWED_HOSTS=.onrender.com,tu-dominio.com

# Database (Ya está configurada automáticamente)

# Email (Gmail SMTP - GRATIS)
USE_EMAIL_NOTIFICATIONS=True
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=tu_email@gmail.com
EMAIL_HOST_PASSWORD=tu_app_password_de_gmail
DEFAULT_FROM_EMAIL=noreply@oceanoptico.com

# Twilio (OPCIONAL - Solo si quieres WhatsApp de pago)
TWILIO_ACCOUNT_SID=tu_twilio_sid
TWILIO_AUTH_TOKEN=tu_twilio_token
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Business Info
BUSINESS_PHONE=+57 300 123 4567
WEBSITE_URL=https://tu-app.onrender.com
```

---

## 🐛 SOLUCIÓN DE PROBLEMAS

### Error: "No module named 'psycopg2'"
Ya está resuelto en `requirements.txt` con `psycopg2-binary`

### Error: "SSL connection closed"
Ya está resuelto en `settings.py` con configuración SSL

### Error: "No subscription plans available"
Ejecuta `python setup_render_superuser.py` en el Shell de Render

### No puedo hacer login
1. Verifica que ejecutaste las migraciones
2. Verifica que ejecutaste `setup_render_superuser.py`
3. Usa: `admin` / `Admin2025!`

---

## 📝 COMANDOS ÚTILES EN RENDER SHELL

```bash
# Ver migraciones aplicadas
python manage.py showmigrations

# Crear otro superuser manualmente
python manage.py createsuperuser

# Acceder al shell de Django
python manage.py shell

# Ver planes existentes
python manage.py shell -c "from apps.organizations.models import SubscriptionPlan; print([p.name for p in SubscriptionPlan.objects.all()])"

# Ver usuarios
python manage.py shell -c "from django.contrib.auth import get_user_model; User = get_user_model(); print(f'Usuarios: {User.objects.count()}')"
```

---

## ✅ CHECKLIST FINAL

- [ ] Deploy completado en Render
- [ ] Migraciones ejecutadas: `python manage.py migrate`
- [ ] Setup automático ejecutado: `python setup_render_superuser.py`
- [ ] Login exitoso en `/admin/` con `admin` / `Admin2025!`
- [ ] 4 planes visibles en el admin
- [ ] Registro de usuario funciona en `/organizations/register/`
- [ ] Contraseña del admin cambiada
- [ ] Variables de entorno configuradas en Render
- [ ] Email SMTP configurado (opcional)
- [ ] Twilio configurado (opcional)

---

## 🎉 ¡LISTO PARA PRODUCCIÓN!

Tu aplicación está configurada y lista para usar. Ahora puedes:

1. **Registrar organizaciones** en `/organizations/register/`
2. **Gestionar usuarios** desde el admin
3. **Configurar notificaciones** desde el dashboard
4. **Crear citas** y empezar a usar el sistema

---

## 📞 SOPORTE

Si tienes problemas:
1. Revisa los logs en Render Dashboard
2. Verifica que todas las migraciones se aplicaron
3. Confirma que el script de setup se ejecutó correctamente
4. Verifica las variables de entorno

---

**Fecha de creación:** 2 de Diciembre, 2025  
**Versión:** 1.0  
**Última actualización:** Configuración SSL + Setup automático
