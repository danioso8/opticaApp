# 🤖 Configuración Automática con API de Render

Este script configura automáticamente todas las variables de entorno en Render usando su API.

## 📋 Requisitos

1. **Cuenta en Render** (gratis)
2. **API Key de Render** 
3. **Web Service creado** en Render
4. **PostgreSQL creado** en Render

## 🔑 Paso 1: Obtener API Key

1. Ve a: https://dashboard.render.com/u/settings#api-keys
2. Click en **"Create API Key"**
3. Dale un nombre: `OpticaApp Deploy`
4. Copia el API Key generado

## 🆔 Paso 2: Obtener Service ID

1. Ve a tu servicio web en Render
2. La URL se verá así: `https://dashboard.render.com/web/srv-XXXXXXXXXXXXX`
3. Copia el ID que empieza con `srv-`

## ⚙️ Paso 3: Configurar el Script

Edita el archivo `auto_deploy_render.py` y completa:

```python
# Tu API Key de Render
RENDER_API_KEY = "rnd_xxxxxxxxxxxxxxxxxxxx"  # <-- PEGA AQUÍ

# ID de tu servicio web
WEB_SERVICE_ID = "srv-xxxxxxxxxxxxx"  # <-- PEGA AQUÍ

# URL de tu PostgreSQL (ya está configurada)
DATABASE_URL = "postgresql://oceano_admin:GqZwicsr384aWBS8YjwBfMbxWrdq61qT@dpg-d4llkbruibrs7384b38g-a/oceano_optico"
```

## 🚀 Paso 4: Ejecutar el Script

```bash
# Instalar la librería requests si no la tienes
pip install requests

# Ejecutar el script
python auto_deploy_render.py
```

## 📊 Qué Hace el Script

1. ✅ Genera un `SECRET_KEY` único y seguro
2. ✅ Configura las 10 variables de entorno necesarias:
   - SECRET_KEY
   - DEBUG
   - ALLOWED_HOSTS
   - DATABASE_URL
   - PYTHON_VERSION
   - BUSINESS_PHONE
   - WEBSITE_URL
   - APPOINTMENT_SLOT_DURATION
   - MAX_DAILY_APARTMENTS
   - ADVANCE_BOOKING_DAYS
3. ✅ Actualiza las variables en Render usando la API
4. ✅ Inicia un deploy automático
5. ✅ Guarda una copia local en `.env.render`

## 📝 Output del Script

```
======================================================================
🚀 CONFIGURACIÓN AUTOMÁTICA DE RENDER
======================================================================

✅ API Key configurada
✅ Service ID: srv-xxxxx
✅ Database URL configurada

🔑 SECRET_KEY generada: 81zMAOPHEDCLGay1EHnj...

📋 Variables a configurar:
----------------------------------------------------------------------
  SECRET_KEY: 81zMAOPHEDCLGay1EHnjLu2eJ-1...
  DEBUG: False
  ALLOWED_HOSTS: .onrender.com
  DATABASE_URL: postgresql://oceano_admin:Gq...
  PYTHON_VERSION: 3.7.9
  BUSINESS_PHONE: 300 123 4567
  WEBSITE_URL: https://oceano-optico.onrender.com
  ...
----------------------------------------------------------------------

¿Deseas continuar? (si/no): si

⏳ Actualizando variables de entorno...
✅ Variables actualizadas correctamente
✅ Copia guardada en .env.render

⏳ Iniciando deploy automático...
✅ Deploy iniciado correctamente

======================================================================
🎉 CONFIGURACIÓN COMPLETADA
======================================================================

📊 Monitorea el progreso en:
   https://dashboard.render.com/web/srv-xxxxx

⏱️  El deploy tomará ~5-10 minutos

🔐 Credenciales de admin (creadas automáticamente):
   Usuario: admin
   Contraseña: admin123

⚠️  CAMBIA LA CONTRASEÑA después del primer login!
```

## 🆘 Solución de Problemas

### Error: "Invalid API Key"
- Verifica que copiaste correctamente el API Key
- El API Key debe empezar con `rnd_`
- Genera un nuevo API Key si es necesario

### Error: "Service not found"
- Verifica el Service ID en la URL de tu servicio web
- Debe empezar con `srv-`

### Error: "Unauthorized"
- El API Key debe tener permisos de escritura
- Verifica en Settings que no esté expirado

## ✅ Verificación Post-Deploy

Una vez completado el deploy:

1. Accede a: `https://oceano-optico.onrender.com`
2. Ve al admin: `https://oceano-optico.onrender.com/admin/`
3. Login: `admin` / `admin123`
4. Cambia la contraseña inmediatamente

## 📁 Archivos Relacionados

- `auto_deploy_render.py` - Script principal
- `setup_render_env.py` - Generador manual de variables
- `.env.render` - Variables guardadas localmente (no en Git)
- `RENDER_DEPLOY.md` - Guía manual completa
