# 🧪 Pruebas de API - Sistema de Óptica

## URLs Base
- **Servidor Local:** http://127.0.0.1:8000
- **Admin:** http://127.0.0.1:8000/admin/

## Credenciales Admin
- **Usuario:** admin
- **Contraseña:** admin123

---

## 📋 APIs Públicas (Sin autenticación)

### 1. Ver fechas disponibles
```bash
# PowerShell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/available-dates/" -Method GET

# cURL
curl http://127.0.0.1:8000/api/available-dates/
```

### 2. Ver horarios disponibles de una fecha
```bash
# PowerShell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/available-slots/?date=2025-11-30" -Method GET

# cURL
curl "http://127.0.0.1:8000/api/available-slots/?date=2025-11-30"
```

### 3. Agendar una cita
```bash
# PowerShell
$body = @{
    full_name = "Juan Pérez"
    phone_number = "3001234567"
    appointment_date = "2025-11-30"
    appointment_time = "10:00:00"
} | ConvertTo-Json

Invoke-RestMethod -Uri "http://127.0.0.1:8000/api/book/" -Method POST -Body $body -ContentType "application/json"

# cURL
curl -X POST http://127.0.0.1:8000/api/book/ \
  -H "Content-Type: application/json" \
  -d '{
    "full_name": "Juan Pérez",
    "phone_number": "3001234567",
    "appointment_date": "2025-11-30",
    "appointment_time": "10:00:00"
  }'
```

---

## 🔐 APIs Administrativas (Requieren sesión)

### Primero, inicia sesión en el admin
Ve a: http://127.0.0.1:8000/admin/ y inicia sesión

### 1. Ver todas las citas
```bash
# Desde el navegador (ya con sesión iniciada)
http://127.0.0.1:8000/api/appointments/

# Filtros disponibles:
http://127.0.0.1:8000/api/appointments/?status=pending
http://127.0.0.1:8000/api/appointments/?date=2025-11-30
http://127.0.0.1:8000/api/appointments/?phone=3001234567
```

### 2. Ver citas del día
```bash
http://127.0.0.1:8000/api/appointments/today/
```

### 3. Ver estadísticas
```bash
http://127.0.0.1:8000/api/appointments/stats/
```

### 4. Ver configuración del sistema
```bash
http://127.0.0.1:8000/api/configuration/
```

---

## 🧪 Flujo de Prueba Completo

### Escenario: Usuario agenda una cita desde la landing page

1. **Ver fechas disponibles**
   ```bash
   GET http://127.0.0.1:8000/api/available-dates/
   ```

2. **Seleccionar una fecha y ver horarios**
   ```bash
   GET http://127.0.0.1:8000/api/available-slots/?date=2025-11-30
   ```

3. **Agendar la cita**
   ```bash
   POST http://127.0.0.1:8000/api/book/
   Body:
   {
     "full_name": "María García",
     "phone_number": "3009876543",
     "appointment_date": "2025-11-30",
     "appointment_time": "11:00:00"
   }
   ```

4. **Admin verifica la nueva cita**
   - Ir a: http://127.0.0.1:8000/admin/appointments/appointment/
   - O: http://127.0.0.1:8000/api/appointments/today/

5. **Admin confirma la cita**
   - Desde el admin Django, cambiar estado a "Confirmada"

---

## 📊 Panel Administrativo

### Acceso al Admin Django
http://127.0.0.1:8000/admin/

### Secciones Disponibles

1. **Citas** (`/admin/appointments/appointment/`)
   - Ver todas las citas
   - Filtrar por estado, fecha
   - Cambiar estado (pendiente → confirmada → completada)
   - Agregar notas

2. **Configuración de Citas** (`/admin/appointments/appointmentconfiguration/`)
   - Abrir/Cerrar sistema
   - Cambiar duración de citas
   - Configurar máximo de citas diarias

3. **Horarios de Atención** (`/admin/appointments/workinghours/`)
   - Configurar horarios por día
   - Activar/desactivar días

