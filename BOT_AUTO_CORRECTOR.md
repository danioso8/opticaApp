# 🤖 Bot Auto-Corrector de Errores - Sistema Interno

## ✅ Lo que tenemos (Ya funcionando)

**Sistema de Monitoreo Propio:**
- Dashboard en `/saas-admin/errors/`
- Captura automática de errores (ErrorCaptureMiddleware)
- Base de datos completa de errores
- Filtros y búsquedas avanzadas
- ¡100% gratis y tuyo!

## 🆕 Lo que agregamos HOY

**Bot Auto-Corrector Inteligente:**
- Detecta errores comunes
- Los corrige automáticamente
- Sin necesidad de intervención manual
- Ejecutable por cron cada hora

**Configuración SSH sin contraseña:**
- Autenticación automática con claves SSH
- No más prompts de contraseña
- Deployment más rápido y automatizado

---

## 🔑 Configuración Inicial (Una sola vez)

### Paso 1: Generar clave SSH en Windows

```powershell
# Generar clave SSH sin contraseña
ssh-keygen -t rsa -b 4096 -f "$env:USERPROFILE\.ssh\id_rsa" -N '""'
```

### Paso 2: Copiar clave al servidor

```powershell
# Copiar clave pública al servidor (pedirá contraseña por última vez)
type "$env:USERPROFILE\.ssh\id_rsa.pub" | ssh root@84.247.129.180 "mkdir -p ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 700 ~/.ssh && chmod 600 ~/.ssh/authorized_keys"
```

### Paso 3: Verificar

```powershell
# Probar conexión (ya no debería pedir contraseña)
ssh root@84.247.129.180 "echo 'Conexión exitosa!' && hostname"
```

✅ **¡Listo!** Ahora puedes ejecutar comandos SSH sin contraseña.

---

## 📦 Archivos del Bot

### 1. `apps/audit/error_auto_fix.py`
Sistema principal de auto-corrección con:
- 7+ tipos de errores detectables
- Correcciones contextuales
- Reportes detallados
- Acciones proactivas

### 2. `apps/audit/management/commands/auto_fix_errors.py`
Comando Django para ejecutar el bot:
```bash
python manage.py auto_fix_errors
python manage.py auto_fix_errors --dry-run  # Modo prueba
```

---

## 🔧 Errores que Corrige Automáticamente

### 1. DatabaseError
- ✅ **Too many connections** → Cierra conexiones idle
- ✅ **Tabla no existe** → Ejecuta migraciones
- ✅ **Deadlock** → Limpia transacciones

### 2. ConnectionError  
- ✅ **Connection refused** → Limpia caché
- ✅ **Connection timeout** → Reinicia conexión

### 3. TimeoutError
- ✅ **Timeout** → Limpia caché

### 4. MemoryError
- ✅ **Memory overflow** → Garbage collection + limpia caché

### 5. PermissionError
- ✅ **Permisos de archivos** → Ajusta chmod

### 6. FileNotFoundError
- ✅ **Directorio faltante** → Crea directorios

### 7. ImportError/ModuleNotFoundError
- ✅ **Módulo faltante** → Instala paquete (solo desarrollo)

---

## 🚀 Deployment al Servidor

### ✅ Con SSH sin contraseña (Recomendado)

```powershell
# 1. Subir archivos (sin pedir contraseña)
scp apps\audit\error_auto_fix.py root@84.247.129.180:/var/www/opticaapp/apps/audit/
scp apps\audit\management\commands\auto_fix_errors.py root@84.247.129.180:/var/www/opticaapp/apps/audit/management/commands/

# 2. Subir templates del SaaS Admin
scp apps\admin_dashboard\templates\admin_dashboard\base.html root@84.247.129.180:/var/www/opticaapp/apps/admin_dashboard/templates/admin_dashboard/
scp apps\admin_dashboard\templates\admin_dashboard\error_monitoring.html root@84.247.129.180:/var/www/opticaapp/apps/admin_dashboard/templates/admin_dashboard/

# 3. Reiniciar aplicación
ssh root@84.247.129.180 "cd /var/www/opticaapp && pm2 restart opticaapp"

# 4. Configurar cron automático (ejecuta cada hora)
ssh root@84.247.129.180 "mkdir -p /var/log/opticaapp && (crontab -l 2>/dev/null; echo '0 * * * * cd /var/www/opticaapp && source venv/bin/activate && python manage.py auto_fix_errors >> /var/log/opticaapp/auto_fix.log 2>&1') | crontab -"

# 5. Verificar cron
ssh root@84.247.129.180 "crontab -l"

# 6. Probar el bot
ssh root@84.247.129.180 "cd /var/www/opticaapp && source venv/bin/activate && python manage.py auto_fix_errors --dry-run"
```

