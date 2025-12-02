# 🚀 Guía Paso a Paso - Sistema SaaS Multi-Tenant

## 📝 Paso 1: Aplicar Migraciones

Primero, necesitamos crear las tablas en la base de datos:

```powershell
# Crear migraciones para la nueva app organizations
python manage.py makemigrations organizations

# Crear migraciones para los modelos modificados
python manage.py makemigrations patients
python manage.py makemigrations appointments
python manage.py makemigrations sales

# Aplicar todas las migraciones
python manage.py migrate
```

**Resultado esperado:** Las tablas de organizaciones, suscripciones y membresías se crearán en la base de datos.

---

## 📦 Paso 2: Configurar Planes de Suscripción

Crear los 4 planes predefinidos:

```powershell
python manage.py setup_plans
```

**Resultado esperado:** 
```
Configurando planes de suscripción...
✓ Creado: Plan Gratuito
✓ Creado: Plan Básico
✓ Creado: Plan Profesional
✓ Creado: Plan Empresarial
```

---

## 👤 Paso 3: Crear Superusuario (si no existe)

```powershell
python manage.py createsuperuser
```

Proporciona:
- Username
- Email
- Password

---

## 🏢 Paso 4: Crear tu Primera Organización

### Opción A: Desde el Admin de Django

```powershell
python manage.py runserver
```

1. Ir a `http://localhost:8000/admin/`
2. Login con superusuario
3. Ir a **Organizations** → **Organizations** → **Add Organization**
4. Completar:
   - Name: "Mi Óptica"
   - Slug: "mi-optica"
   - Email: "contacto@mioptica.com"
   - Owner: (seleccionar tu usuario)
5. Guardar

### Opción B: Desde la Interfaz Web

1. Ir a `http://localhost:8000/organizations/`
2. Click en "Nueva Organización"
3. Completar el formulario
4. Automáticamente se asignará plan gratuito

### Opción C: Desde el Shell de Django

```powershell
python manage.py shell
```

```python
from django.contrib.auth.models import User
from apps.organizations.models import Organization, Subscription, SubscriptionPlan

# Obtener tu usuario
user = User.objects.first()  # o User.objects.get(username='tu_usuario')

# Crear organización
org = Organization.objects.create(
    name="Mi Óptica",
    slug="mi-optica",
    email="contacto@mioptica.com",
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

print(f"✓ Organización '{org.name}' creada con plan {free_plan.name}")
```

---

## 🔄 Paso 5: Migrar Datos Existentes (IMPORTANTE)

Si ya tienes datos en la base de datos (pacientes, citas, ventas), necesitas asignarlos a una organización:

```powershell
python manage.py shell
```

```python
from apps.organizations.models import Organization
from apps.patients.models import Patient
from apps.appointments.models import Appointment, WorkingHours, AppointmentConfiguration
from apps.sales.models import Product, Category, Sale

# Obtener la organización
org = Organization.objects.first()  # o .get(slug='mi-optica')

# Asignar todos los pacientes existentes
Patient.objects.all().update(organization=org)

# Asignar todas las citas existentes
Appointment.objects.all().update(organization=org)

# Asignar configuración de citas
AppointmentConfiguration.objects.all().update(organization=org)

# Asignar horarios
WorkingHours.objects.all().update(organization=org)

# Asignar productos y categorías
Product.objects.all().update(organization=org)
Category.objects.all().update(organization=org)
Sale.objects.all().update(organization=org)

print("✓ Datos migrados exitosamente a la organización")
```

---

## 🎯 Paso 6: Probar el Sistema

### A. Acceder a la Organización

1. Ir a `http://localhost:8000/organizations/`
2. Ver tu lista de organizaciones
3. Click en "Acceder" para activar una organización

### B. Verificar el Contexto de Tenant

El middleware automáticamente establecerá `request.organization` en todas tus vistas.

### C. Crear Nuevos Registros

Ahora cuando crees pacientes, citas o ventas, estarán automáticamente vinculados a tu organización activa.

---

## 👥 Paso 7: Agregar Miembros a tu Organización

### Desde el Admin:

