# GUÍA DE DEPLOY INICIAL - OpticaApp en Render

## 🎯 OBJETIVO
Desplegar OpticaApp en Render desde cero con el plan Professional ($19/mes)

---

## PASO 1: CREAR CUENTA EN RENDER ⭐

1. Ve a: **https://render.com/**
2. Click en **"Get Started"** o **"Sign Up"**
3. Opciones de registro:
   - Con GitHub (RECOMENDADO - más fácil)
   - Con Google
   - Con Email
4. **Completa el registro**
5. **Verifica tu email** si usaste email directo
6. Accede al Dashboard: https://dashboard.render.com/

---

## PASO 2: ACTIVAR PLAN PROFESSIONAL ($19/mes) 💳

1. En el Dashboard, busca en la parte superior derecha tu nombre/avatar
2. Click en **"Account Settings"** o ve directamente a Settings
3. En el menú lateral, click en **"Billing"**
4. Verás los planes disponibles
5. Selecciona **"Professional"** ($19 USD per user/month)
6. Click en **"Select Plan"** o **"Upgrade"**
7. Ingresa los datos de tu tarjeta
8. Confirma el pago
9. Verás que tu plan cambió a "Professional" ✅

**Costos estimados:**
- Plan Professional: $19/mes
- PostgreSQL Basic-1gb: $19/mes
- Web Service Starter: $7/mes
- **TOTAL: ~$45/mes**

---

## PASO 3: CREAR BASE DE DATOS POSTGRESQL 🗄️

1. En el Dashboard principal, click en el botón azul **"New +"** (arriba a la derecha)
2. Selecciona **"PostgreSQL"**
3. Configuración:

```
Name: opticaapp-db
Region: Ohio (US East) o el más cercano a ti
PostgreSQL Version: 15 (o 16 si está disponible)
```

4. En **"Instance Type"**, selecciona: **Basic-1gb** ($19/mes)
   - 1 GB RAM
   - 0.5 CPU
   - Incluye backups automáticos
   - Point-in-time recovery

5. Click en **"Create Database"**
6. **Espera 2-3 minutos** mientras se aprovisiona
7. Una vez listo, verás un círculo verde ✅

---

## PASO 4: OBTENER CREDENCIALES DE LA BD 📋

1. Click en tu base de datos recién creada
2. Ve a la pestaña **"Info"**
3. **COPIA Y GUARDA** estos datos (los necesitarás después):

```
Internal Database URL: postgresql://user:pass@host/db
  ↑ Usa esta para conectar desde Render

External Database URL: postgresql://user:pass@external-host/db
  ↑ Usa esta para conectar desde tu PC

Hostname: xxxxx.oregon-postgres.render.com
Port: 5432
Database: opticaapp_db_xxxx
Username: opticaapp_db_xxxx_user
Password: (largo, guárdalo bien)
```

**IMPORTANTE:** Guarda estos datos en un lugar seguro (archivo local)

---

## PASO 5: CREAR WEB SERVICE 🚀

1. En el Dashboard, click en **"New +"** nuevamente
2. Selecciona **"Web Service"**
3. Conectar repositorio:
   - Si te registraste con GitHub, verás tus repos
   - Busca **"OpticaApp"** (o danioso8/opticaApp)
   - Click en **"Connect"**

4. Configuración del servicio:

```
Name: opticaapp
  ↑ Este será tu subdominio: opticaapp.onrender.com

Region: Ohio (US East) - mismo que la BD
  ↑ IMPORTANTE: Usa la misma región que tu base de datos

Branch: main
  ↑ La rama principal de tu repositorio

Root Directory: (dejar vacío)

Runtime: Python 3

Build Command:
pip install -r requirements.txt && python manage.py collectstatic --noinput

Start Command:
daphne -b 0.0.0.0 -p $PORT config.asgi:application
```

5. En **"Instance Type"**, selecciona: **Starter** ($7/mes)
   - 512 MB RAM
   - 0.5 CPU
   - Suficiente para empezar

6. **NO HAGAS CLICK EN "CREATE" TODAVÍA** ⚠️

---

## PASO 6: CONFIGURAR VARIABLES DE ENTORNO ⚙️

**ANTES de crear el servicio**, baja hasta la sección **"Environment Variables"**

Click en **"Add Environment Variable"** y agrega estas (una por una):

### Variables requeridas:

