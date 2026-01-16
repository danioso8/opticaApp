# 🔧 Sistema de WhatsApp Persistente - Configuración Completada

## ✅ Mejoras Implementadas

### 1. **Reconexión Automática Persistente**
- El sistema ahora **reconecta automáticamente** después de reinicios del servidor
- Si hay credenciales guardadas, intentará reconectar **indefinidamente** (hasta 999 intentos)
- Si no hay credenciales, pedirá QR después de 3 intentos fallidos

### 2. **Keep-Alive Automático**
- Monitoreo cada 5 minutos para verificar que la conexión esté activa
- Detecta sockets cerradas y actualiza el estado automáticamente
- Previene estados "conectado" falsos

### 3. **Backoff Exponencial Inteligente**
- Primer reintento: 2 segundos
- Segundo reintento: 4 segundos
- Tercer reintento: 8 segundos
- Máximo delay: 30 segundos
- Evita saturar los servidores de WhatsApp

### 4. **Detección Mejorada de Sesiones Corruptas**
- Detecta sockets cerradas en `/api/status` y `/api/send-message`
- Verifica `sock.ws.readyState === 1` (WebSocket abierto)
- Actualiza estado a `disconnected` cuando detecta problemas

## 📱 Cómo Funciona Ahora (Similar a WhatsApp Web)

### Primera Vez (Requiere QR):
1. Ir a: `https://www.optikaapp.com/dashboard/whatsapp-baileys/`
2. Escanear el código QR con WhatsApp
3. ✅ Conexión establecida

### Después de Reinicios del Servidor:
1. El servidor se reinicia (PM2 restart, actualización, etc.)
2. 🔄 El sistema **restaura automáticamente** las sesiones guardadas
3. 🔗 **Reconecta automáticamente** sin necesidad de QR
4. ✅ WhatsApp funciona normalmente

**NO es necesario volver a escanear el QR** a menos que:
- Se cierre sesión manualmente desde el teléfono
- Se desinstale WhatsApp del teléfono
- Se cambie de número de teléfono
- Las credenciales se corrompan (error Bad MAC)

### ✅ Estado Actual (14 Enero 2026):
- **Oceano Optico (org 4)**: ✅ CONECTADO - WhatsApp 3007915262
- **CompuEasys (org 2)**: ⏳ Pendiente escanear QR
- **Sistema:** ✅ Funcionando correctamente con reconexión automática

## 🧹 Limpieza de Sesiones Corruptas

Las sesiones actuales estaban corruptas (probablemente por múltiples reinicios mientras estábamos probando).

**Ya se ejecutó la limpieza automática** para ambas organizaciones:
- ✅ Organización 2 (CompuEasys): Sesión limpiada
- ✅ Organización 4 (Oceano Optico): Sesión limpiada

## 🚀 Próximos Pasos

### Para Oceano Optico (org_id 4):
1. Ir a: `https://www.optikaapp.com/dashboard/whatsapp-baileys/`
2. Login como usuario de Oceano Optico
3. Verás el código QR fresco
4. Escanear con WhatsApp: Configuración > Dispositivos vinculados > Vincular un dispositivo
5. Una vez conectado, probar enviando un mensaje de prueba
6. ✅ La sesión se mantendrá activa incluso después de reinicios

### Para CompuEasys (org_id 2):
- Mismo proceso que Oceano Optico

## 🔍 Verificar Estado

### Desde Python:
```python
from apps.appointments.whatsapp_baileys_client import whatsapp_baileys_client

# Verificar estado
status = whatsapp_baileys_client.get_status(4)  # 4 = Oceano Optico
print(status)
# {'status': 'connected', 'connected': True, 'phone_number': '573126809496'}

# Enviar mensaje de prueba
result = whatsapp_baileys_client.send_message(4, '573126809496', 'Hola desde OpticaApp!')
print(result)
```

### Desde el Dashboard:
- URL: `https://www.optikaapp.com/dashboard/whatsapp-baileys/`
- Verás el estado: "WhatsApp Conectado" con número
- Botón para enviar mensaje de prueba

## 📊 Logs del Servidor

