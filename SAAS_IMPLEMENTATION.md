# Sistema Multi-Tenant SaaS - OpticaApp

## 📋 Descripción

Se ha implementado un sistema completo de multi-tenancy (SaaS) para OpticaApp, permitiendo que múltiples organizaciones (ópticas) puedan usar el sistema de forma independiente con sus propios datos y configuraciones.

## 🎯 Características Implementadas

### 1. **Modelo de Organizaciones**
- Cada organización (óptica) tiene sus propios datos aislados
- Sistema de membresía con roles: Owner, Admin, Staff, Viewer
- Configuración personalizada por organización (logo, colores, etc.)
- Slug único para identificación

### 2. **Sistema de Suscripciones**
- 4 planes predefinidos: Gratuito, Básico, Profesional, Empresarial
- Límites configurables por plan:
  - Número de usuarios
  - Citas mensuales
  - Pacientes
  - Almacenamiento
- Características premium:
  - Integración WhatsApp
  - Marca personalizada
  - Acceso API
  - Soporte prioritario
  - Análisis avanzado
  - Múltiples ubicaciones
- Ciclos de facturación: mensual y anual
- Sistema de renovación automática

### 3. **Middleware de Multi-Tenant**
- `TenantMiddleware`: Identifica la organización actual basándose en:
  - Subdominio
  - Sesión del usuario
  - Membresía del usuario
- `SubscriptionMiddleware`: Valida que la organización tenga suscripción activa
- URLs protegidas automáticamente

### 4. **Modelos Multi-Tenant**
Todos los modelos principales ahora son multi-tenant:
- ✅ Patients (Pacientes)
- ✅ Appointments (Citas)
- ✅ WorkingHours (Horarios)
- ✅ Products (Productos)
- ✅ Sales (Ventas)
- ✅ Categories (Categorías)

Cada modelo incluye:
- Campo `organization` (ForeignKey)
- Índices optimizados por organización
- Restricciones de unicidad por organización

### 5. **Vistas y Templates**
- Lista de organizaciones del usuario
- Crear nueva organización
- Detalle de organización con información de suscripción
- Cambio entre organizaciones
- Configuración de organización
- Visualización de planes disponibles
- Página de suscripción expirada

## 📁 Estructura de Archivos

```
apps/organizations/
├── __init__.py
├── admin.py                    # Administración Django
├── apps.py                     # Configuración de la app
├── base_models.py             # Modelo base TenantModel
├── middleware.py              # Middlewares de tenant y suscripción
├── models.py                  # Modelos principales
├── signals.py                 # Señales para membresía automática
├── urls.py                    # URLs de la app
├── views.py                   # Vistas
├── management/
│   └── commands/
│       └── setup_plans.py     # Comando para crear planes
└── templates/
    └── organizations/
        ├── list.html
        ├── create.html
        ├── detail.html
        ├── settings.html
        ├── plans.html
        └── subscription_expired.html
```

## 🚀 Instalación y Configuración

### 1. Generar Migraciones

```bash
python manage.py makemigrations organizations
python manage.py makemigrations patients
python manage.py makemigrations appointments
python manage.py makemigrations sales
```

### 2. Aplicar Migraciones

```bash
python manage.py migrate
```

### 3. Configurar Planes de Suscripción

Opción A - Usando el comando de management:
```bash
python manage.py setup_plans
```

Opción B - Usando el script:
```bash
python setup_subscription_plans.py
```

### 4. Crear una Organización de Prueba

```python
from django.contrib.auth.models import User
from apps.organizations.models import Organization, Subscription, SubscriptionPlan

# Obtener usuario
user = User.objects.first()

# Crear organización
org = Organization.objects.create(
    name="Óptica Vision",
    slug="optica-vision",
    email="info@opticavision.com",
    phone="300 123 4567",
    owner=user
)

# Asignar plan gratuito
free_plan = SubscriptionPlan.objects.get(slug='free')
subscription = Subscription.objects.create(
    organization=org,
    plan=free_plan,
    billing_cycle='monthly',
    payment_status='paid'
)
```

## 📊 Planes de Suscripción

### Plan Gratuito ($0/mes)
- 1 usuario
- 50 citas/mes
- 100 pacientes
- 100 MB almacenamiento

### Plan Básico ($29.99/mes)
- 3 usuarios
- 200 citas/mes
- 500 pacientes
- 500 MB almacenamiento
- ✓ Integración WhatsApp
- ✓ Análisis básico

