# Sistema de Gestión de Sesiones WhatsApp

## Fecha: 10 de Enero 2026

## Problema Resuelto

Las sesiones de WhatsApp pueden corromperse por varios motivos:
- **Stream Errored (conflict)**: Cuando se escanea el mismo QR en múltiples dispositivos
- **Connection Failure**: Cuando la sesión expira o hay problemas de red
- **Bad MAC Error**: Errores de cifrado en sesiones antiguas

### Síntomas
- No se genera código QR al intentar conectar
- Estado "Connection Closed" con Status 401
- Usuario no puede reconectar WhatsApp

## Solución Implementada

### 1. Endpoint de Limpieza de Sesión

**Vista**: `apps/dashboard/views_whatsapp_baileys.py`
```python
@login_required
def whatsapp_clear_session(request):
    """Limpiar sesión corrupta de WhatsApp"""
    # Cierra sesión existente
    # Llama al servidor para eliminar archivos de autenticación
    # Permite generar nuevo QR
```

**Cliente**: `apps/appointments/whatsapp_baileys_client.py`
```python
def clear_session(self, organization_id):
    """Limpiar sesión corrupta de WhatsApp"""
    return self._make_request('POST', '/api/clear-session', data)
```

### 2. Interfaz de Usuario

**Ubicación**: `/dashboard/whatsapp-baileys/`

**Nuevo Botón**: "🧹 Limpiar Sesión Corrupta"
- Aparece cuando NO está conectado
- Color amarillo/ambar para indicar acción de mantenimiento
- Confirmación antes de ejecutar
- Feedback visual de éxito

### 3. Flujo de Uso

```
1. Usuario detecta que no se genera QR
   ↓
2. Click en "Limpiar Sesión Corrupta"
   ↓
3. Confirmar acción
   ↓
4. Sistema elimina sesión corrupta del servidor
   ↓
5. Recarga página automáticamente
   ↓
6. Click en "Conectar WhatsApp" genera QR nuevo
   ↓
7. Escanear QR y listo
```

## Archivos Modificados

### Backend
- `apps/dashboard/views_whatsapp_baileys.py` → Agregado `whatsapp_clear_session()`
- `apps/appointments/whatsapp_baileys_client.py` → Agregado `clear_session()`
- `apps/dashboard/urls.py` → Ruta `whatsapp-baileys/clear/`

### Frontend
- `apps/dashboard/templates/dashboard/whatsapp_baileys_config.html`
  - Botón "Limpiar Sesión Corrupta"
  - Función JavaScript `clearSession()`
  - Confirmación y notificaciones

## Comandos de Emergencia

### Limpiar Sesión Manualmente (SSH)
```bash
# Conectar al servidor
ssh root@84.247.129.180

# Eliminar sesión específica (ejemplo: org 2)
rm -rf /var/www/whatsapp-server/auth_sessions/2

# Reiniciar servidor WhatsApp
pm2 restart whatsapp-server
```

### Verificar Estado de Sesiones
```bash
# Ver sesiones existentes
ls -la /var/www/whatsapp-server/auth_sessions/

# Ver logs del servidor
pm2 logs whatsapp-server --lines 50
```

## Prevención de Errores

### Buenas Prácticas
1. ✅ Usar solo UN dispositivo por número WhatsApp
2. ✅ No escanear el mismo QR múltiples veces
3. ✅ Si aparece "conflict", usar botón de limpiar sesión
4. ✅ Mantener WhatsApp actualizado en el móvil

### Monitoreo
- Revisar logs regularmente: `pm2 logs whatsapp-server`
- Verificar espacio en disco: `df -h`
- Estado de sesiones: `/dashboard/whatsapp-baileys/`

## Endpoints API

### POST `/dashboard/whatsapp-baileys/clear/`
**Descripción**: Limpia sesión corrupta de WhatsApp

**Headers**:
```
X-CSRFToken: <csrf_token>
```

**Respuesta Exitosa**:
```json
{
  "success": true,
  "message": "Sesión limpiada correctamente"
}
```

**Respuesta Error**:
```json
{
  "error": "No se pudo limpiar la sesión"
}
```

## Próximas Mejoras (Pendientes)

### Servidor WhatsApp Baileys
- [ ] Implementar endpoint `/api/clear-session`
- [ ] Detección automática de sesiones corruptas
- [ ] Limpieza automática de sesiones antiguas (>30 días sin uso)
- [ ] Logs estructurados por organización
- [ ] Health check de sesiones individuales

### Monitoreo
- [ ] Dashboard de estado de sesiones
- [ ] Alertas por email cuando sesión se desconecta
- [ ] Métricas de uso (mensajes enviados, fallos, etc.)
- [ ] Auto-reconexión inteligente

## Notas Técnicas

### Estructura de Sesiones
```
/var/www/whatsapp-server/auth_sessions/
├── 2/           # Organización ID 2 (CompuEasys)
│   ├── creds.json
│   ├── app-state-sync-key-*.json
│   └── pre-key-*.json
├── 4/           # Organización ID 4 (OCÉANO ÓPTICO)
│   └── ...
```

### Logs a Monitorear
- ❌ `Stream Errored (conflict)` → Necesita limpiar sesión
- ❌ `Connection Failure` → Verificar red/sesión
- ❌ `Bad MAC Error` → Sesión corrupta, limpiar
- ✅ `WhatsApp conectado exitosamente` → Todo bien

## Historial de Cambios

**10 Ene 2026**
- Implementado sistema de limpieza de sesiones
- Agregado botón en interfaz
- Documentación creada

## Soporte

Si el problema persiste después de limpiar sesión:
1. Verificar que el servidor WhatsApp esté activo: `pm2 status`
2. Revisar logs: `pm2 logs whatsapp-server`
3. Verificar conectividad de red
4. Contactar administrador del sistema
