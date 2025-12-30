# OpticaApp - Sistema Completo de Gestión Óptica SaaS

## 👤 Información del Proyecto

**Desarrollador Principal**: Daniel (danioso8)  
**Usuario de Prueba**: danioso8  
**Tipo**: Sistema SaaS Multi-Tenant para Ópticas en Colombia  
**Base de Datos**: PostgreSQL (Producción en Render.com) / SQLite (Desarrollo)  
**Framework**: Django 3.2+ con Django REST Framework  

---

## 📋 Resumen del Sistema

OpticaApp es un **sistema SaaS multi-tenant** completo para la gestión de ópticas que incluye:

### Módulos Principales
1. **Gestión de Pacientes** - Registro completo, historia clínica digital
2. **Citas** - Sistema de agendamiento con calendario, horarios bloqueados
3. **Doctores/Optómetras** - Gestión de profesionales
4. **Historia Clínica** - Registro digital con firma, PDF
5. **Exámenes Visuales** - Registro de optometrías con PDF
6. **Exámenes Especiales** - Órdenes de exámenes (paquimetría, topografía, etc.)
7. **Inventario** - Productos, proveedores, stock
8. **Facturación Electrónica DIAN** - Integración directa con DIAN Colombia
9. **WhatsApp** - Notificaciones automáticas con Twilio
10. **Landing Page** - Página personalizable por organización
11. **Gestión de Equipo** - Roles y permisos granulares
12. **Analytics** - Reportes y estadísticas

---

## 💳 Sistema de Suscripciones y Planes

### Planes Disponibles

| Plan | Precio | Módulos | Características |
|------|--------|---------|-----------------|
| **FREE** | $12 USD/mes (después de 3 meses gratis) | 7 módulos básicos | Dashboard, Pacientes, Citas, Doctores, Landing, Facturación Básica, Historia Clínica |
| **BÁSICO** | $25 USD/mes | 10 módulos | FREE + Inventario (Productos, Proveedores) |
| **PROFESIONAL** | $50 USD/mes | 15 módulos | BÁSICO + Facturación DIAN, WhatsApp, Pagos Wompi |
| **PREMIUM** | $100 USD/mes | 19 módulos | PROFESIONAL + Analytics, Reportes, Gestión de Equipo, Multi-ubicación |
| **EMPRESARIAL** | $200 USD/mes | 20 módulos | PREMIUM + Acceso API |

### Trial System
- **3 meses gratis** para nuevos usuarios (90 días)
- Activación automática al registrarse
- Después del trial: cobro automático de $12 USD/mes para Plan Free
- Usuario: danioso8 tiene **85 días de trial restantes**

### Renovación Automática
✅ **Sistema completo implementado** (como Netflix/Spotify):
- Cobro automático 3 días antes del vencimiento
- Email recordatorio 7 días antes
- Toggle ON/OFF en panel de usuario
- Gestión de métodos de pago (tarjetas tokenizadas con Wompi)
- Historial de renovaciones
- **Panel**: `/users/subscription/manage/`

**Comandos cron necesarios**:
```bash
# Diario a las 2 AM - Renovar suscripciones
python manage.py renew_subscriptions --days-before 3

# Diario a las 9 AM - Enviar recordatorios
python manage.py send_renewal_reminders --days-before 7
```

### Control de Acceso por Módulos
✅ **Sistema de restricciones implementado**:
- 20 módulos definidos con íconos y descripciones
- Decoradores para proteger vistas: `@require_module('whatsapp')`
- Template tags para UI: `{% has_module 'products' %}`
- Badges visuales de "Upgrade" en sidebar
- Redirección automática a página de planes si no tiene acceso

---

## 🔐 Autenticación y Seguridad

### Verificación de Email
- Sistema de tokens únicos (UUID) con expiración 24 horas
- Email automático al registrarse
- Reenvío de verificación disponible
- Bloqueo de acceso hasta verificar email

### Recuperación de Contraseña
- Sistema nativo de Django con tokens seguros
- Emails HTML personalizados
- Expiración de links (3 días)

### Permisos y Roles
**4 tipos de usuarios por organización**:
1. **Owner** - Control total
2. **Admin** - Casi todo excepto eliminar organización
3. **Doctor** - Acceso a pacientes, citas, historias clínicas
4. **Recepcionist** - Solo citas y pacientes (lectura)

---

## 💰 Integraciones de Pago

### Wompi (Colombia)
- **Producción**: Claves con prefijo `prod_`
- **Sandbox**: Claves con prefijo `test_` o `pub_test_`
- **Funcionalidades**:
  - Tokenización de tarjetas (NO guarda datos sensibles)
  - Pagos recurrentes para suscripciones
  - Webhooks para confirmación
  - Conversión automática USD → COP (1 USD = 4000 COP)

