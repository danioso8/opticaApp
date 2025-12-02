# 📱 Integración de WhatsApp - Sistema de Notificaciones

## 🌟 Características

Sistema de notificaciones gratuito por WhatsApp usando **Baileys** (WhatsApp Web API).

✅ **100% Gratuito** - Sin costos mensuales
✅ **Sin límites** - Envía mensajes ilimitados
✅ **Fácil de configurar** - Solo necesitas escanear un código QR
✅ **Multi-organización** - Mensajes personalizados por sucursal

---

## 📋 Requisitos

- Node.js 14+ instalado
- Un número de WhatsApp disponible
- Acceso al teléfono para escanear QR

---

## 🚀 Configuración Inicial

### 1. Instalar Dependencias

```bash
cd whatsapp-bot
npm install
```

### 2. Iniciar el Bot

```bash
npm start
```

Verás algo como:
```
🚀 ================================
   Servidor WhatsApp Bot iniciado
   http://localhost:3000
================================

📱 Para conectar WhatsApp, ve a:
   http://localhost:3000/qr
```

### 3. Conectar WhatsApp

1. Abre tu navegador en: `http://localhost:3000/qr`
2. Verás un código QR grande
3. En tu teléfono:
   - Abre **WhatsApp**
   - Ve a **Menú (⋮)** → **Dispositivos vinculados**
   - Toca **Vincular un dispositivo**
   - Escanea el código QR

✅ ¡Listo! El bot está conectado

---

## 📤 ¿Cómo Funciona?

### Notificaciones Automáticas

El sistema envía automáticamente mensajes de WhatsApp cuando:

1. **Nueva Cita Agendada** - Confirmación inmediata
2. **Recordatorio** - 1 día antes de la cita (requiere cronjob)
3. **Cancelación** - Cuando se cancela una cita

### Flujo de Envío

```
Cliente agenda cita → Sistema crea appointment → 
Serializer llama a whatsapp_local.py → 
Bot envía mensaje por WhatsApp → Cliente recibe notificación
```

---

## 🛠️ Comandos de Gestión

### Verificar Estado del Bot

```bash
python manage.py test_whatsapp
```

Resultado:
```
🔍 Verificando bot de WhatsApp en http://localhost:3000...

✅ Servidor está corriendo
✅ WhatsApp está conectado

✅ Todo listo para enviar notificaciones
```

### Enviar Mensaje de Prueba

```bash
python manage.py test_whatsapp --phone 3001234567
```

---

## 💻 Uso en el Dashboard

### Panel de Estado

En el **Dashboard Principal** verás una tarjeta de "Estado de WhatsApp":

- 🟢 **Verde**: Todo funcionando correctamente
- 🟡 **Amarillo**: Servidor corriendo, pero necesita conectar WhatsApp
- 🔴 **Rojo**: Servidor no está corriendo

### Botones de Acción

- **Actualizar**: Verifica el estado actual
- **Probar**: Envía un mensaje de prueba
- **Ver QR**: Conecta o reconecta WhatsApp

---

## 📝 Personalización de Mensajes

Los mensajes se personalizan automáticamente con:

- ✅ Nombre de la organización
- ✅ Dirección completa (calle, barrio, ciudad)
- ✅ Teléfono de contacto
- ✅ Datos de la cita (fecha, hora)

### Ejemplo de Mensaje

```
👓 *COMPUEASYS*

¡Hola Juan Pérez!

✅ Tu cita ha sido agendada exitosamente:

📅 *Fecha:* 05/12/2024
🕐 *Hora:* 02:00 PM
📍 *Dirección:* Calle 123, Centro, Bogotá

💡 *Recomendaciones:*
• Llega 10 minutos antes
• Trae tu documento de identidad
• Si usas lentes, tráelos contigo

❓ *¿Necesitas cancelar o reagendar?*
Llámanos al: 3001234567

¡Te esperamos! 😊
```

---

## 🔧 Configuración Avanzada

### Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto:

