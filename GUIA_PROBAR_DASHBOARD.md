# 🎯 GUÍA RÁPIDA: Probar Dashboard de Notificaciones

## 🚀 Paso 1: Servidor Local (Ya está corriendo)

El servidor está activo en: **http://127.0.0.1:8000**

---

## 🔐 Paso 2: Iniciar Sesión

1. Ve a: http://127.0.0.1:8000/dashboard/login/
2. Inicia sesión con tu usuario

---

## ⚙️ Paso 3: Acceder a Configuración de Notificaciones

### Opción A: Desde el menú sidebar

1. En el dashboard, busca el menú lateral izquierdo
2. Haz clic en **"Configuración"** (ícono de engranaje)
3. Se desplegará un submenú
4. Haz clic en **"WhatsApp Twilio"**

### Opción B: URL directa

Simplemente ve a: http://127.0.0.1:8000/dashboard/configuracion/notificaciones/

---

## 🎨 Paso 4: Interfaz de Configuración

Verás 3 tarjetas principales:

### 📱 1. WhatsApp Twilio (Verde)
- **Costo**: $0.005/mensaje
- **Estado**: "Producción • Recomendado"
- **Uso**: Para enviar notificaciones a tus clientes desde tu cuenta Twilio

**Para activar:**
- ✅ Activa el toggle "Habilitar WhatsApp con Twilio"
- 📝 Ingresa tu Account SID (comienza con AC...)
- 🔐 Ingresa tu Auth Token
- 📞 Ingresa el número WhatsApp de Twilio (ej: whatsapp:+14155238886)
- 💾 Click en "Sincronizar WhatsApp"

### 📱 2. WhatsApp Local (Azul)
- **Costo**: GRATIS
- **Estado**: "Desarrollo • Gratis"
- **Uso**: Solo para desarrollo local (NO funciona en producción)

**Para activar:**
- ✅ Activa el toggle "Habilitar WhatsApp Local"
- 🌐 URL: http://localhost:3000 (por defecto)
- ⚠️ Requiere tener el bot corriendo: `cd whatsapp-bot && npm start`

### 📧 3. Email (Cyan)
- **Costo**: GRATIS
- **Estado**: "Producción • Gratis"
- **Uso**: Alternativa 100% gratuita que funciona en cualquier lado

**Para activar:**
- ✅ Activa el toggle "Habilitar Notificaciones por Email"
- 📧 Email remitente (opcional): deja vacío para usar el por defecto

---

## 🔔 Paso 5: Configurar Notificaciones Automáticas

Más abajo verás 3 opciones con iconos:

- ✅ **Confirmación de Cita** (verde): Al agendar una cita nueva
- ⏰ **Recordatorio** (azul): 1 día antes de la cita
- ❌ **Cancelación** (rojo): Al cancelar una cita

Activa/desactiva según necesites.

---

## 🧪 Paso 6: Probar el Sistema

### Test de Email (100% funcional si configuraste SMTP):

1. Click en el botón **"Enviar Email de Prueba"**
2. Ingresa tu email
3. Click "Enviar"
4. Revisa tu bandeja de entrada

### Test de WhatsApp Twilio:

1. Click en el botón **"Enviar Prueba"** (en la sección Twilio)
2. Ingresa tu número de WhatsApp (ej: 3001234567)
3. Click "Enviar"
4. Revisa tu WhatsApp

### Test de WhatsApp Local:

1. Asegúrate de tener el bot corriendo: `cd whatsapp-bot && npm start`
2. Escanea el QR si es la primera vez
3. Click en **"Ver Código QR"** o **"Enviar Prueba"**

---

## ✅ Paso 7: Guardar Configuración

1. Después de configurar todo, scroll hasta abajo
2. Click en el botón grande azul: **"Guardar Configuración"**
3. Verás un mensaje de éxito

---

## 🎯 Paso 8: Ver el Método Activo

En la parte inferior, verás una tarjeta morada/azul con gradiente que dice:

**"Método de Notificación Activo"**

Mostrará cuál método está usando el sistema:
- 🟢 **WhatsApp (Twilio)** - Si configuraste Twilio
- 🔵 **WhatsApp Local** - Si tienes el bot local activo
- 🟦 **Email** - Si tienes email habilitado
- 🔴 **Ninguno configurado** - Si no hay nada activo

El sistema usa esta prioridad:
1. Twilio (si está configurado)
2. WhatsApp Local (si está corriendo)
3. Email (siempre disponible como fallback)

---

## 🔍 Verificación Visual

