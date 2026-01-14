# 🎯 Sistema de Monitoreo y Auto-Corrección de Errores

## 📊 Resumen

OpticaApp ahora cuenta con **DOS sistemas de monitoreo de errores**:

1. **Sistema Interno** (Ya funcionando)
   - Dashboard en `/saas-admin/errors/`
   - Captura automática de errores
   - Almacenamiento en base de datos
   - 100% gratis y self-hosted

2. **Sentry** (Recién integrado - Requiere configuración)
   - Monitoreo profesional en la nube
   - 5,000 errores/mes GRATIS
   - Performance monitoring
   - Stack traces detallados
   - Alertas por email

3. **Bot Auto-Corrector** (¡NUEVO!)
   - Corrige errores comunes automáticamente
   - Se ejecuta manualmente o por cron
   - Reinicia servicios, limpia caché, ejecuta migraciones, etc.

---

## 🚀 Instalación Rápida

### En tu servidor Contabo:

```bash
# 1. Conectar al servidor
ssh root@84.247.129.180

# 2. Ir al directorio
cd /var/www/opticaapp

# 3. Activar virtual environment
source venv/bin/activate

# 4. Instalar Sentry
pip install sentry-sdk==1.40.0

# 5. Configurar variables de entorno (ver abajo)
nano .env
```

### Agregar a `.env`:

```bash
# Sentry Configuration (Obtener DSN en https://sentry.io)
SENTRY_DSN=https://TU_DSN_AQUI@o123456.ingest.sentry.io/7654321
ENVIRONMENT=production
APP_VERSION=1.0.0
```

### Reiniciar aplicación:

```bash
pm2 restart opticaapp
```

---

## 🤖 Bot Auto-Corrector de Errores

### ✅ Errores que puede corregir:

| Tipo de Error | Solución Automática |
|---------------|---------------------|
| **DatabaseError** | Cierra conexiones idle, ejecuta migraciones, limpia deadlocks |
| **ConnectionError** | Limpia caché de conexiones |
| **TimeoutError** | Limpia caché |
| **MemoryError** | Limpia caché + garbage collection |
| **PermissionError** | Ajusta permisos de archivos (chmod) |
| **FileNotFoundError** | Crea directorios faltantes |
| **ImportError** | Instala módulos faltantes (solo desarrollo) |

### 🎮 Comandos del Bot:

```bash
# Ejecutar auto-corrección manual
python manage.py auto_fix_errors

# Modo prueba (sin aplicar cambios)
python manage.py auto_fix_errors --dry-run
```

### ⏰ Configurar Auto-Corrección Automática (Cron):

```bash
# Editar crontab
crontab -e

# Agregar esta línea (ejecuta cada hora)
0 * * * * cd /var/www/opticaapp && source venv/bin/activate && python manage.py auto_fix_errors >> /var/log/opticaapp/auto_fix.log 2>&1
```

---

## 📋 Configuración de Sentry (Paso a Paso)

### 1. Crear cuenta en Sentry

1. Ir a https://sentry.io/signup/
2. Registrarse (gratis hasta 5,000 errores/mes)

### 2. Crear proyecto

1. Click en "Create Project"
2. Seleccionar: **Django**
3. Nombre: `opticaapp`
4. Click "Create Project"

### 3. Copiar DSN

Sentry mostrará algo como:
```
https://1234567890abcdef@o123456.ingest.sentry.io/7654321
```

**COPIAR COMPLETO este URL**

### 4. Configurar en servidor

```bash
# SSH al servidor
ssh root@84.247.129.180

# Editar .env
nano /var/www/opticaapp/.env

# Agregar al final:
SENTRY_DSN=https://TU_DSN_PEGADO_AQUI@o123456.ingest.sentry.io/7654321
ENVIRONMENT=production
APP_VERSION=1.0.0

# Guardar: Ctrl+O, Enter, Ctrl+X
```

### 5. Verificar instalación

```bash
# En el servidor
cd /var/www/opticaapp
source venv/bin/activate

# Ejecutar shell de Django
python manage.py shell

# Dentro del shell:
from config.sentry import capture_message
capture_message('¡Sentry configurado correctamente!')
exit()
```

Ve a tu dashboard de Sentry y deberías ver el mensaje.

### 6. Probar captura de errores

```bash
python manage.py shell

# Dentro del shell:
from config.sentry import capture_exception
try:
    1 / 0
except Exception as e:
    capture_exception(e)
exit()
```