### Plan Profesional ($79.99/mes)
- 10 usuarios
- 1000 citas/mes
- 2000 pacientes
- 2 GB almacenamiento
- ✓ Integración WhatsApp
- ✓ Marca personalizada
- ✓ Acceso API
- ✓ Soporte prioritario
- ✓ Análisis avanzado
- ✓ Múltiples ubicaciones

### Plan Empresarial ($149.99/mes)
- Usuarios ilimitados
- Citas ilimitadas
- 10,000 pacientes
- 10 GB almacenamiento
- ✓ Todas las características premium

## 🔐 Sistema de Permisos

### Roles de Organización

1. **Owner (Propietario)**
   - Acceso completo
   - Puede gestionar configuración
   - Puede agregar/remover miembros
   - Puede cambiar plan de suscripción

2. **Admin (Administrador)**
   - Puede gestionar configuración
   - Puede agregar/remover miembros
   - Acceso a todas las funcionalidades

3. **Staff (Personal)**
   - Acceso a funcionalidades operativas
   - Crear/editar citas, pacientes, ventas
   - No puede modificar configuración

4. **Viewer (Visualizador)**
   - Solo lectura
   - Ver información sin modificar

## 🔄 Flujo de Trabajo

### Para un Usuario Nuevo

1. Usuario se registra en el sistema
2. Usuario crea su primera organización
3. Se asigna automáticamente como Owner
4. Se crea suscripción gratuita por defecto
5. Usuario puede empezar a usar el sistema

### Cambio entre Organizaciones

1. Usuario accede a "Mis Organizaciones"
2. Selecciona la organización deseada
3. Sistema actualiza el contexto (request.organization)
4. Todos los datos filtrados por organización actual

### Verificación de Límites

```python
# En las vistas
if request.organization:
    limits = request.organization.get_plan_limits()
    
    # Verificar límite de pacientes
    current_patients = Patient.objects.filter(
        organization=request.organization
    ).count()
    
    if current_patients >= limits['max_patients']:
        messages.error(request, 'Has alcanzado el límite de pacientes')
        return redirect('subscription_plans')
```

## 🛠️ Uso en Vistas

### Filtrar por Organización

```python
from django.contrib.auth.decorators import login_required

@login_required
def patient_list(request):
    # request.organization es automáticamente establecido por TenantMiddleware
    patients = Patient.objects.filter(
        organization=request.organization
    )
    
    return render(request, 'patients/list.html', {
        'patients': patients
    })
```

### Crear Registros con Organización

```python
@login_required
def patient_create(request):
    if request.method == 'POST':
        patient = Patient.objects.create(
            organization=request.organization,
            full_name=request.POST.get('full_name'),
            phone_number=request.POST.get('phone_number'),
            # ... otros campos
        )
        return redirect('patient_detail', pk=patient.pk)
```

## 📝 Tareas Pendientes

- [ ] Implementar QuerySet managers personalizados para filtrado automático
- [ ] Agregar sistema de pagos (Stripe/PayPal)
- [ ] Implementar facturación automática
- [ ] Crear dashboard de métricas por organización
- [ ] Agregar límites de API rate limiting por plan
- [ ] Implementar notificaciones de vencimiento de suscripción
- [ ] Crear sistema de invitaciones para miembros
- [ ] Agregar soporte para subdominios personalizados
- [ ] Implementar backup automático por organización
- [ ] Crear API REST para gestión de organizaciones

## 🔧 Configuración Adicional

### Variables de Entorno

Agregar a `.env`:
```
# Multi-tenant settings
DEFAULT_PLAN_SLUG=free
TRIAL_DAYS=14
```

### Subdominios (Opcional)

Para usar subdominios (ej: `optica1.tudominio.com`):

1. Configurar DNS wildcard
2. Actualizar `ALLOWED_HOSTS` en settings:
```python
ALLOWED_HOSTS = ['.tudominio.com', 'tudominio.com']
```

## 📚 Recursos Adicionales

- [Django Multi-Tenant Best Practices](https://docs.djangoproject.com/)
- [SaaS Application Patterns](https://example.com)

## 🤝 Contribución

Para contribuir a esta implementación:

1. Crear un branch feature
2. Implementar cambios
3. Escribir tests
4. Crear PR con descripción detallada

## 📄 Licencia

Este módulo es parte de OpticaApp y sigue la misma licencia del proyecto principal.