### Indicadores de Estado:

1. **Badges de color**:
   - 🟢 Verde "Activo" - El método está habilitado
   - ⚪ Gris "Inactivo" - El método está deshabilitado

2. **Estado de Conexión** (arriba):
   - 🔵 Spinner girando - Verificando...
   - 🟢 Check verde - Conectado
   - 🔴 Exclamación roja - Sin configurar

3. **Botones disponibles**:
   - 🔄 "Sincronizar WhatsApp" - Conecta con Twilio
   - 📱 "Enviar Prueba" - Test de mensaje
   - 🔍 "Ver QR Code" - Para WhatsApp Local
   - 💾 "Guardar Configuración" - Guarda cambios

---

## 🚨 Troubleshooting

### "No aparece el menú de Configuración"
- Verifica que estés logueado
- El menú debe decir "Configuración" con un ícono de engranaje ⚙️
- Está debajo de "Gestión de Citas"

### "Error 404 al ir a notificaciones"
- La URL correcta es: `/dashboard/configuracion/notificaciones/`
- Verifica que el servidor esté corriendo

### "No se guarda la configuración"
- Verifica que el botón "Guardar Configuración" sea azul
- Debe estar al final de la página
- Checa la consola del navegador (F12) para ver errores

### "Test de Twilio falla"
- Verifica que el Account SID comience con "AC"
- El Auth Token debe ser tu token real (no el test)
- El formato del número debe ser: `whatsapp:+14155238886`

---

## 📸 Capturas Esperadas

### Vista del Dashboard:
```
┌─────────────────────────────────────────┐
│ 🌊 OpticaApp                            │
├─────────────────────────────────────────┤
│ 📊 Dashboard                            │
│ 📅 Gestión de Citas ▼                   │
│   └─ 📋 Lista de Citas                  │
│   └─ 📅 Calendario                      │
│   └─ ⏰ Horarios y Fechas               │
│ ⚙️  Configuración ▼                     │
│   └─ 📱 WhatsApp Twilio  ← AQUÍ        │
└─────────────────────────────────────────┘
```

### Vista de Notificaciones:
```
┌─────────────────────────────────────────────────┐
│  🌊 WhatsApp Twilio                             │
│  ← Volver                                       │
├─────────────────────────────────────────────────┤
│ Estado de Conexión                              │
│ 🔵 No configurado                               │
│                         [Verificar Conexión]    │
├─────────────────────────────────────────────────┤
│ [Verde] WhatsApp Twilio     💵 $0.005/mensaje  │
│ ┌─────────────────────────────────────────┐    │
│ │ ℹ️  Sobre Twilio: Servicio profesional  │    │
│ │ Incluye $15 de crédito gratis...        │    │
│ └─────────────────────────────────────────┘    │
│ ⚪→🟢 Habilitar WhatsApp con Twilio            │
│ [Account SID]  AC...                           │
│ [Auth Token]   ••••••••  👁️                    │
│ [WhatsApp From] whatsapp:+14155238886          │
│ [Sincronizar] [Enviar Prueba] [Ver QR]        │
├─────────────────────────────────────────────────┤
│ [Azul] WhatsApp Local       💯 GRATIS          │
│ ... (similar)                                   │
├─────────────────────────────────────────────────┤
│ [Cyan] Email               💯 GRATIS           │
│ ... (similar)                                   │
├─────────────────────────────────────────────────┤
│ 🔔 Notificaciones Automáticas                  │
│ [✓] Confirmación  [✓] Recordatorio [✓] Cancel │
├─────────────────────────────────────────────────┤
│ 📡 Método Activo: Email                        │
├─────────────────────────────────────────────────┤
│        [💾 Guardar Configuración]              │
└─────────────────────────────────────────────────┘
```

---

## 🎉 ¡Listo!

Si ves la interfaz como se describe arriba, **¡todo está funcionando correctamente!** 🚀

Puedes configurar:
- ✅ Twilio para producción ($0.005/mensaje)
- ✅ Email para alternativa gratis (Gmail SMTP)
- ✅ WhatsApp Local para desarrollo (gratis, localhost)

---

## 📱 Para Sincronizar en Render:

Una vez que funcione local, sigue los pasos en **COMANDOS_RENDER.md** para configurar en producción.

La diferencia es que en Render:
- No usarás WhatsApp Local (no funciona en la nube)
- Configurarás Email SMTP o Twilio
- Cada usuario puede configurar su propio Twilio desde el dashboard

¿Necesitas ayuda con algo específico? 🤔