### Opción 2: Manual (Paso a Paso)

```powershell
# 1. Subir archivos
scp apps\audit\error_auto_fix.py root@84.247.129.180:/var/www/opticaapp/apps/audit/
scp apps\audit\management\commands\auto_fix_errors.py root@84.247.129.180:/var/www/opticaapp/apps/audit/management/commands/

# 2. Conectar al servidor
ssh root@84.247.129.180

# 3. En el servidor:
cd /var/www/opticaapp
mkdir -p apps/audit/management/commands
touch apps/audit/management/__init__.py
touch apps/audit/management/commands/__init__.py
source venv/bin/activate
pm2 restart opticaapp

# 4. Probar el bot
python manage.py auto_fix_errors --dry-run
```

---

## 🎮 Uso del Bot

### Ejecutar manualmente:
```bash
# Modo normal (aplica correcciones)
python manage.py auto_fix_errors

# Modo prueba (solo reporta)
python manage.py auto_fix_errors --dry-run
```

### Automatizar con Cron (cada hora):

**Opción A: Desde tu PC Windows (con SSH sin contraseña)**
```powershell
ssh root@84.247.129.180 "mkdir -p /var/log/opticaapp && (crontab -l 2>/dev/null; echo '0 * * * * cd /var/www/opticaapp && source venv/bin/activate && python manage.py auto_fix_errors >> /var/log/opticaapp/auto_fix.log 2>&1') | crontab -"
```

**Opción B: Desde el servidor**
```bash
# Conectar al servidor
ssh root@84.247.129.180

# Editar crontab
crontab -e

# Agregar esta línea
0 * * * * cd /var/www/opticaapp && source venv/bin/activate && python manage.py auto_fix_errors >> /var/log/opticaapp/auto_fix.log 2>&1

# Guardar y salir (Ctrl+O, Enter, Ctrl+X en nano)
```

**Verificar cron configurado:**
```bash
crontab -l
```

**Ver logs del bot:**
```bash
tail -f /var/log/opticaapp/auto_fix.log
```

---

## 📊 Ejemplo de Salida

```
🤖 Iniciando auto-corrección de errores...

✅ Proceso completado:
  • Correcciones aplicadas: 3
  • Correcciones fallidas: 1

📝 Correcciones exitosas:
  • Error #45: DatabaseError - fix_database_error
  • Error #47: TimeoutError - fix_timeout_error
  • Error #52: MemoryError - fix_memory_error

⚠️ Correcciones fallidas:
  • Error #48: ValueError - Handler returned False
```

---

## ⚠️ Limitaciones del Bot

### ❌ NO puede corregir:
- Bugs de lógica de negocio
- Errores de sintaxis en código
- Problemas de diseño
- Errores de validación de datos

### ✅ SÍ puede corregir:
- Problemas de infraestructura
- Errores de conexión/recursos
- Permisos de archivos
- Directorios faltantes
- Caché corrupto
- Migraciones pendientes

---

## 🔍 Monitoreo de Errores

### Dashboard Interno:
```
http://84.247.129.180/saas-admin/errors/
```

**Características:**
- 📊 Estadísticas en tiempo real
- 📈 Gráfico de tendencias (7 días)
- 🔍 Búsqueda y filtros avanzados
- 📋 Lista de errores recientes
- 🏆 Top 10 errores frecuentes
- 🎯 Severidad por colores
- ✅ Sistema de resolución

