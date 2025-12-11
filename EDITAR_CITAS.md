# ✏️ Editar y Reagendar Citas

## 📋 Descripción

Se ha implementado la funcionalidad para **editar y reagendar citas** de los pacientes. Esta característica permite cambiar la fecha y hora de las citas cuando los pacientes no pueden asistir al horario originalmente agendado.

## 🎯 Características Implementadas

### 1. **Vista de Detalle de Cita**
- Botón "Reagendar Cita" en la sección de gestión
- Modal con formulario para cambiar fecha y hora
- Validación de conflictos de horario
- Notificación automática al paciente

### 2. **Vista de Detalle de Paciente**
- Botón "Editar" en cada cita listada
- Edición rápida desde el historial del paciente
- Solo disponible para citas pendientes o confirmadas

### 3. **Sistema de Notificaciones**
- Notificación automática al paciente cuando se reagenda
- Muestra la fecha/hora anterior y la nueva
- Compatible con WhatsApp y Email según configuración

## 📍 Ubicación de las Funcionalidades

### Archivos Modificados:

1. **`apps/dashboard/views.py`**
   - Nueva función: `appointment_edit(request, pk)`
   - Maneja la lógica de reagendamiento
   - Valida disponibilidad y conflictos

2. **`apps/dashboard/urls.py`**
   - Nueva URL: `/dashboard/appointments/<id>/edit/`
   - Ruta para editar citas

3. **`apps/dashboard/templates/dashboard/appointments/detail.html`**
   - Botón "Reagendar Cita"
   - Modal de edición con formulario
   - JavaScript para manejo del modal

4. **`apps/dashboard/templates/dashboard/patients/detail.html`**
   - Botón "Editar" en cada cita
   - Modal de edición rápida
   - JavaScript para edición desde historial

5. **`apps/appointments/notifications.py`**
   - Nueva función: `notify_appointment_rescheduled()`
   - Envía notificación al paciente sobre el cambio

## 🚀 Cómo Usar

### Desde Detalle de Cita:

1. Ir a **Dashboard → Citas**
2. Hacer clic en una cita para ver detalles
3. En la sección "Gestión de Cita", hacer clic en **"Reagendar Cita"**
4. En el modal:
   - Seleccionar nueva fecha
   - Seleccionar nueva hora
   - Agregar notas si es necesario (opcional)
5. Hacer clic en **"Guardar Cambios"**
6. Confirmar el cambio en el diálogo
7. El paciente recibirá una notificación automáticamente

### Desde Historial del Paciente:

1. Ir a **Dashboard → Pacientes**
2. Hacer clic en un paciente para ver detalles
3. En la pestaña "Citas", localizar la cita
4. Hacer clic en el botón **"Editar"**
5. En el modal, cambiar fecha/hora
6. Hacer clic en **"Guardar"**

## ⚠️ Validaciones Implementadas

### Validaciones del Sistema:

- ✅ **Fecha requerida**: No se puede dejar vacía
- ✅ **Hora requerida**: No se puede dejar vacía
- ✅ **Formato correcto**: Fecha YYYY-MM-DD, Hora HH:MM
- ✅ **Sin conflictos**: No permite reagendar si existe otra cita confirmada en ese horario
- ✅ **Solo citas activas**: Solo se pueden editar citas pendientes o confirmadas
- ✅ **Notificación automática**: El paciente es notificado del cambio

### Restricciones:

- ❌ No se pueden editar citas **completadas**
- ❌ No se pueden editar citas **canceladas**
- ❌ No se puede reagendar a un horario ya ocupado

## 📧 Sistema de Notificaciones

Cuando se reagenda una cita, el paciente recibe automáticamente una notificación que incluye:

### Contenido del Mensaje:

```
📅 CITA REAGENDADA

Hola [Nombre del Paciente],

Su cita ha sido REAGENDADA:

❌ Cita Anterior:
   📆 DD/MM/YYYY
   🕒 HH:MM

✅ Nueva Cita:
   📆 DD/MM/YYYY
   🕒 HH:MM

Por favor, confirme su asistencia en el nuevo horario.
```

### Canales de Notificación:

- **WhatsApp**: Si está configurado (local o Twilio)
- **Email**: Si el paciente tiene email registrado
- **Automático**: Según la configuración de la organización

## 🔧 Configuración Técnica

### Endpoint API:

```
POST /dashboard/appointments/<id>/edit/
```

### Parámetros:

| Campo | Tipo | Requerido | Descripción |
|-------|------|-----------|-------------|
| `appointment_date` | date | Sí | Nueva fecha (YYYY-MM-DD) |
| `appointment_time` | time | Sí | Nueva hora (HH:MM) |
| `notes` | text | No | Notas adicionales |

### Respuesta Exitosa:

```json
{
  "success": true,
  "message": "Cita reagendada para DD/MM/YYYY a las HH:MM"
}
```

### Respuesta de Error:

```json
{
  "success": false,
  "message": "Ya existe una cita confirmada en esa fecha y hora"
}
```

## 🎨 Interfaz de Usuario

### Botón de Reagendar:
- **Color**: Naranja (indica acción de modificación)
- **Icono**: 📝 (fas fa-edit)
- **Ubicación**: Sección "Gestión de Cita"

### Modal de Edición:
- **Diseño**: Ventana modal centrada
- **Header**: Fondo degradado naranja
- **Campos**: Fecha, hora y notas opcionales
- **Botones**: Cancelar (gris) y Guardar (naranja)

### Mensajes de Confirmación:
- **Toast Success**: Verde con mensaje de éxito
- **Toast Error**: Rojo con mensaje de error
- **Diálogo de Confirmación**: Antes de guardar cambios

## 📊 Beneficios

✅ **Flexibilidad**: Los pacientes pueden cambiar sus citas fácilmente
✅ **Eficiencia**: Menos llamadas telefónicas para reagendar
✅ **Comunicación**: Notificación automática al paciente
✅ **Control**: Validación de horarios disponibles
✅ **Historial**: Se mantiene registro de cambios
✅ **Usabilidad**: Interfaz intuitiva y fácil de usar

## 🐛 Solución de Problemas

### Problema: "Ya existe una cita confirmada en esa fecha y hora"
**Solución**: Elegir otro horario disponible o cancelar la cita conflictiva primero.

### Problema: No se envía la notificación
**Solución**: 
- Verificar configuración de WhatsApp/Email en Configuración → Notificaciones
- Verificar que el paciente tenga teléfono o email registrado
- Revisar logs del sistema para errores

### Problema: No aparece el botón "Reagendar"
**Solución**: 
- El botón solo aparece en citas pendientes o confirmadas
- Verificar el estado de la cita
- Las citas completadas o canceladas no se pueden editar

## 📝 Notas Importantes

1. **Historial Preservado**: Aunque se cambie la fecha, la hora de creación original se mantiene
2. **Sin Deshacer Automático**: Los cambios son permanentes, usar con cuidado
3. **Notificaciones Opcionales**: Se intenta enviar pero no bloquea si falla
4. **Zona Horaria**: Usar la zona horaria local configurada en el sistema

## 🔜 Mejoras Futuras Sugeridas

- [ ] Historial de cambios (audit trail)
- [ ] Límite de reagendamientos por cita
- [ ] Sugerencias de horarios disponibles
- [ ] Calendario visual para selección
- [ ] Confirmación del paciente requerida
- [ ] Recordatorio automático después de reagendar

---

**Última actualización**: Diciembre 2025  
**Versión**: 1.0.0
