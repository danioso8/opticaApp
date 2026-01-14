# 🔍 REFERENCIA RÁPIDA DE ERRORES - OpticaApp

## 📋 Índice de Módulos y Archivos Críticos

### Sistema de Códigos de Referencia

Para facilitar la comunicación sobre errores, usa estos códigos:

| Código | Módulo | Archivo Principal | Descripción |
|--------|--------|------------------|-------------|
| **APT** | Citas/Appointments | `apps/appointments/` | Sistema de agendamiento |
| **APT-V** | Citas Vista | `apps/dashboard/templates/dashboard/appointments/` | Templates de citas |
| **PAT** | Pacientes | `apps/patients/` | Gestión de pacientes |
| **PAT-V** | Pacientes Vista | `apps/dashboard/templates/dashboard/patients/` | Templates de pacientes |
| **EXM** | Exámenes | `apps/patients/templates/exams/` | Exámenes visuales |
| **NOT** | Notificaciones | `apps/notifications/` | Sistema de notificaciones |
| **NOT-V** | Notif. Vista | `apps/dashboard/templates/dashboard/notifications/` | Config. notificaciones |
| **CFG** | Configuración | `apps/dashboard/views_configuration.py` | Configuración general |
| **WF** | Workflows | `apps/dashboard/views_workflows.py` | Flujos de trabajo |
| **API** | API General | `apps/appointments/views.py` | Endpoints API |
| **WA** | WhatsApp | `apps/notifications/views_whatsapp_baileys.py` | WhatsApp Baileys |
| **ADM** | Admin SAAS | `apps/admin_dashboard/` | Panel de administración |
| **AUD** | Auditoría | `apps/audit/` | Logs y errores |

---

## 🎯 Mapeo de Errores Comunes a Módulos

### Errores de JavaScript (Frontend)

#### 1. "Swal is not defined"
- **Código:** `APT-V` o `PAT-V`
- **Archivo:** Template donde ocurre el error
- **Solución típica:** Agregar `<script src="https://cdn.jsdelivr.net/npm/sweetalert2@11"></script>`

#### 2. "Cannot read properties of null (reading 'checked')"
- **Código:** `NOT-V`
- **Archivo:** `apps/dashboard/templates/dashboard/notifications/settings.html`
- **Solución típica:** Validar existencia del elemento antes de acceder

#### 3. "saveFormDataToLocalStorage is not defined"
- **Código:** `EXM`
- **Archivo:** `apps/dashboard/templates/dashboard/patients/visual_exam_form.html`
- **Solución típica:** Definir la función o eliminar la llamada

### Errores de Backend (Python/Django)

#### 4. "HTTP 404: Not Found - /api/appointments/X/resend-notification/"
- **Código:** `API`
- **Archivo:** `apps/appointments/urls.py` + `views.py`
- **Solución típica:** Verificar ruta en urls.py

#### 5. "HTTP 500: Internal Server Error - /api/book-patient/"
- **Código:** `API`
- **Archivo:** `apps/appointments/views.py` → función `book_appointment_api`
- **Solución típica:** Revisar logs del servidor, validar datos

#### 6. "IntegrityError: null value in column organization_id"
- **Código:** Depende del modelo
- **Solución típica:** Agregar validación de organización en el middleware

#### 7. "HTTP 404: /toggle-system/"
- **Código:** `CFG`
- **Archivo:** `apps/dashboard/urls.py` + `views_configuration.py`
- **Solución típica:** Agregar ruta faltante

---

## 🚀 Comandos Rápidos para Diagnóstico

### Ver errores del monitor
```bash
ssh root@84.247.129.180 "cd /var/www/opticaapp && source venv/bin/activate && python manage.py shell < check_errors_monitor.py"
```

### Marcar errores como resueltos
```bash
# Editar mark_errors_resolved.py con los IDs
# error_ids = [35, 36, 37]
ssh root@84.247.129.180 "cd /var/www/opticaapp && source venv/bin/activate && python manage.py shell < mark_errors_resolved.py"
```

