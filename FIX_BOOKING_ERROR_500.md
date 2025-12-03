# Corrección: Error 500 al Agendar Cita desde Landing Page

## Problema Identificado

Al intentar crear una cita desde la landing page (booking.html), se generaba un error 500:
```
POST https://oceano-optico-v2.onrender.com/api/book/ 500 (Internal Server Error)
```

## Causas del Error

1. **Validación sin filtrar por organización**: El `AppointmentCreateSerializer` validaba citas, fechas bloqueadas y horarios sin considerar la organización específica, causando conflictos en sistemas multi-tenant.

2. **Configuración sin organización**: El método `get_config()` podía retornar `None` si no había configuraciones, sin crear una por defecto.

3. **Notificaciones no manejadas**: Las notificaciones (WhatsApp/Email) podían causar excepciones que detenían todo el proceso de agendamiento.

## Cambios Realizados

### 1. `apps/appointments/serializers.py` - AppointmentCreateSerializer

**Método `validate()`:**
- ✅ Agregado manejo de `organization_id` desde `initial_data`
- ✅ Validación de existencia y estado activo de la organización
- ✅ Filtrado de configuración por organización
- ✅ Creación automática de configuración si no existe
- ✅ Filtrado de fechas bloqueadas por organización
- ✅ Filtrado de citas existentes por organización
- ✅ Filtrado de horarios específicos por organización
- ✅ Filtrado de horarios de trabajo por organización

**Método `create()`:**
- ✅ Movido el manejo de notificaciones a la vista
- ✅ Agregado logging para debugging
- ✅ Mejorado manejo de excepciones al buscar pacientes

### 2. `apps/appointments/views.py` - book_appointment

- ✅ Agregado try-catch global para capturar errores 500
- ✅ Las notificaciones ahora se manejan en la vista con try-catch
- ✅ Si falla una notificación, no falla el agendamiento
- ✅ Agregado logging detallado de errores
- ✅ Respuesta de error más informativa

## Flujo Corregido

```
1. Usuario completa formulario en landing page (booking.html)
   - Selecciona organización (sucursal)
   - Selecciona fecha
   - Selecciona hora
   - Ingresa nombre y teléfono

2. POST /api/book/ con datos:
   {
     "full_name": "Juan Pérez",
     "phone_number": "+573001234567",
     "email": "email@example.com",  // opcional
     "appointment_date": "2025-12-04",
     "appointment_time": "10:00:00",
     "organization_id": 1
   }

3. AppointmentCreateSerializer.validate():
   ✓ Obtiene y valida organización
   ✓ Verifica fecha no sea pasada
   ✓ Obtiene/crea configuración para esa organización
   ✓ Verifica sistema abierto
   ✓ Verifica días de anticipación
   ✓ Verifica fecha no bloqueada (filtrado por org)
   ✓ Verifica horario no ocupado (filtrado por org)
   ✓ Verifica horario dentro de rango de atención

4. AppointmentCreateSerializer.create():
   ✓ Asigna organización a la cita
   ✓ Busca paciente existente (filtrado por org)
   ✓ Crea el appointment
   ✓ Retorna appointment (sin enviar notificaciones aquí)

5. book_appointment view:
   ✓ Cita creada exitosamente
   ✓ Intenta enviar notificaciones (no falla si hay error)
   ✓ Retorna respuesta exitosa al cliente

6. Cliente recibe confirmación
   ✓ Muestra mensaje de éxito
   ✓ Usuario puede agendar otra cita o volver al inicio
```

## Testing

Para probar el endpoint corregido:

```bash
# 1. Activar entorno virtual
& D:/ESCRITORIO/OpticaApp/.venv/Scripts/Activate.ps1

# 2. Ejecutar script de prueba
python test_book_appointment.py

# 3. O probar con curl/PowerShell
$body = @{
    full_name = "Test Usuario"
    phone_number = "+573001234567"
    email = "test@example.com"
    appointment_date = "2025-12-05"
    appointment_time = "10:00:00"
    organization_id = 1
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/book/" `
    -Method POST `
    -Body $body `
    -ContentType "application/json"
```

## Prevención de Errores Futuros

1. **Siempre filtrar por organización** en sistemas multi-tenant
2. **Manejar notificaciones de forma asíncrona** o con try-catch
3. **Logging detallado** para debugging en producción
4. **Validar datos de entrada** antes de operaciones críticas
5. **Crear configuraciones por defecto** cuando sea necesario

## Archivos Modificados

- ✅ `apps/appointments/serializers.py`
- ✅ `apps/appointments/views.py`
- ✅ `test_book_appointment.py` (nuevo)