4. **Fechas Bloqueadas** (`/admin/appointments/blockeddate/`)
   - Bloquear festivos, vacaciones

5. **Pacientes** (`/admin/patients/patient/`)
   - Ver todos los pacientes registrados
   - Editar información

---

## 🎯 Casos de Prueba

### ✅ Caso 1: Agendar cita exitosamente
```json
POST /api/book/
{
  "full_name": "Carlos Ruiz",
  "phone_number": "3001111111",
  "appointment_date": "2025-12-01",
  "appointment_time": "09:00:00"
}
```
**Resultado esperado:** Status 201, cita creada

### ❌ Caso 2: Intentar agendar en horario ocupado
```json
POST /api/book/
{
  "full_name": "Ana López",
  "phone_number": "3002222222",
  "appointment_date": "2025-12-01",
  "appointment_time": "09:00:00"
}
```
**Resultado esperado:** Error 400, "Este horario ya está ocupado"

### ❌ Caso 3: Fecha en el pasado
```json
POST /api/book/
{
  "full_name": "Pedro Gómez",
  "phone_number": "3003333333",
  "appointment_date": "2025-11-01",
  "appointment_time": "10:00:00"
}
```
**Resultado esperado:** Error 400, "No se pueden agendar citas en fechas pasadas"

### ❌ Caso 4: Horario fuera de atención
```json
POST /api/book/
{
  "full_name": "Laura Díaz",
  "phone_number": "3004444444",
  "appointment_date": "2025-12-01",
  "appointment_time": "20:00:00"
}
```
**Resultado esperado:** Error 400, "Fuera del horario de atención"

### ❌ Caso 5: Domingo (sin atención)
```json
POST /api/book/
{
  "full_name": "José Martínez",
  "phone_number": "3005555555",
  "appointment_date": "2025-11-30",
  "appointment_time": "10:00:00"
}
```
**Resultado esperado:** Error 400, "No hay atención disponible en este día"

---

## 🔄 Pruebas de Configuración

### 1. Cerrar el sistema de agendamiento
```bash
POST http://127.0.0.1:8000/api/toggle-system/
```

### 2. Intentar agendar con sistema cerrado
```bash
POST http://127.0.0.1:8000/api/book/
```
**Resultado esperado:** Error 400, "Sistema cerrado temporalmente"

### 3. Abrir el sistema nuevamente
```bash
POST http://127.0.0.1:8000/api/toggle-system/
```

### 4. Bloquear una fecha
```bash
POST http://127.0.0.1:8000/api/block-date/
Body:
{
  "date": "2025-12-25",
  "reason": "Navidad"
}
```

---

## 📈 Monitoreo en Tiempo Real

Una vez implementado Django Channels, el dashboard mostrará:
- ✅ Nuevas citas llegando en vivo
- ✅ Cambios de estado instantáneos
- ✅ Notificaciones visuales
- ✅ Contador de citas en tiempo real

---

## 🛠️ Herramientas Recomendadas

### Para probar APIs:
- **Postman:** https://www.postman.com/
- **Insomnia:** https://insomnia.rest/
- **Thunder Client** (extensión VS Code)
- **REST Client** (extensión VS Code)

### Navegador:
- Accede directamente a las URLs GET desde el navegador
- Django REST Framework proporciona una interfaz web interactiva

---

## 📝 Notas Importantes

1. **Formato de teléfono:** 
   - Acepta: `3001234567` o `+573001234567`
   - Longitud: 9-15 dígitos

2. **Formato de fecha:** `YYYY-MM-DD` (ej: 2025-12-01)

3. **Formato de hora:** `HH:MM:SS` (ej: 14:30:00)

4. **Estados de cita:**
   - `pending`: Pendiente
   - `confirmed`: Confirmada
   - `completed`: Completada
   - `cancelled`: Cancelada
   - `no_show`: No asistió

---

¡Sistema listo para pruebas! 🎉
