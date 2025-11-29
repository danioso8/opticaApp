# 🚀 Configuración Rápida de Variables en Render

## Paso 1: Generar Variables

Ejecuta el script localmente:

```bash
python setup_render_env.py
```

Este script genera automáticamente:
- ✅ SECRET_KEY único y seguro
- ✅ Todas las variables de configuración
- ✅ Archivo `.env.render` con las variables (no se sube a Git)

## Paso 2: Copiar Variables a Render

### A. Ir a Environment Variables

1. Ve a tu servicio web en Render: https://dashboard.render.com
2. Selecciona `oceano-optico`
3. Click en **Environment** en el menú izquierdo
4. Click en **Add Environment Variable**

### B. Agregar Variables Básicas

Copia cada variable del output del script:

| Variable | Valor (del script) |
|----------|-------------------|
| `SECRET_KEY` | `81zMAOP...` (el generado) |
| `DEBUG` | `False` |
| `ALLOWED_HOSTS` | `oceano-optico.onrender.com,.onrender.com` |
| `PYTHON_VERSION` | `3.7.9` |
| `BUSINESS_PHONE` | `300 123 4567` |
| `WEBSITE_URL` | `https://oceano-optico.onrender.com` |
| `APPOINTMENT_SLOT_DURATION` | `30` |
| `MAX_DAILY_APPOINTMENTS` | `20` |
| `ADVANCE_BOOKING_DAYS` | `30` |

### C. Agregar DATABASE_URL

1. Ve a tu base de datos PostgreSQL `oceano-optico-db`
2. Busca la sección **Connections**
3. Copia el **Internal Database URL** 
4. En tu servicio web, agrega:
   - Variable: `DATABASE_URL`
   - Valor: `postgresql://oceano_admin:...@dpg-xxx.oregon-postgres.render.com/oceano_optico`

### D. (Opcional) WhatsApp con Twilio

Si quieres notificaciones por WhatsApp:

| Variable | Valor |
|----------|-------|
| `TWILIO_ACCOUNT_SID` | Tu Account SID de Twilio |
| `TWILIO_AUTH_TOKEN` | Tu Auth Token de Twilio |
| `TWILIO_WHATSAPP_FROM` | `whatsapp:+14155238886` |

## Paso 3: Deploy

Click en **Manual Deploy** → **Deploy latest commit**

El build tomará ~5-10 minutos.

## Paso 4: Verificar

Una vez completado el deploy:

1. Accede a: `https://oceano-optico.onrender.com`
2. Ve al admin: `https://oceano-optico.onrender.com/admin/`
3. Login:
   - Usuario: `admin`
   - Contraseña: `admin123`
4. ⚠️ **CAMBIA LA CONTRASEÑA inmediatamente**

## 🔍 Verificar Configuración

```bash
# Ver logs en tiempo real
Dashboard → Logs

# Busca estos mensajes:
==> Instalando dependencias... ✓
==> Recolectando archivos estáticos... ✓
==> Aplicando migraciones... ✓
==> Creando superusuario... ✓
==> Build completado exitosamente ✓
```

## 📁 Archivos de Referencia

- `setup_render_env.py` - Script generador
- `.env.render` - Variables generadas (local, no en Git)
- `RENDER_DEPLOY.md` - Guía completa detallada

## ⚠️ Importante

- **NO** subas `.env.render` a Git (ya está en .gitignore)
- **SÍ** cambia la contraseña del admin después del primer login
- Las variables se pueden editar en cualquier momento en Render
- Cada cambio de variables requiere un re-deploy

## 🆘 Problemas Comunes

### Error: "No module named 'psycopg2'"
✅ Ya incluido en `requirements.txt`

### Error: "ALLOWED_HOSTS"
✅ Verifica que ALLOWED_HOSTS incluya `.onrender.com`

### Error: "SECRET_KEY"
✅ Ejecuta `python setup_render_env.py` nuevamente para generar uno nuevo

### Base de datos no conecta
✅ Verifica que `DATABASE_URL` sea el **Internal Database URL** de PostgreSQL