```bash
DATABASE_URL
Internal Database URL de tu PostgreSQL (paso 4)
postgresql://user:pass@host/db

SECRET_KEY
Genera uno nuevo con este comando en tu terminal local:
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"

DEBUG
False

ALLOWED_HOSTS
*.onrender.com

DJANGO_SETTINGS_MODULE
config.settings

PYTHONUNBUFFERED
1

WEB_CONCURRENCY
2
```

### Cómo agregar cada variable:
1. Click "Add Environment Variable"
2. Key: (nombre de la variable, ej: DATABASE_URL)
3. Value: (el valor correspondiente)
4. Click fuera del campo para guardar
5. Repite para cada variable

---

## PASO 7: DEPLOY! 🎉

1. Una vez agregadas **TODAS** las variables, baja hasta el final
2. Click en el botón azul **"Create Web Service"**
3. **Render comenzará a construir y desplegar** tu aplicación
4. Verás los logs en tiempo real:
   - Installing dependencies...
   - Running migrations...
   - Collecting static files...
   - Starting server...

**Tiempo estimado: 5-10 minutos**

---

## PASO 8: EJECUTAR MIGRACIONES 🔧

Una vez que el deploy termine (verás "Live" en verde):

1. En tu servicio, click en **"Shell"** en el menú lateral
2. Se abrirá una terminal
3. Ejecuta estos comandos uno por uno:

```bash
# Ver migraciones pendientes
python manage.py showmigrations

# Aplicar todas las migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Seguir las instrucciones para crear tu usuario admin
```

---

## PASO 9: VERIFICAR QUE TODO FUNCIONA ✅

1. En el Dashboard, busca la URL de tu servicio:
   - Algo como: `https://opticaapp.onrender.com`
2. **Click en la URL** o cópiala y ábrela en tu navegador
3. Deberías ver la página de login de OpticaApp
4. **Inicia sesión** con el superusuario que creaste
5. **Prueba**:
   - Crear un paciente
   - Crear un examen visual
   - Ver el dashboard
   - Todas las funcionalidades

---

## PASO 10: CONFIGURAR DOMINIO PERSONALIZADO (Opcional) 🌐

Si tienes un dominio propio:

1. En tu servicio, ve a **"Settings"**
2. Busca la sección **"Custom Domains"**
3. Click en **"Add Custom Domain"**
4. Ingresa tu dominio (ej: optica.tudominio.com)
5. Render te dará instrucciones para configurar DNS
6. Agrega los registros CNAME en tu proveedor de dominio
7. Espera propagación (5-30 minutos)

---

## 🎊 ¡LISTO! Tu OpticaApp está en producción

**URLs importantes:**
- Dashboard: https://dashboard.render.com/
- Tu App: https://opticaapp.onrender.com (o tu dominio)
- Docs Render: https://render.com/docs

**Próximos pasos:**
- Configura backups regulares
- Monitorea el uso de recursos
- Configura notificaciones de errores
- Invita a otros usuarios si es necesario

---

## 🆘 TROUBLESHOOTING

### Error: "Application failed to respond"
- Verifica que las variables de entorno estén correctas
- Revisa los logs en la pestaña "Logs"
- Verifica que DATABASE_URL apunte a tu BD

### Error: "Bad Request (400)"
- Agrega tu dominio real a ALLOWED_HOSTS
- Ej: `opticaapp.onrender.com,*.onrender.com`

### Error: "DisallowedHost"
- Mismo que arriba, actualiza ALLOWED_HOSTS

### Migraciones fallan
- Ve al Shell y ejecuta manualmente: `python manage.py migrate`
- Si hay conflictos, ejecuta: `python manage.py migrate --fake-initial`

---

## 💰 COSTOS MENSUALES

```
Plan Professional:        $19/mes
PostgreSQL Basic-1gb:     $19/mes  
Web Service Starter:      $7/mes
Bandwidth (incluido):     100 GB
──────────────────────────────────
TOTAL:                    $45/mes
```

**Incluye:**
✅ Proyectos ilimitados
✅ Pipeline minutes ilimitados
✅ Backups automáticos diarios
✅ SSL/HTTPS gratuito
✅ Soporte por email y chat

---

## 📞 SOPORTE

¿Problemas? Contacta:
- Email: support@render.com
- Community: https://community.render.com/
- Docs: https://render.com/docs

---

**¡Éxito con tu deploy! 🚀**