**Variables de entorno necesarias**:
```
WOMPI_PUBLIC_KEY=pub_prod_xxxxx
WOMPI_PRIVATE_KEY=prv_prod_xxxxx
WOMPI_EVENTS_SECRET=xxxxx
WOMPI_INTEGRITY_SECRET=xxxxx
WOMPI_TEST_MODE=False
```

---

## 📱 Notificaciones WhatsApp

### Twilio WhatsApp
- **Número sandbox**: `whatsapp:+14155238886`
- **Configuración por organización**
- **Plantillas personalizables** para:
  - Confirmación de citas
  - Recordatorios (1 día antes)
  - Cancelaciones
  - Cambios de horario

**Variables de entorno**:
```
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

**Configuración**: `/dashboard/notification-settings/`

---

## 📄 Facturación Electrónica DIAN

### Integración Directa
- **Sin APIs externas** - Sistema propio
- Genera XML según resolución DIAN
- Firma digital con certificado
- QR code en facturas
- Cufe/Cude generado

**Configuración necesaria por organización**:
- NIT, nombre, dirección
- Resolución DIAN (número, prefijo, rango)
- Certificado digital (.p12)
- Contraseña del certificado

**Acceso**: Solo planes **Profesional o superior**

---

## 🏥 Sistema Clínico

### Historia Clínica
- Registro completo: antecedentes, medicamentos, alergias
- Motivo de consulta, diagnóstico
- Firma del paciente (canvas HTML5)
- **PDF automático** con logo de la organización
- Búsqueda y filtros avanzados

### Exámenes Visuales
- Refracción (OD/OI)
- Agudeza visual
- Queratometría
- Refracción final con adición
- **PDF con membrete**

### Exámenes Especiales
- Órdenes de laboratorio externo
- 10 tipos: Paquimetría, Topografía, OCT, etc.
- Estados: Pendiente, Realizado, Entregado
- Adjuntar resultados PDF

---

## 🗓️ Sistema de Citas

### Funcionalidades
- Calendario visual (FullCalendar)
- Configuración de horarios por día
- Bloqueador de fechas/rangos
- Duración personalizable (15-60 min)
- Notificaciones WhatsApp automáticas
- Sistema abierto/cerrado por organización
- **Landing page pública** para agendar sin login

### Estados de Citas
- Programada (azul)
- Confirmada (verde)
- En Proceso (naranja)
- Completada (verde oscuro)
- Cancelada (rojo)

---

## 📊 Multi-Tenancy (SaaS)

### Arquitectura
- **1 Base de Datos** compartida
- Campo `organization_id` en cada tabla
- Middleware automático: `TenantMiddleware`
- Aislamiento de datos por organización
- Sin subdominios - URLs con selección manual

### Cambio de Organización
Usuario puede pertenecer a múltiples organizaciones y cambiar entre ellas desde el menú.

---

## 🌐 Deployment en Render.com

### Servicios Configurados
1. **Web Service**: Django app (Gunicorn)
2. **PostgreSQL**: Base de datos principal
3. **Disk**: 1GB persistente para media files
4. **Redis**: Cache (opcional)

### Variables de Entorno Críticas
```bash
DJANGO_SETTINGS_MODULE=config.settings
SECRET_KEY=xxxxx
DEBUG=False
ALLOWED_HOSTS=opticaapp.onrender.com
DATABASE_URL=postgresql://... (auto)
RENDER_DISK_PATH=/var/data
WOMPI_PUBLIC_KEY=xxxxx
TWILIO_ACCOUNT_SID=xxxxx
EMAIL_HOST_USER=xxxxx
DEFAULT_FROM_EMAIL=noreply@opticaapp.com
```

### Build Command
```bash
pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate
```

### Start Command
```bash
gunicorn config.wsgi:application
```

---

## 🧪 Testing y Comandos Útiles

### Comandos de Gestión

```bash
# Verificar trial de usuarios
python manage.py check_trial_expiration --days 90

# Verificar sistema de módulos
python verify_module_access.py

# Renovación de suscripciones (modo prueba)
python manage.py renew_subscriptions --dry-run

# Enviar recordatorios (modo prueba)
python manage.py send_renewal_reminders --dry-run

# Crear parámetros clínicos globales
python manage.py create_clinical_parameters

# Activar trial para usuarios existentes
python activate_trial_existing_users.py

