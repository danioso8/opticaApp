# 🏥 Sistema de Gestión para Óptica

Sistema completo de gestión para óptica con Django, que incluye:
- ✅ Gestión de citas en tiempo real
- ✅ Gestión de pacientes
- ✅ API REST completa
- 🔄 Sistema de tiempo real (en desarrollo)
- 📊 Dashboard administrativo

## 🚀 Características Implementadas

### ✅ Módulo de Citas
- **API Pública (Landing Page):**
  - Ver fechas disponibles
  - Ver horarios disponibles por fecha
  - Agendar cita (solo nombre y teléfono)

- **API Administrativa:**
  - Gestionar todas las citas
  - Cambiar estados (pendiente, confirmada, completada, cancelada)
  - Ver citas del día
  - Estadísticas en tiempo real
  - Abrir/Cerrar sistema de agendamiento
  - Bloquear fechas específicas
  - Bloquear horarios específicos

### ✅ Configuración del Sistema
- Duración de citas configurable (default: 30 min)
- Máximo de citas diarias
- Días de anticipación para agendar
- Horarios de atención por día de la semana

## 🛠️ Tecnologías

- **Backend:** Django 3.2, Django REST Framework
- **Base de datos:** SQLite (desarrollo)
- **Python:** 3.7+

## 📦 Instalación

### 1. Clonar el repositorio
```bash
cd d:\ESCRITORIO\OpticaApp
```

### 2. Instalar dependencias
```bash
python -m pip install -r requirements.txt
```

### 3. Aplicar migraciones
```bash
python manage.py migrate
```

### 4. Inicializar datos
```bash
python scripts\init_data.py
```

## 🚀 Ejecutar el Proyecto

```bash
python manage.py runserver
```

El servidor estará disponible en: `http://127.0.0.1:8000/`

## 🔐 Credenciales de Acceso

**Panel Administrativo:** http://127.0.0.1:8000/admin/
- **Usuario:** `admin`
- **Contraseña:** `admin123`

## 📚 API Endpoints

### APIs Públicas (Landing Page)

#### Obtener fechas disponibles
```http
GET /api/available-dates/
GET /api/available-dates/?days=30
```

**Respuesta:**
```json
[
  {
    "date": "2025-11-30",
    "available_slots": 12,
    "total_slots": 18,
    "is_available": true
  }
]
```

#### Obtener horarios disponibles
```http
GET /api/available-slots/?date=2025-11-30
```

**Respuesta:**
```json
{
  "date": "2025-11-30",
  "slots": [
    {
      "time": "09:00:00",
      "available": true
    },
    {
      "time": "09:30:00",
      "available": false
    }
  ]
}
```

#### Agendar cita
```http
POST /api/book/
Content-Type: application/json

{
  "full_name": "Juan Pérez",
  "phone_number": "3001234567",
  "appointment_date": "2025-11-30",
  "appointment_time": "10:00:00"
}
```

**Respuesta exitosa:**
```json
{
  "success": true,
  "message": "¡Cita agendada exitosamente!",
  "appointment": {
    "id": 1,
    "full_name": "Juan Pérez",
    "date": "2025-11-30",
    "time": "10:00:00",
    "status": "pending"
  }
}
```

### APIs Administrativas (Requieren autenticación)

#### Listar todas las citas
```http
GET /api/appointments/
GET /api/appointments/?status=pending
GET /api/appointments/?date=2025-11-30
GET /api/appointments/?phone=3001234567
```

#### Citas del día
```http
GET /api/appointments/today/
```

#### Estadísticas
```http
GET /api/appointments/stats/
```

**Respuesta:**
```json
{
  "today": {
    "total": 15,
    "pending": 5,
    "confirmed": 8,
    "completed": 2,
    "cancelled": 0,
    "no_show": 0
  },
  "system_open": true
}
```

#### Cambiar estado de cita
```http
PATCH /api/appointments/{id}/change_status/
Content-Type: application/json

{
  "status": "confirmed"
}
```

Valores válidos: `pending`, `confirmed`, `completed`, `cancelled`, `no_show`