Deberías ver el error en Sentry con stack trace completo.

---

## 🎯 Dashboards Disponibles

### 1. Dashboard Interno (Ya funcionando)
- **URL:** http://84.247.129.180/saas-admin/errors/
- **Features:**
  - Estadísticas de errores
  - Gráfico de tendencias (7 días)
  - Lista de errores recientes
  - Top 10 errores frecuentes
  - Filtros por severidad y estado
  - Admin completo con stack traces

### 2. Dashboard de Sentry (Una vez configurado)
- **URL:** https://sentry.io/
- **Features:**
  - Stack traces enriquecidos
  - Performance monitoring
  - Source maps
  - Alertas por email
  - Integración con Slack, GitHub, etc.
  - Releases tracking

---

## 🔧 Uso del Sistema

### Capturar mensaje personalizado en Sentry:

```python
from config.sentry import capture_message

capture_message('Usuario completó checkout', level='info')
```

### Capturar excepción en Sentry:

```python
from config.sentry import capture_exception

try:
    # Tu código
    pass
except Exception as e:
    capture_exception(e)
```

### Configurar usuario en contexto:

```python
from config.sentry import set_user

set_user(
    user_id=request.user.id,
    email=request.user.email,
    username=request.user.username
)
```

### Agregar contexto personalizado:

```python
from config.sentry import set_context

set_context('payment', {
    'amount': 100.00,
    'currency': 'COP',
    'method': 'card'
})
```

### Agregar breadcrumb:

```python
from config.sentry import add_breadcrumb

add_breadcrumb(
    message='Usuario inició pago',
    category='payment',
    level='info',
    data={'amount': 100.00}
)
```

---

## 📊 Comparación: Sistema Interno vs Sentry

| Característica | Sistema Interno | Sentry |
|----------------|-----------------|--------|
| **Costo** | ✅ Gratis (self-hosted) | ✅ Gratis hasta 5K errors/mes |
| **Stack traces** | ✅ Completos | ✅ Enriquecidos con source maps |
| **Performance** | ❌ No | ✅ Sí (APM) |
| **Alertas** | ⚠️ Básicas | ✅ Avanzadas (email, Slack, etc.) |
| **Búsqueda** | ✅ Sí | ✅ Avanzada |
| **Privacidad** | ✅ 100% tuyo | ⚠️ En cloud de Sentry |
| **Mantenimiento** | ⚠️ Lo haces tú | ✅ Ninguno |
| **Releases** | ❌ No | ✅ Sí |
| **Integraciones** | ❌ No | ✅ Muchas |

**Recomendación:** Usar ambos
- **Sistema Interno:** Para desarrollo y backup
- **Sentry:** Para producción y alertas críticas

---

## ⚠️ Limitaciones del Bot

### ❌ El bot NO puede:
- Corregir bugs de lógica en tu código
- Escribir código nuevo
- Corregir errores de sintaxis
- Resolver problemas de diseño
- Arreglar errores de negocio

### ✅ El bot SÍ puede:
- Reiniciar servicios caídos
- Limpiar caché corrupto
- Ejecutar migraciones faltantes
- Ajustar permisos de archivos
- Crear directorios faltantes
- Optimizar base de datos
- Cerrar conexiones idle
- Liberar memoria

---

## 🔒 Seguridad

### Datos sensibles filtrados automáticamente:

En ambos sistemas (interno y Sentry), se filtran:
- Passwords
- Tokens
- API Keys
- Secrets
- Credit cards
- CVV
- Cookies de sesión
- Headers de autenticación

---

## 📝 Logs

### Ver logs del bot auto-corrector:

```bash
# Si configuraste cron, los logs estarán en:
tail -f /var/log/opticaapp/auto_fix.log

# Si ejecutas manual:
python manage.py auto_fix_errors
```

### Ver logs de Sentry en Django:

```bash
# En producción
pm2 logs opticaapp | grep -i sentry
```

---

## 🎓 Recursos Adicionales

- **Documentación interna:** `SISTEMA_MONITOREO_ERRORES.md`
- **Sentry Docs:** https://docs.sentry.io/platforms/python/guides/django/
- **Setup script:** `python setup_sentry.py`

---

## 📞 Soporte

- **Dashboard interno:** http://84.247.129.180/saas-admin/errors/
- **Sentry:** https://sentry.io/
- **Issues:** Reportar en el proyecto

---

**Fecha:** 13 de Enero 2026  
**Versión:** 1.0.0  
**Estado:** ✅ Listo para producción