```env
# WhatsApp Bot Local
WHATSAPP_API_URL=http://localhost:3000

# Información del Negocio
BUSINESS_PHONE=300 123 4567
WEBSITE_URL=http://127.0.0.1:8000
```

### Puerto Personalizado

Edita `whatsapp-bot/server.js`:

```javascript
const PORT = process.env.PORT || 3000; // Cambia 3000 por el puerto deseado
```

---

## 🐛 Solución de Problemas

### Bot no conecta

**Problema**: El QR no aparece o no conecta

**Solución**:
```bash
cd whatsapp-bot
rm -rf auth_info  # Eliminar sesión anterior
npm start
```

### Mensajes no se envían

**Problema**: Los mensajes no llegan

**Verificar**:
1. Bot está corriendo: `python manage.py test_whatsapp`
2. WhatsApp está conectado (QR escaneado)
3. Número de teléfono es válido (formato: 3001234567)

### Servidor no inicia

**Problema**: Error al ejecutar `npm start`

**Solución**:
```bash
cd whatsapp-bot
rm -rf node_modules package-lock.json
npm install
npm start
```

---

## 📊 Monitoreo

### Logs del Bot

El bot muestra logs en la terminal:

```
✅ Mensaje enviado a 573001234567
❌ Error al enviar mensaje: ...
```

### Dashboard Django

Verifica el estado en tiempo real en:
- **Dashboard Principal** → Tarjeta "Estado de WhatsApp"
- Actualización automática cada 30 segundos

---

## 🔒 Seguridad

### Datos de Autenticación

Los datos de sesión se guardan en: `whatsapp-bot/auth_info/`

⚠️ **IMPORTANTE**: 
- **NO** subir `auth_info/` a Git
- Ya está en `.gitignore`
- Contiene la sesión de WhatsApp Web

### Producción

Para desplegar en producción:

1. **Servidor dedicado**: El bot necesita correr 24/7
2. **PM2**: Mantener el proceso vivo
   ```bash
   npm install -g pm2
   cd whatsapp-bot
   pm2 start server.js --name whatsapp-bot
   pm2 save
   pm2 startup
   ```

3. **Backup de sesión**: Guarda `auth_info/` regularmente

---

## 🎯 Próximos Pasos

### Recordatorios Automáticos

Configura un cronjob para enviar recordatorios:

```bash
# Editar crontab
crontab -e

# Agregar (ejecutar todos los días a las 9 AM)
0 9 * * * cd /ruta/proyecto && python manage.py send_reminders
```

### Crear comando de recordatorios

```python
# apps/appointments/management/commands/send_reminders.py
from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from apps.appointments.models import Appointment
from apps.appointments.whatsapp_local import whatsapp_notifier

class Command(BaseCommand):
    help = 'Envía recordatorios de citas para mañana'

    def handle(self, *args, **options):
        tomorrow = timezone.now().date() + timedelta(days=1)
        appointments = Appointment.objects.filter(
            appointment_date=tomorrow,
            status__in=['pending', 'confirmed']
        )
        
        sent = 0
        for apt in appointments:
            if whatsapp_notifier.send_appointment_reminder(apt):
                sent += 1
        
        self.stdout.write(
            self.style.SUCCESS(f'✅ {sent} recordatorios enviados')
        )
```

---

## 📚 Recursos Adicionales

- **Baileys Documentation**: https://github.com/WhiskeySockets/Baileys
- **Node.js**: https://nodejs.org/
- **PM2 Process Manager**: https://pm2.keymetrics.io/

---

## 🤝 Soporte

Si tienes problemas:

1. Revisa esta documentación
2. Ejecuta: `python manage.py test_whatsapp`
3. Verifica logs del bot en la terminal
4. Revisa el panel de estado en el dashboard

---

## ✅ Checklist de Verificación

- [ ] Node.js instalado
- [ ] Dependencias instaladas (`npm install`)
- [ ] Bot iniciado (`npm start`)
- [ ] QR escaneado
- [ ] Estado verde en dashboard
- [ ] Mensaje de prueba enviado exitosamente

---

**¡Listo!** Tu sistema ahora envía notificaciones por WhatsApp automáticamente 🎉