#### Abrir/Cerrar sistema
```http
POST /api/toggle-system/
```

#### Bloquear fecha
```http
POST /api/block-date/
Content-Type: application/json

{
  "date": "2025-12-25",
  "reason": "Navidad"
}
```

#### Bloquear horario específico
```http
POST /api/block-slot/
Content-Type: application/json

{
  "date": "2025-11-30",
  "time": "14:00:00",
  "reason": "Reunión interna"
}
```

## 📊 Modelos de Datos

### Appointment (Cita)
- `full_name`: Nombre completo (requerido)
- `phone_number`: Número de celular (requerido)
- `appointment_date`: Fecha de la cita
- `appointment_time`: Hora de la cita
- `status`: Estado (pending, confirmed, completed, cancelled, no_show)
- `notes`: Notas adicionales
- `patient`: Relación con paciente (opcional)
- `attended_by`: Usuario que atendió

### AppointmentConfiguration
- `is_open`: Sistema abierto/cerrado
- `slot_duration`: Duración de cita (minutos)
- `max_daily_appointments`: Máximo de citas diarias
- `advance_booking_days`: Días de anticipación

### WorkingHours
- `day_of_week`: Día de la semana (0-6)
- `start_time`: Hora de inicio
- `end_time`: Hora de fin
- `is_active`: Activo/inactivo

### BlockedDate
- `date`: Fecha bloqueada
- `reason`: Motivo del bloqueo

### Patient
- `full_name`: Nombre completo
- `identification`: Identificación
- `date_of_birth`: Fecha de nacimiento
- `gender`: Género
- `phone_number`: Teléfono
- `email`: Email
- `address`: Dirección
- `allergies`: Alergias
- `medical_conditions`: Condiciones médicas
- `current_medications`: Medicamentos actuales

## 🎯 Próximas Funcionalidades

- [ ] Django Channels para actualizaciones en tiempo real
- [ ] WebSockets para dashboard en vivo
- [ ] Frontend con React/Next.js
- [ ] Notificaciones SMS/WhatsApp
- [ ] Módulo de historia clínica
- [ ] Módulo de exámenes visuales
- [ ] Módulo de inventario
- [ ] Módulo de ventas y facturación
- [ ] Reportes y estadísticas avanzadas

## 📝 Horarios de Atención Predeterminados

- **Lunes a Viernes:** 9:00 AM - 6:00 PM
- **Sábado:** 9:00 AM - 2:00 PM
- **Domingo:** Cerrado

*Los horarios se pueden modificar desde el panel administrativo*

## 🔧 Configuración Avanzada

### Cambiar zona horaria
Editar `config/settings.py`:
```python
TIME_ZONE = 'America/Bogota'  # Cambiar según tu ubicación
```

### Cambiar duración de citas
Opción 1: Desde el admin en `/admin/appointments/appointmentconfiguration/`

Opción 2: Editar `.env`:
```
APPOINTMENT_SLOT_DURATION=45
```

## 📱 Estructura del Proyecto

```
OpticaApp/
├── config/                 # Configuración Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── appointments/       # Módulo de citas
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   └── utils.py
│   ├── patients/          # Módulo de pacientes
│   └── users/             # Módulo de usuarios
├── scripts/
│   └── init_data.py       # Script de inicialización
├── manage.py
├── requirements.txt
├── .env
└── README.md
```

## 🐛 Solución de Problemas

### Error al crear cita: "Horario ya ocupado"
Verifica que no exista otra cita en el mismo horario y fecha.

### No aparecen fechas disponibles
1. Verifica que el sistema esté abierto en `/admin/`
2. Revisa los horarios de trabajo configurados
3. Verifica que no estén todas las fechas bloqueadas

### Error de importación
Asegúrate de que todas las apps tengan el prefijo `apps.` en `name` en sus `apps.py`

## 📞 Soporte

Para más información o reportar bugs, contacta al equipo de desarrollo.

---
**Desarrollado con ❤️ para Gestión de Ópticas**
