# 🚀 Guía de Despliegue en Render

Esta guía te ayudará a desplegar OCEANO OPTICO en Render de forma gratuita.

## 📋 Requisitos Previos

1. Cuenta en [Render](https://render.com) (gratis)
2. Repositorio GitHub con el código (ya está listo)
3. 10 minutos de tu tiempo

## 🎯 Paso 1: Crear Base de Datos PostgreSQL

1. Ve a [Render Dashboard](https://dashboard.render.com/)
2. Click en **"New +"** → **"PostgreSQL"**
3. Configura:
   - **Name**: `oceano-optico-db`
   - **Database**: `oceano_optico`
   - **User**: `oceano_admin`
   - **Region**: Elige el más cercano
   - **Plan**: **Free** (gratis)
4. Click en **"Create Database"**
5. **Guarda la URL de conexión** (Internal Database URL) - la necesitarás después

## 🎯 Paso 2: Crear Web Service

1. En Render Dashboard, click en **"New +"** → **"Web Service"**
2. Conecta tu repositorio GitHub: `danioso8/opticaApp`
3. Configura el servicio:

### Configuración Básica
- **Name**: `oceano-optico`
- **Region**: El mismo que la base de datos
- **Branch**: `main`
- **Root Directory**: (dejar vacío)
- **Runtime**: `Python 3`
- **Build Command**: `./build.sh`
- **Start Command**: `daphne -b 0.0.0.0 -p $PORT config.asgi:application`

### Plan
- **Instance Type**: **Free** (gratis)

## 🎯 Paso 3: Variables de Entorno

En la sección **Environment**, agrega estas variables:

```env
# Django Settings
SECRET_KEY=tu-secret-key-super-segura-aqui-generala-random
DEBUG=False
ALLOWED_HOSTS=.onrender.com

# Database (Copiar de tu PostgreSQL en Render)
DATABASE_URL=postgresql://usuario:password@host/database

# Python
PYTHON_VERSION=3.7.9

# Business Info
BUSINESS_PHONE=300 123 4567
WEBSITE_URL=https://oceano-optico.onrender.com

# WhatsApp (Opcional - puedes configurarlo después)
TWILIO_ACCOUNT_SID=
TWILIO_AUTH_TOKEN=
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Appointment Settings
APPOINTMENT_SLOT_DURATION=30
MAX_DAILY_APPOINTMENTS=20
ADVANCE_BOOKING_DAYS=30
```

### 🔑 Generar SECRET_KEY

Puedes generar una clave secreta segura con Python:

```python
import secrets
print(secrets.token_urlsafe(50))
```

O usa este comando en tu terminal:
```bash
python -c "import secrets; print(secrets.token_urlsafe(50))"
```

## 🎯 Paso 4: Desplegar

1. Revisa que todas las variables estén configuradas
2. Click en **"Create Web Service"**
3. Render comenzará a construir y desplegar tu aplicación
4. Espera 5-10 minutos (la primera vez tarda más)

## ✅ Paso 5: Verificar el Despliegue

Una vez que termine, verás:
- ✅ Build succeeded
- ✅ Service is live

Tu aplicación estará disponible en:
```
https://oceano-optico.onrender.com
```

## 🔐 Paso 6: Acceder al Admin

El script `build.sh` crea automáticamente un superusuario:

- **URL**: `https://oceano-optico.onrender.com/admin/`
- **Usuario**: `admin`
- **Contraseña**: `admin123`

⚠️ **IMPORTANTE**: Cambia la contraseña inmediatamente después del primer login.

## 📱 Paso 7: Configurar WhatsApp (Opcional)

Si quieres habilitar notificaciones por WhatsApp:

### Opción 1: Twilio (Recomendado para producción)
1. Crea cuenta en [Twilio](https://www.twilio.com)
2. Obtén tus credenciales
3. Actualiza las variables en Render:
   - `TWILIO_ACCOUNT_SID`
   - `TWILIO_AUTH_TOKEN`
   - `TWILIO_WHATSAPP_FROM`

### Opción 2: Bot Local
El bot local de WhatsApp no funcionará en Render Free (necesita estar siempre corriendo).
Para producción, usa Twilio.

## 🔧 Configuración Post-Despliegue

### Actualizar URLs Permitidas

1. En Render, ve a tu servicio
2. Copia la URL completa (ej: `oceano-optico.onrender.com`)
3. Ve a **Environment** y actualiza:
   ```
   ALLOWED_HOSTS=oceano-optico.onrender.com,.onrender.com
   WEBSITE_URL=https://oceano-optico.onrender.com
   ```

### Configurar Dominio Personalizado (Opcional)

1. En Render, ve a **Settings** → **Custom Domain**
2. Agrega tu dominio: `oceanooptico.com`
3. Actualiza los DNS en tu proveedor de dominio
4. Actualiza `ALLOWED_HOSTS` con tu dominio

## 🎨 Verificar Funcionalidades

Prueba estas URLs:

1. **Landing Page**: `https://tu-app.onrender.com/`
2. **Agendar Cita**: `https://tu-app.onrender.com/agendar/`
3. **Dashboard**: `https://tu-app.onrender.com/dashboard/`
4. **Admin**: `https://tu-app.onrender.com/admin/`
5. **API Health**: `https://tu-app.onrender.com/api/configuration/`

## 🐛 Troubleshooting

### Error: "Application failed to start"

**Solución 1**: Verifica los logs en Render
- Ve a **Logs** en tu servicio
- Busca errores rojos

**Solución 2**: Verifica las variables de entorno
- Asegúrate de que `DATABASE_URL` esté correcta
- Verifica que `SECRET_KEY` no tenga espacios

**Solución 3**: Rebuild
- Ve a **Manual Deploy** → **Clear build cache & deploy**

### Error: "Static files not found"

**Solución**: Verifica que `build.sh` se ejecutó correctamente
```bash
python manage.py collectstatic --no-input
```

### Error: "Database connection failed"

**Solución**: Verifica `DATABASE_URL`
1. Ve a tu PostgreSQL en Render
2. Copia la **Internal Database URL**
3. Pégala en la variable `DATABASE_URL`

### La aplicación es lenta

⚠️ **Normal en Free Tier**: Render Free tiene estas limitaciones:
- Se duerme después de 15 minutos de inactividad
- El primer request tarda ~1 minuto en despertar
- 750 horas gratis al mes

**Solución**: Actualiza a plan pagado ($7/mes) para mantenerla siempre activa.

### Los archivos estáticos no cargan

**Solución**: Verifica Whitenoise
1. En `settings.py` debe estar:
   ```python
   MIDDLEWARE = [
       'whitenoise.middleware.WhiteNoiseMiddleware',  # Después de SecurityMiddleware
       ...
   ]
   ```

2. Rebuild la aplicación

## 📊 Monitoreo

Render proporciona:
- **Logs en tiempo real**: Ve errores y requests
- **Métricas**: CPU, memoria, requests
- **Alertas**: Notificaciones si la app falla

## 🔄 Actualizar la Aplicación

Para desplegar cambios:

1. Haz commit en tu repositorio:
   ```bash
   git add .
   git commit -m "Update: descripción del cambio"
   git push origin main
   ```

2. Render detectará el cambio automáticamente
3. Se redesplegarán los cambios en ~5 minutos

O manualmente:
1. Ve a tu servicio en Render
2. Click en **Manual Deploy** → **Deploy latest commit**

## 💰 Costos

### Plan Free (Actual)
- ✅ **Gratis** para siempre
- 750 horas/mes por servicio
- Se duerme después de 15 min inactividad
- PostgreSQL 1GB
- 100GB bandwidth

### Plan Starter ($7/mes)
- Siempre activo (no se duerme)
- PostgreSQL 10GB
- 100GB bandwidth
- Mejor rendimiento

## 🎉 ¡Listo!

Tu aplicación está en producción:
- 🌐 **Web**: https://tu-app.onrender.com
- 📊 **Dashboard**: https://tu-app.onrender.com/dashboard
- 🔐 **Admin**: https://tu-app.onrender.com/admin

## 📚 Recursos Adicionales

- [Render Docs](https://render.com/docs)
- [Django Deployment](https://docs.djangoproject.com/en/3.2/howto/deployment/)
- [PostgreSQL en Render](https://render.com/docs/databases)

## 🆘 Soporte

Si tienes problemas:
1. Revisa los logs en Render
2. Verifica las variables de entorno
3. Consulta esta guía
4. Contacta al equipo de desarrollo

---

⭐ **Pro Tip**: Mantén un respaldo de tu base de datos SQLite local antes de desplegar.

🌊 **OCEANO OPTICO** en la nube 🚀