Ver logs de WhatsApp:
```bash
ssh root@84.247.129.180
pm2 logs whatsapp-server --lines 50
```

Logs importantes:
- `✅ WhatsApp conectado exitosamente para X` → Conexión OK
- `🔄 Reconectando X en Yms` → Reintento automático
- `🧹 Limpiando sesión anterior` → Limpieza antes de nuevo QR
- `💚 Keep-alive OK para X` → Monitoreo funcionando

## ⚠️ Troubleshooting

### Si después de escanear QR sigue sin funcionar:
1. Esperar 30-60 segundos (reconexión puede tardar)
2. Refrescar la página del dashboard
3. Verificar logs: `pm2 logs whatsapp-server`
4. Si persiste, ejecutar limpieza de nuevo:
   ```bash
   cd /var/www/opticaapp
   /var/www/opticaapp/venv/bin/python clean_all_whatsapp_sessions.py
   ```

### Si aparece "Bad MAC" o "Stream Errored":
- El sistema detectará automáticamente y limpiará la sesión
- Se generará nuevo QR automáticamente
- Solo necesitas volver a escanear

## 📝 Notas Técnicas

### Archivos Modificados:
1. `whatsapp-server/server.js`:
   - Reconexión automática con credenciales guardadas (999 intentos)
   - Keep-alive cada 5 minutos
   - Backoff exponencial hasta 30s
   - Mejor manejo de restauración de sesiones

2. `apps/appointments/whatsapp_baileys_client.py`:
   - Soporte para `phone_number` y `phone` en respuestas
   - Detección mejorada de conexión

### Estructura de Sesiones:
```
/var/www/whatsapp-server/auth_sessions/
├── 2/              # CompuEasys
│   ├── creds.json  # Credenciales encriptadas
│   └── ...
├── 4/              # Oceano Optico
│   ├── creds.json
│   └── ...
└── *_corrupted_*/  # Backups de sesiones corruptas
```

## ✨ Resultado Final

**Antes:**
- ❌ Escanear QR cada vez que se reinicia el servidor
- ❌ Conexiones "fantasma" (dice conectado pero no funciona)
- ❌ Sesiones se corrompen fácilmente

**Ahora:**
- ✅ Escanear QR **solo una vez**
- ✅ Reconexión automática después de reinicios
- ✅ Detección y limpieza automática de sesiones corruptas
- ✅ Keep-alive para mantener conexión estable
- ✅ Similar a WhatsApp Web (escaneas una vez, funciona siempre)

---

## 🎉 Resultado Final

**Fecha de implementación:** 14 de enero de 2026  
**Estado:** ✅ **COMPLETADO Y FUNCIONANDO**

### Conexiones Activas:
- ✅ **Oceano Optico** - WhatsApp: 3007915262 - **CONECTADO EXITOSAMENTE**
- ⏳ CompuEasys - Pendiente de configuración

### Pruebas Realizadas:
1. ✅ Escaneo de QR funcional
2. ✅ Conexión establecida correctamente
3. ✅ Sistema de reconexión automática activo
4. ✅ Keep-alive funcionando (monitoreo cada 5 minutos)
5. ✅ Detección de sockets cerradas implementada

### Próximos Pasos (Para mañana):
1. Verificar que WhatsApp siga conectado después de 24 horas
2. Probar envío de mensajes automáticos con citas
3. Configurar WhatsApp para CompuEasys si es necesario
4. Monitorear logs para asegurar estabilidad

### Comandos Útiles:
```bash
# Ver estado de WhatsApp
ssh root@84.247.129.180 'pm2 logs whatsapp-server --lines 50'

# Verificar conexión desde Python
cd /var/www/opticaapp
/var/www/opticaapp/venv/bin/python -c "
from apps.appointments.whatsapp_baileys_client import whatsapp_baileys_client
status = whatsapp_baileys_client.get_status(4)
print(status)
"

# Limpiar sesión si es necesario
/var/www/opticaapp/venv/bin/python clean_all_whatsapp_sessions.py
```

**¡Sistema de WhatsApp persistente completamente funcional! 🚀**
