# Configuración de Twilio WhatsApp en Render

## Error actual
```
HTTP 401 error: Unable to create record: Authenticate
```

Este error indica que las credenciales de Twilio no están configuradas correctamente o son inválidas.

## Pasos para configurar Twilio WhatsApp en Render

### 1. Obtener credenciales de Twilio

1. Ve a **Twilio Console**: https://console.twilio.com
2. En el Dashboard principal, encontrarás:
   - **Account SID** (comienza con `AC...`)
   - **Auth Token** (haz clic en "Show" para verlo)

### 2. Configurar WhatsApp Sandbox (para pruebas)

1. Ve a: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
2. Sigue las instrucciones para unir tu número a la sandbox:
   - Envía un mensaje WhatsApp al número proporcionado
   - Envía el código que te indican (ej: `join <código>`)
3. El número de la sandbox es: **+1 415 523 8886** (en formato E.164: `+14155238886`)

### 3. Configurar variables de entorno en Render

1. Ve a tu servicio en Render Dashboard
2. Click en **Environment** en el menú lateral
3. Agrega o actualiza estas variables:

```bash
# Credenciales de Twilio
TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
TWILIO_AUTH_TOKEN=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx

# Número de WhatsApp (Sandbox para pruebas)
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

⚠️ **IMPORTANTE**: 
- El `TWILIO_ACCOUNT_SID` debe comenzar con `AC`
- El `TWILIO_AUTH_TOKEN` es tu Auth Token completo (32 caracteres)
- El formato del número debe ser: `whatsapp:+14155238886`

### 4. Verificar las credenciales

**Formato correcto del Account SID:**
```
ACxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
(AC seguido de 32 caracteres hexadecimales)
```

**Formato correcto del Auth Token:**
```
xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
(32 caracteres hexadecimales)
```

### 5. Después de configurar

1. Click en **Save Changes** en Render
2. Espera a que el servicio se redeploy automáticamente
3. Una vez completado, ve a tu dashboard
4. En Configuración → WhatsApp Twilio
5. Haz clic en "Probar" para enviar un mensaje de prueba

## Verificar que funciona

### Opción 1: Desde el Dashboard
1. Ve a Dashboard → Configuración
2. Sección "WhatsApp Twilio"
3. Ingresa tu número (formato: +573001234567)
4. Click en "Enviar Mensaje de Prueba"

### Opción 2: Crear una cita de prueba
1. Crea una cita para un paciente
2. Usa un número que esté unido a la sandbox de Twilio
3. El paciente recibirá notificación automática

## Troubleshooting

### Error: "Account SID debe comenzar con AC"
- Verifica que copiaste el Account SID completo
- No copies el Auth Token en el campo de Account SID

### Error: "Unable to create record: Authenticate"
- Verifica que el Auth Token sea correcto
- Asegúrate de que no haya espacios al inicio o final
- Genera un nuevo Auth Token si es necesario:
  1. Ve a Twilio Console
  2. Settings → API Keys
  3. Genera un nuevo Auth Token

### Error: "to number is not a valid phone number"
- El número debe estar en formato E.164: `+573001234567`
- Incluye el código de país (+57 para Colombia)
- Sin espacios ni guiones

### El mensaje no llega
1. Verifica que el número destinatario esté unido a la sandbox:
   - Envía `join <código>` al número de sandbox de Twilio
2. Verifica que el número esté en formato correcto
3. Revisa los logs en Twilio Console:
   - https://console.twilio.com/us1/monitor/logs/messages

## Pasar a producción (número real)

Para usar un número de WhatsApp real (no sandbox):

1. En Twilio Console, ve a: **Messaging → Try it out → Send a WhatsApp message**
2. Solicita acceso a WhatsApp Business API
3. Una vez aprobado, configura tu número de WhatsApp Business
4. Actualiza la variable en Render:
   ```bash
   TWILIO_WHATSAPP_FROM=whatsapp:+TuNumeroReal
   ```

## Costos de Twilio

- **Sandbox**: GRATIS (solo para pruebas con números registrados)
- **Mensajes WhatsApp**: ~$0.005 USD por mensaje en producción
- **Número de teléfono**: ~$1-2 USD/mes (si usas número dedicado)

## Enlaces útiles

- Twilio Console: https://console.twilio.com
- Twilio WhatsApp Sandbox: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn
- Documentación: https://www.twilio.com/docs/whatsapp
- Precios: https://www.twilio.com/whatsapp/pricing

## Resumen de configuración

```bash
# En Render Environment Variables
TWILIO_ACCOUNT_SID=AC1234567890abcdef1234567890abcd
TWILIO_AUTH_TOKEN=abcdef1234567890abcdef1234567890
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886

# Formato de números para enviar
# Colombia: +573001234567
# Sin espacios, con + y código de país
```