### Admin de Django:
```
http://84.247.129.180/admin/audit/errorlog/
```

**Características:**
- Stack traces completos
- Filtros por tipo, severidad, fecha
- Búsqueda full-text
- Acciones masivas
- Exportación de datos

---

## 🎯 Flujo de Trabajo Recomendado

1. **Monitoreo Pasivo:**
   - Dashboard en `/saas-admin/errors/` captura TODO
   - Sistema registra automáticamente cada error
   
2. **Auto-Corrección (Cron cada hora):**
   - Bot revisa errores sin resolver
   - Aplica correcciones automáticas
   - Genera reporte en log
   
3. **Revisión Manual:**
   - Errores que el bot no pudo corregir
   - Requieren intervención humana
   - Se marcan como resueltos manualmente

---

## 🔐 Seguridad

**Datos filtrados automáticamente:**
- Passwords
- Tokens
- API Keys
- Secrets
- Credit cards
- Cookies de sesión

---

## 📝 Logs

### Ver logs del bot:
```bash
# Si usas cron:
tail -f /var/log/opticaapp/auto_fix.log

# Si ejecutas manual:
python manage.py auto_fix_errors
```
Checklist de Implementación

- [x] **Configurar SSH sin contraseña**
  - Generar clave SSH
  - Copiar al servidor
  - Verificar conexión

- [x] **Subir archivos del bot**
  - error_auto_fix.py
  - auto_fix_errors.py (comando Django)
  - Templates del SaaS Admin

- [x] **Configurar cron automático**
  - Crear directorio de logs
  - Agregar tarea a crontab
  - Verificar configuración

- [x] **Verificar funcionamiento**
  - Probar bot con --dry-run
  - Ver menú en SaaS Admin
  - Revisar logs

- [ ] **Monitoreo continuo**
  - Revisar dashboard de errores semanalmente
  - Verificar logs del bot mensualmente
  - Ajustar correcciones según necesites

---

## 📸 Captura de pantalla esperada

Después de configurar todo, deberías ver:

**En el SaaS Admin (`/saas-admin/`):**
```
Sidebar:
  📊 Dashboard
  👥 Usuarios
  💳 Suscripciones
  🏢 Organizaciones
  📦 Planes
  🧩 Módulos
  ⚠️ Monitoreo de Errores  ← NUEVO
```

**En el cron:**
```bash
$ crontab -l
0 2 * * * /var/www/opticaapp/backup_automatico.sh
0 * * * * cd /var/www/opticaapp && source venv/bin/activate && python manage.py auto_fix_errors >> /var/log/opticaapp/auto_fix.log 2>&1
```

## 🆚 Ventajas vs Sentry (Externo)

| Característica | Sistema Interno + Bot | Sentry Externo |
|----------------|----------------------|----------------|
| **Costo** | ✅ $0 (100% gratis) | ⚠️ $0 hasta 5K errors, luego $$$$ |
| **Privacidad** | ✅ 100% tuyo | ❌ En cloud de terceros |
| **Personalizable** | ✅ Totalmente | ❌ Limitado |
| **Auto-corrección** | ✅ Sí (nuestro bot) | ❌ No |
| **Setup** | ✅ Ya está | ⚠️ Requiere cuenta + config |
| **Integración** | ✅ Nativo en Django | ⚠️ SDK externo |
| **Control total** | ✅ Sí | ❌ No |

---

## 🎓 Próximos Pasos

1. ✅ Subir archivos del bot al servidor
2. ✅ Probar con `--dry-run`
3. ✅ Configurar cron para ejecución automática
4. ✅ Revisar dashboard de errores regularmente
5. ✅ Ajustar correcciones según necesites

---

## 📞 Soporte

- **Dashboard:** http://84.247.129.180/saas-admin/errors/
- **Admin:** http://84.247.129.180/admin/audit/errorlog/
- **Documentación:** SISTEMA_MONITOREO_ERRORES.md

---

**Fecha:** 13 de Enero 2026  
**Versión:** 1.0.0  
**Estado:** ✅ Listo para deployment