1. Ir a `http://localhost:8000/admin/organizations/organizationmember/`
2. Click en "Add Organization Member"
3. Seleccionar:
   - Organization: "Mi Óptica"
   - User: (usuario a agregar)
   - Role: (Owner/Admin/Staff/Viewer)
4. Guardar

### Desde el Shell:

```python
from django.contrib.auth.models import User
from apps.organizations.models import Organization, OrganizationMember

org = Organization.objects.get(slug='mi-optica')
nuevo_usuario = User.objects.get(username='empleado1')

miembro = OrganizationMember.objects.create(
    organization=org,
    user=nuevo_usuario,
    role='staff'
)

print(f"✓ {nuevo_usuario.username} agregado como {miembro.get_role_display()}")
```

---

## 🔄 Paso 8: Cambiar entre Organizaciones

Si un usuario pertenece a múltiples organizaciones:

1. Ir a `http://localhost:8000/organizations/`
2. Ver todas tus organizaciones
3. Click en "Acceder" en la organización deseada
4. El sistema cambiará el contexto automáticamente

---

## 💳 Paso 9: Gestionar Suscripciones

### Ver Planes Disponibles

```
http://localhost:8000/organizations/subscription/plans/
```

### Cambiar Plan (desde el shell por ahora)

```python
from apps.organizations.models import Organization, Subscription, SubscriptionPlan
from django.utils import timezone

org = Organization.objects.get(slug='mi-optica')

# Desactivar suscripción actual
Subscription.objects.filter(organization=org, is_active=True).update(is_active=False)

# Crear nueva suscripción con plan profesional
professional_plan = SubscriptionPlan.objects.get(slug='professional')
new_subscription = Subscription.objects.create(
    organization=org,
    plan=professional_plan,
    billing_cycle='monthly',
    payment_status='paid'
)

print(f"✓ Plan actualizado a {professional_plan.name}")
print(f"  - {professional_plan.max_users} usuarios")
print(f"  - {professional_plan.max_appointments_month} citas/mes")
```

---

## 🧪 Paso 10: Verificar el Aislamiento de Datos

### Crear Segunda Organización de Prueba

```python
from django.contrib.auth.models import User
from apps.organizations.models import Organization, Subscription, SubscriptionPlan

user = User.objects.first()

# Crear segunda organización
org2 = Organization.objects.create(
    name="Óptica Vision",
    slug="optica-vision",
    email="info@opticavision.com",
    owner=user
)

# Asignar plan
free_plan = SubscriptionPlan.objects.get(slug='free')
Subscription.objects.create(
    organization=org2,
    plan=free_plan,
    billing_cycle='monthly',
    payment_status='paid'
)
```

### Crear Datos en Diferentes Organizaciones

```python
from apps.patients.models import Patient

org1 = Organization.objects.get(slug='mi-optica')
org2 = Organization.objects.get(slug='optica-vision')

# Paciente para organización 1
paciente1 = Patient.objects.create(
    organization=org1,
    full_name="Juan Pérez",
    phone_number="3001234567"
)

# Paciente para organización 2
paciente2 = Patient.objects.create(
    organization=org2,
    full_name="María García",
    phone_number="3009876543"
)

# Verificar aislamiento
print(f"Org 1 tiene {Patient.objects.filter(organization=org1).count()} pacientes")
print(f"Org 2 tiene {Patient.objects.filter(organization=org2).count()} pacientes")
```

---

## 📊 Paso 11: Verificar Límites del Plan

```python
from apps.organizations.models import Organization

org = Organization.objects.get(slug='mi-optica')

# Ver límites actuales
limits = org.get_plan_limits()
print("Límites del plan:")
print(f"  - Usuarios: {limits['max_users']}")
print(f"  - Citas/mes: {limits['max_appointments_month']}")
print(f"  - Pacientes: {limits['max_patients']}")
print(f"  - Almacenamiento: {limits['max_storage_mb']} MB")

# Ver características
print("\nCaracterísticas:")
for feature, enabled in limits['features'].items():
    status = "✓" if enabled else "✗"
    print(f"  {status} {feature}")
```

---

## 🔧 Paso 12: Actualizar Vistas Existentes (IMPORTANTE)

