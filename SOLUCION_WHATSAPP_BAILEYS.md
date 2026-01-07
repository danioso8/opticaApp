# Configuración y Solución de Problemas de WhatsApp (Baileys)

**Fecha**: 6 de Enero de 2026  
**Versión**: 1.0  
**Servidor**: Contabo VPS (84.247.129.180)

---

## 📋 Tabla de Contenidos

1. [Arquitectura del Sistema](#arquitectura-del-sistema)
2. [Configuración Inicial](#configuración-inicial)
3. [Problemas Comunes y Soluciones](#problemas-comunes-y-soluciones)
4. [Mantenimiento](#mantenimiento)
5. [Verificación de Estado](#verificación-de-estado)

---

## 🏗️ Arquitectura del Sistema

### Componentes

1. **Servidor WhatsApp (Node.js + Baileys)**
   - Puerto: 3000
   - Ubicación: `/var/www/whatsapp-server/`
   - Proceso: PM2 (ID: 3, nombre: `whatsapp-server`)
   - Sesiones: `/var/www/whatsapp-server/auth_sessions/`

2. **Aplicación Django (OpticaApp)**
   - Puerto: 8000
   - Ubicación: `/var/www/opticaapp/`
   - Proceso: PM2 (ID: 2, nombre: `opticaapp`)
   - Cliente: `apps/appointments/whatsapp_baileys_client.py`

3. **Base de Datos PostgreSQL**
   - Tabla: `appointments_notificationsettings`
   - Configuración por organización

### Flujo de Comunicación

```
Django App → whatsapp_baileys_client.py → HTTP (localhost:3000) → Servidor Node.js → WhatsApp API
```

---

## ⚙️ Configuración Inicial

### 1. Variables de Entorno (.env)

**Archivo**: `/var/www/opticaapp/.env`

```bash
# API Key para autenticación con servidor WhatsApp
WHATSAPP_SERVER_API_KEY=opticaapp_2026_whatsapp_baileys_secret_key_12345
```

**Importante**: Esta variable DEBE existir en el servidor de producción. Si falta, las peticiones a WhatsApp fallarán con error 401 Unauthorized.

### 2. Configuración de Notificaciones en Base de Datos

Para habilitar WhatsApp Baileys como método de notificación:

```python
# Ejecutar en shell de Django
from apps.appointments.models_notifications import NotificationSettings
from apps.organizations.models import Organization

# Para cada organización
for org in Organization.objects.all():
    settings = NotificationSettings.get_settings(org)
    settings.local_whatsapp_enabled = True  # Habilitar WhatsApp Baileys
    settings.email_enabled = False          # Deshabilitar Email
    settings.send_confirmation = True       # Confirmación al agendar
    settings.send_reminder = True           # Recordatorios
    settings.send_cancellation = True       # Cancelaciones
    settings.save()
```

**Script rápido desde servidor**:
```bash
cd /var/www/opticaapp
source venv/bin/activate
cat > /tmp/enable_wa.py << 'HEREDOC'
from apps.appointments.models_notifications import NotificationSettings
from apps.organizations.models import Organization

for org in Organization.objects.all():
    settings = NotificationSettings.get_settings(org)
    settings.local_whatsapp_enabled = True
    settings.email_enabled = False
    settings.save()
    print(f'{org.name}: WhatsApp Baileys habilitado')
HEREDOC

python manage.py shell < /tmp/enable_wa.py
```

### 3. Activación Automática al Conectar

El sistema ahora activa automáticamente las notificaciones cuando:
- Se escanea el QR y WhatsApp se conecta exitosamente
- El toggle "Habilitar Notificaciones por WhatsApp" se marca automáticamente

---

## 🔧 Problemas Comunes y Soluciones

### Problema 1: Error 401 Unauthorized

**Síntomas**:
```
Error en petición a WhatsApp server: 401 Client Error: Unauthorized for url: http://localhost:3000/api/status/2
```

**Causa**: Falta la variable `WHATSAPP_SERVER_API_KEY` en el archivo `.env`

**Solución**:
```bash
# Conectar al servidor
ssh root@84.247.129.180

# Agregar la variable al .env
echo 'WHATSAPP_SERVER_API_KEY=opticaapp_2026_whatsapp_baileys_secret_key_12345' >> /var/www/opticaapp/.env

# Reiniciar aplicación Django
pm2 restart opticaapp
```

---

### Problema 2: Error 500 Internal Server Error al Enviar Mensaje

**Síntomas**:
```
Error en petición a WhatsApp server: 500 Server Error: Internal Server Error for url: http://localhost:3000/api/send-message
Error al enviar mensaje: Connection Closed
```

**Causa**: Múltiples sesiones del mismo número o sesiones corruptas

**Solución**:
```bash
# Conectar al servidor
ssh root@84.247.129.180

# Ver sesiones existentes
ls -la /var/www/whatsapp-server/auth_sessions/

# Eliminar sesión conflictiva (ejemplo: organización 23)
rm -rf /var/www/whatsapp-server/auth_sessions/23/

# Reiniciar servidor WhatsApp
pm2 restart whatsapp-server

# Volver a escanear QR desde el dashboard
```

**Prevención**: Un número de WhatsApp solo puede conectarse en UNA organización a la vez.

---

### Problema 3: No Envía Notificaciones al Agendar Cita

**Síntomas**: Se agenda la cita pero no llega notificación por WhatsApp

**Diagnóstico**:
```bash
# Verificar configuración de notificaciones
cd /var/www/opticaapp
source venv/bin/activate
python check_notification_settings.py
```

**Debe mostrar**:
```
Método activo: local_whatsapp
WhatsApp Local (Baileys): ✅
Email: ❌
Confirmación: ✅
```

**Si muestra Email como método activo**:
```bash
# Ejecutar script de corrección
cat > /tmp/enable_wa.py << 'HEREDOC'
from apps.appointments.models_notifications import NotificationSettings
from apps.organizations.models import Organization

for org in Organization.objects.all():
    settings = NotificationSettings.get_settings(org)
    settings.local_whatsapp_enabled = True
    settings.email_enabled = False
    settings.save()
    print(f'{org.name}: WhatsApp Baileys habilitado')
HEREDOC

python manage.py shell < /tmp/enable_wa.py
```

---

### Problema 4: QR se Desconecta Inmediatamente Después de Escanear

**Síntomas**:
- QR se escanea correctamente
- Muestra "Conectado"
- Inmediatamente se desconecta

**Logs**:
```
Conexión cerrada para 2. Status: 515, Reconectar: true
Razón de desconexión: Stream Errored (restart required)
```

**Causa**: Sesión corrupta o conflicto con otra conexión del mismo número

**Solución**:
```bash
# 1. Eliminar todas las sesiones
rm -rf /var/www/whatsapp-server/auth_sessions/*

# 2. Reiniciar servidor WhatsApp
pm2 restart whatsapp-server

# 3. Volver a conectar desde dashboard
# 4. Escanear QR con el teléfono
```

---

### Problema 5: Connection Refused (Puerto 3000)

**Síntomas**:
```
Error en petición a WhatsApp server: HTTPConnectionPool(host='localhost', port=3000): Max retries exceeded
Failed to establish a new connection: [Errno 111] Connection refused
```

**Causa**: Servidor WhatsApp Node.js no está corriendo

**Solución**:
```bash
# Verificar estado
pm2 list

# Si no está corriendo, iniciar
pm2 start whatsapp-server

# Si falla, revisar logs
pm2 logs whatsapp-server --lines 50

# Reiniciar desde cero
cd /var/www/whatsapp-server
pm2 delete whatsapp-server
pm2 start server.js --name whatsapp-server
pm2 save
```

---

## 🔍 Verificación de Estado

### 1. Verificar Procesos PM2

```bash
ssh root@84.247.129.180
pm2 list
```

**Salida esperada**:
```
┌────┬────────────────────┬─────────┬──────────┬────────┬──────┬───────────┐
│ id │ name               │ mode    │ pid      │ uptime │ ↺    │ status    │
├────┼────────────────────┼─────────┼──────────┼────────┼──────┼───────────┤
│ 2  │ opticaapp          │ fork    │ 44903    │ 5h     │ 21   │ online    │
│ 3  │ whatsapp-server    │ fork    │ 45772    │ 5h     │ 4    │ online    │
└────┴────────────────────┴─────────┴──────────┴────────┴──────┴───────────┘
```

### 2. Verificar Logs de WhatsApp

```bash
# Últimas 50 líneas
pm2 logs whatsapp-server --lines 50 --nostream

# Seguir en tiempo real
pm2 logs whatsapp-server
```

**Logs normales**:
```
🚀 Servidor WhatsApp iniciado en puerto 3000
📱 API Key: opticaapp_2026_whatsapp_baileys_secret_key_12345
📂 Sesiones guardadas en: /var/www/whatsapp-server/auth_sessions
✅ WhatsApp conectado exitosamente para 2
📱 Número conectado: 573007915262
```

**Logs de error**:
```
Session error:Error: Bad MAC Error: Bad MAC
Conexión cerrada para 2. Status: 500
Error al enviar mensaje: Connection Closed
```

### 3. Verificar Configuración de Notificaciones

```bash
cd /var/www/opticaapp
source venv/bin/activate
python check_notification_settings.py
```

### 4. Verificar Variable de Entorno

```bash
grep WHATSAPP_SERVER_API_KEY /var/www/opticaapp/.env
```

**Debe mostrar**:
```
WHATSAPP_SERVER_API_KEY=opticaapp_2026_whatsapp_baileys_secret_key_12345
```

### 5. Verificar Conectividad

```bash
# Desde el servidor
curl http://localhost:3000/health

# Debería retornar: {"status":"ok"}
```

---

## 🔄 Mantenimiento

### Reinicio Completo del Servicio

```bash
# 1. Reiniciar servidor WhatsApp
pm2 restart whatsapp-server

# 2. Reiniciar aplicación Django
pm2 restart opticaapp

# 3. Verificar que ambos están online
pm2 list
```

### Limpieza de Sesiones Antiguas

```bash
# Eliminar sesiones con más de 30 días (opcional)
find /var/www/whatsapp-server/auth_sessions -type f -mtime +30 -delete
```

### Monitoreo Automático

PM2 reinicia automáticamente los procesos si se caen. Ver configuración:
```bash
pm2 startup
pm2 save
```

---

## 📊 Scripts de Utilidad

### Script: Verificar Estado Completo

```bash
#!/bin/bash
echo "=== Estado de Servicios WhatsApp ==="
echo ""
echo "1. Procesos PM2:"
pm2 list | grep -E "whatsapp|opticaapp"
echo ""
echo "2. Variable de Entorno:"
grep WHATSAPP_SERVER_API_KEY /var/www/opticaapp/.env
echo ""
echo "3. Último log de WhatsApp:"
pm2 logs whatsapp-server --lines 10 --nostream | tail -5
echo ""
echo "4. Sesiones activas:"
ls -l /var/www/whatsapp-server/auth_sessions/
```

### Script: Resetear WhatsApp Completamente

```bash
#!/bin/bash
echo "Reseteando WhatsApp Baileys..."

# 1. Eliminar todas las sesiones
rm -rf /var/www/whatsapp-server/auth_sessions/*

# 2. Reiniciar servidor WhatsApp
pm2 restart whatsapp-server

# 3. Reiniciar Django
pm2 restart opticaapp

echo "✅ Reset completado. Vuelve a escanear el QR desde el dashboard."
```

---

## 📝 Checklist de Solución de Problemas

Cuando WhatsApp no funciona, revisar en este orden:

- [ ] 1. ¿Está corriendo el servidor WhatsApp? (`pm2 list`)
- [ ] 2. ¿Está corriendo la aplicación Django? (`pm2 list`)
- [ ] 3. ¿Existe la variable `WHATSAPP_SERVER_API_KEY` en `.env`?
- [ ] 4. ¿La configuración de notificaciones tiene `local_whatsapp_enabled=True`?
- [ ] 5. ¿WhatsApp muestra estado "connected" en el dashboard?
- [ ] 6. ¿Hay sesiones conflictivas en `/var/www/whatsapp-server/auth_sessions/`?
- [ ] 7. ¿Los logs de WhatsApp muestran errores? (`pm2 logs whatsapp-server`)
- [ ] 8. ¿El número de WhatsApp está conectado en otra organización?

---

## 🆘 Comandos de Emergencia

```bash
# Resetear todo y empezar desde cero
ssh root@84.247.129.180
cd /var/www/whatsapp-server
rm -rf auth_sessions/*
pm2 restart whatsapp-server
pm2 restart opticaapp

# Luego desde el dashboard:
# 1. Ir a WhatsApp Baileys Config
# 2. Hacer clic en "Iniciar Sesión"
# 3. Escanear QR
# 4. Verificar que dice "Conectado"
# 5. Las notificaciones se activarán automáticamente
```

---

## 📞 Contacto de Soporte

Si ninguna solución funciona:
1. Revisar logs completos: `pm2 logs whatsapp-server --lines 200`
2. Revisar logs de Django: `pm2 logs opticaapp --lines 200`
3. Documentar el error exacto
4. Contactar al equipo de desarrollo

---

**Última actualización**: 6 de Enero de 2026  
**Autor**: Sistema OpticaApp  
**Versión del documento**: 1.0