# Actualizar precio de plan Free
python update_free_plan_price.py
```

### Usuarios de Prueba

**Usuario Principal**: danioso8  
- Email: danisobarzo@gmail.com
- Es superusuario (acceso completo)
- Plan: Free con 85 días de trial restante
- Organización: Oceano Optico

---

## 📁 Estructura del Proyecto

```
OpticaApp/
├── apps/
│   ├── users/          # Autenticación, suscripciones, pagos
│   ├── organizations/  # Multi-tenant, planes, middleware
│   ├── dashboard/      # Vista principal, home
│   ├── patients/       # Gestión de pacientes
│   ├── appointments/   # Sistema de citas
│   ├── billing/        # Facturación DIAN, inventario
│   └── sales/          # Ventas (no usado actualmente)
├── config/             # Settings, URLs principales
├── static/             # CSS, JS, imágenes
├── media/              # Archivos subidos (logos, PDFs)
├── templates/          # Templates base
└── manage.py
```

---

## 🔧 Configuración Local

### Requisitos
- Python 3.8+
- PostgreSQL (o SQLite para desarrollo)
- Virtual environment

### Setup Inicial
```bash
# Crear entorno virtual
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Ejecutar servidor
python manage.py runserver
```

### Variables de Entorno (.env)
```
DEBUG=True
SECRET_KEY=tu-clave-secreta-aqui
DATABASE_URL=sqlite:///db.sqlite3
WOMPI_TEST_MODE=True
WOMPI_PUBLIC_KEY=pub_test_xxxxx
```

---

## 🎯 Funcionalidades Destacadas

### Landing Page Personalizable
- `/landing/<slug>/` - Página pública por organización
- Personalización: Logo, colores, descripción, horarios
- Formulario de contacto
- Sistema de citas públicas
- WhatsApp directo

### Sistema Abierto/Cerrado
- Toggle por organización para activar/desactivar citas online
- Cuando está cerrado: Landing muestra solo info, no permite agendar
- Útil para vacaciones o mantenimiento

### Historial Completo
- Todas las acciones registradas con fecha/hora/usuario
- Auditoría completa de cambios
- Soft delete (eliminación lógica)

### PDFs Automáticos
- Historia clínica con firma
- Exámenes visuales
- Facturas DIAN con QR
- Logo de organización en todos

---

## 📈 Métricas y Analytics

### Dashboard Principal
- Total pacientes
- Citas del mes
- Ingresos del mes
- Gráficas de tendencias

### Reportes (Plan Premium)
- Pacientes por período
- Citas por doctor
- Ingresos por servicio
- Productos más vendidos

---

## 🚀 Estado Actual del Proyecto

### ✅ Completado al 100%
- Sistema de autenticación y permisos
- Multi-tenancy completo
- Gestión de pacientes y citas
- Historia clínica digital
- Facturación electrónica DIAN
- Inventario y productos
- WhatsApp notificaciones
- Landing pages
- Sistema de planes y suscripciones
- Trial de 3 meses
- Renovación automática
- Control de acceso por módulos
- Tokenización de tarjetas
- Emails HTML personalizados

### ⚠️ Pendiente de Configuración
- [ ] Cron jobs en Render para renovaciones automáticas
- [ ] Testing con usuarios reales
- [ ] Certificado SSL personalizado (opcional)
- [ ] Domain propio (opcional)

---

## 🆘 Solución de Problemas Comunes

### Error: "No organization found"
**Solución**: Usuario debe pertenecer a una organización. Crear desde `/admin/` o hacer que se registre desde landing.

### Error: "Trial expired"
**Solución**: Usuario debe pagar. Ir a `/users/subscription/trial-expired/`

### Error: "Module not accessible"
**Solución**: Plan del usuario no incluye ese módulo. Debe upgradearse.

### Error: "Payment failed"
**Solución**: Verificar credenciales Wompi, tarjeta válida, fondos suficientes.

### Error: "WhatsApp not sending"
**Solución**: Verificar credenciales Twilio, número de teléfono en formato +57XXXXXXXXXX

### Error: "DIAN validation error"
**Solución**: Verificar configuración DIAN completa, certificado válido, resolución activa.

---

## 📞 Contacto y Soporte

**Desarrollador**: Daniel (danioso8)  
**Email**: danisobarzo@gmail.com  
**Organización Demo**: Oceano Optico

---

## 📝 Notas Importantes

1. **Conversión de moneda**: 1 USD = 4000 COP (fijo en el sistema)
2. **Trial**: Auto-activado para nuevos usuarios, 90 días
3. **Superuser**: danioso8 tiene acceso completo sin restricciones
4. **Método de pago**: Tokenizado, NO se guardan datos de tarjeta
5. **Backup**: Configurar backups automáticos en Render
6. **Logs**: Revisar `/admin/users/subscriptionrenewallog/` para renovaciones

---

**Última actualización**: 30 de diciembre de 2024  
**Versión del sistema**: 2.0  
**Estado**: ✅ Producción - Completamente funcional