Debes modificar tus vistas para filtrar por organización. Ejemplo:

### Antes:
```python
def patient_list(request):
    patients = Patient.objects.all()
    return render(request, 'patients/list.html', {'patients': patients})
```

### Después:
```python
def patient_list(request):
    patients = Patient.objects.filter(organization=request.organization)
    return render(request, 'patients/list.html', {'patients': patients})
```

### Al Crear:
```python
def patient_create(request):
    if request.method == 'POST':
        patient = Patient.objects.create(
            organization=request.organization,  # ← AGREGAR ESTO
            full_name=request.POST.get('full_name'),
            phone_number=request.POST.get('phone_number'),
            # ... otros campos
        )
        return redirect('patient_detail', pk=patient.pk)
```

---

## ⚠️ Consideraciones Importantes

### 1. **Middleware Order**
Los middlewares están en el orden correcto en settings.py:
```python
'django.contrib.auth.middleware.AuthenticationMiddleware',
'apps.organizations.middleware.TenantMiddleware',  # Después de auth
'apps.organizations.middleware.SubscriptionMiddleware',  # Después de tenant
```

### 2. **URLs Exentas**
Estas URLs no requieren suscripción activa:
- `/admin/`
- `/accounts/login/`
- `/accounts/logout/`
- `/organizations/`

### 3. **Suscripción Expirada**
Si una organización no tiene suscripción activa, será redirigida a:
```
/organizations/subscription/expired/
```

---

## 🎓 Casos de Uso Comunes

### Usuario con Múltiples Organizaciones
```
1. Usuario inicia sesión
2. Ve lista de sus organizaciones
3. Selecciona una organización
4. Trabaja con los datos de esa organización
5. Puede cambiar a otra organización en cualquier momento
```

### Nuevo Cliente (Óptica)
```
1. Registro de usuario
2. Crear organización
3. Se asigna plan gratuito automáticamente
4. Puede empezar a usar inmediatamente
5. Upgrade a plan superior cuando necesite
```

### Límite Alcanzado
```
1. Usuario intenta crear más pacientes
2. Sistema verifica límite del plan
3. Si excede, muestra mensaje
4. Redirige a página de planes
5. Usuario puede hacer upgrade
```

---

## 🐛 Solución de Problemas

### Error: "no such table: organizations_organization"
```powershell
python manage.py migrate
```

### Error: "request has no attribute organization"
- Verificar que los middlewares estén configurados
- Verificar que el usuario esté autenticado
- Verificar que el usuario tenga una organización

### Datos no aparecen
- Verificar que los datos tengan organization asignada
- Verificar que request.organization no sea None
- Ejecutar el paso 5 (migrar datos existentes)

---

## 📚 Recursos Adicionales

- **Documentación completa:** `SAAS_IMPLEMENTATION.md`
- **Tests:** `apps/organizations/tests.py`
- **Admin:** `http://localhost:8000/admin/organizations/`

---

## ✅ Checklist de Implementación

- [ ] Paso 1: Migraciones aplicadas
- [ ] Paso 2: Planes configurados
- [ ] Paso 3: Superusuario creado
- [ ] Paso 4: Primera organización creada
- [ ] Paso 5: Datos existentes migrados
- [ ] Paso 6: Sistema probado
- [ ] Paso 7: Miembros agregados (opcional)
- [ ] Paso 8: Cambio entre organizaciones probado
- [ ] Paso 9: Suscripciones verificadas
- [ ] Paso 10: Aislamiento de datos verificado
- [ ] Paso 11: Límites verificados
- [ ] Paso 12: Vistas actualizadas

---

## 🎉 ¡Listo!

Tu sistema SaaS multi-tenant está configurado y listo para usar. Cada organización (óptica) ahora puede:

✅ Tener sus propios datos aislados
✅ Gestionar sus propios usuarios y roles
✅ Elegir el plan que necesite
✅ Escalar según sus necesidades
✅ Mantener total independencia de otras organizaciones

**Siguiente paso recomendado:** Implementar sistema de pagos (Stripe/PayPal) para upgrades automáticos.