### Ver logs en tiempo real
```bash
ssh root@84.247.129.180 "pm2 logs opticaapp --lines 50"
```

---

## 📝 Plantilla de Reporte de Error

**Formato sugerido para pedir correcciones:**

```
Código: [APT-V]
Error ID: #35
Descripción: Swal is not defined en detalle de cita
Solución: Agregar SweetAlert2
Estado: ✅ Resuelto
```

O simplemente:
```
APT-V #35 - Swal is not defined → RESUELTO
```

---

## 🔧 Errores Actuales (Última actualización: 14/01/2026)

### ✅ Resueltos
- [x] **APT-V #35** - Swal is not defined (14/01/2026)

### 🔴 Pendientes (Prioridad Alta)

#### NOT-V #33, #32, #30, #23 - Cannot read 'checked'
- **Archivo:** `apps/dashboard/templates/dashboard/notifications/settings.html`
- **Líneas:** 1443, 1447, 1455, 1496
- **Acción:** Validar existencia de checkboxes antes de acceder

#### EXM #26, #25 - saveFormDataToLocalStorage is not defined
- **Archivo:** `apps/dashboard/templates/dashboard/patients/visual_exam_form.html`
- **Líneas:** 2962, 2997
- **Acción:** Definir función o remover llamadas

#### CFG #24 - HTTP 404: /toggle-system/
- **Archivo:** `apps/dashboard/urls.py` + `views_configuration.py`
- **Acción:** Agregar ruta faltante

#### API #19, #18 - HTTP 500 en book-patient y configuration
- **Archivos:** `apps/appointments/views.py`
- **Acción:** Revisar stack trace y validar datos

#### EXM #28, #27, #16, #13 - Cannot read 'data'
- **Archivo:** `apps/dashboard/templates/dashboard/patients/visual_exam_form.html`
- **Líneas:** 2999, 4169, 4042, 4017
- **Acción:** Validar objeto antes de acceder a .data

---

## 💡 Uso del Sistema

### Para el usuario:
**Reportar un error:**
```
"Soluciona NOT-V #33"
"Arregla los errores EXM de saveFormDataToLocalStorage"
"Revisa API #19 y #18"
```

### Para el asistente:
1. Identificar el código del módulo
2. Ir directamente al archivo correcto
3. Aplicar la solución
4. Marcar error como resuelto
5. Actualizar este documento

---

## 🗂️ Estructura de Directorios Rápida

```
OpticaApp/
├── apps/
│   ├── appointments/           # APT - Sistema de citas
│   │   ├── views.py           # API de citas
│   │   ├── urls.py            # Rutas de citas
│   │   └── models.py          # Modelos de citas
│   ├── patients/              # PAT - Gestión de pacientes
│   ├── notifications/         # NOT - Notificaciones
│   │   ├── views_whatsapp_baileys.py  # WA
│   │   └── models_whatsapp_connection.py
│   ├── dashboard/             # Dashboard general
│   │   ├── templates/dashboard/
│   │   │   ├── appointments/  # APT-V
│   │   │   ├── patients/      # PAT-V
│   │   │   └── notifications/ # NOT-V
│   │   ├── views_configuration.py  # CFG
│   │   └── views_workflows.py      # WF
│   ├── admin_dashboard/       # ADM - Admin SAAS
│   └── audit/                 # AUD - Logs y errores
└── whatsapp-server/          # Servidor Node.js WhatsApp
```

---

## 🎯 Scripts de Utilidad

### check_errors_monitor.py
Analiza todos los errores del sistema con estadísticas completas.

### mark_errors_resolved.py
Marca errores específicos como resueltos. Editar `error_ids = [...]`

### sync_whatsapp_connections.py
Sincroniza sesiones de WhatsApp entre servidor Node.js y Django.

### fix_whatsapp_session.py
Limpia sesiones corruptas de WhatsApp.

---

**Última actualización:** 14 de Enero de 2026  
**Mantenido por:** Sistema Auto-Corrector OpticaApp
