# CHECKLIST DE MIGRACIÓN - OpticaApp a Nueva Cuenta Render

## ✅ PASO 1: BACKUP (EN PROGRESO)
- [ ] Acceder a Render Dashboard actual
- [ ] Abrir Shell del Web Service
- [ ] Ejecutar comando pg_dump
- [ ] Copiar contenido del backup
- [ ] Guardar en: d:\ESCRITORIO\OpticaApp\backup_render.sql
- [ ] Verificar que el archivo no está vacío

## 📝 PASO 2: CREAR NUEVA CUENTA RENDER
- [ ] Ir a https://render.com/
- [ ] Registrar nueva cuenta (nuevo email O nuevo Team en cuenta actual)
- [ ] Verificar email
- [ ] Acceder al Dashboard

## 💳 PASO 3: ACTIVAR PLAN PROFESSIONAL
- [ ] En Dashboard, ir a Settings → Billing
- [ ] Seleccionar plan "Professional" ($19/mes)
- [ ] Agregar método de pago
- [ ] Confirmar suscripción
- [ ] Verificar que plan está activo

## 🗄️ PASO 4: CREAR NUEVA BASE DE DATOS
- [ ] En Dashboard nuevo, click "New +" → "PostgreSQL"
- [ ] Nombre: opticaapp-db
- [ ] Region: Ohio (US East) o más cercana
- [ ] PostgreSQL Version: 15 o 16
- [ ] Plan: Basic-1gb ($19/mes)
- [ ] Click "Create Database"
- [ ] Esperar provisión (2-3 minutos)

## 📋 PASO 5: COPIAR CREDENCIALES NUEVA BD
- [ ] En la nueva BD, ir a pestaña "Info"
- [ ] Copiar y guardar:
  - Internal Database URL
  - External Database URL
  - Hostname
  - Port
  - Database name
  - Username
  - Password

## 🔄 PASO 6: RESTAURAR BACKUP
- [ ] En nueva cuenta, crear Web Service temporal
- [ ] Conectar repositorio GitHub
- [ ] Configurar DATABASE_URL con nueva BD
- [ ] Abrir Shell del nuevo servicio
- [ ] Crear archivo con el backup
- [ ] Ejecutar: psql $DATABASE_URL < backup.sql
- [ ] Verificar que se restauró correctamente

## 🚀 PASO 7: CREAR WEB SERVICE DEFINITIVO
- [ ] Click "New +" → "Web Service"
- [ ] Conectar repositorio OpticaApp
- [ ] Configurar:
  - Name: opticaapp
  - Runtime: Python 3
  - Build Command: pip install -r requirements.txt && python manage.py collectstatic --noinput
  - Start Command: daphne -b 0.0.0.0 -p $PORT config.asgi:application

## ⚙️ PASO 8: CONFIGURAR VARIABLES DE ENTORNO
- [ ] DATABASE_URL (de la nueva BD)
- [ ] SECRET_KEY (generar nuevo)
- [ ] DEBUG=False
- [ ] ALLOWED_HOSTS=*.onrender.com
- [ ] DJANGO_SETTINGS_MODULE=config.settings
- [ ] PYTHONUNBUFFERED=1

## ✨ PASO 9: DEPLOY Y VERIFICACIÓN
- [ ] Esperar deploy completo
- [ ] Acceder a URL del nuevo servicio
- [ ] Hacer login
- [ ] Verificar datos (pacientes, exámenes, etc.)
- [ ] Probar crear nuevo registro
- [ ] Verificar todas las funcionalidades

## 🎯 PASO 10: LIMPIEZA Y CIERRE
- [ ] Documentar nueva URL
- [ ] Guardar credenciales en lugar seguro
- [ ] Mantener cuenta antigua activa por 1 semana (backup)
- [ ] Después de 1 semana, cancelar cuenta antigua

---

## 📞 CONTACTOS DE AYUDA
- Render Docs: https://render.com/docs
- Render Support: support@render.com
- Community: https://community.render.com/

## ⏱️ TIEMPO ESTIMADO TOTAL
- Backup: 10 minutos
- Crear cuenta nueva: 5 minutos
- Crear BD y restaurar: 15 minutos
- Configurar Web Service: 15 minutos
- Deploy y verificación: 10 minutos
- **TOTAL: ~55 minutos**

---

**ESTADO ACTUAL:** En PASO 1 - Esperando backup de base de datos
