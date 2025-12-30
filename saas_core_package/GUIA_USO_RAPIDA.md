# 🚀 Guía Rápida de Uso - SaaS Core Package

**Autor**: Daniel (danioso8)

---

## ✅ Lo que acabas de crear

Has generado **2 proyectos SaaS completos** en segundos:

### 📁 InmobiliariaApp
- **Industria**: Real Estate (Bienes Raíces)
- **Módulos**: 19 (Propiedades, Asesores, CRM, Tours Virtuales, etc.)
- **Planes**: $15-$250 USD/mes
- **Ubicación**: `D:\ESCRITORIO\InmobiliariaApp`

### 📁 CompraVentaApp
- **Industria**: Retail (Compraventa)
- **Módulos**: 20 (POS, Productos, Inventario, E-commerce, etc.)
- **Planes**: $10-$220 USD/mes
- **Ubicación**: `D:\ESCRITORIO\CompraVentaApp`

---

## 🎯 Qué incluyen automáticamente

### ✅ Ya configurado y listo para usar:
- Sistema de autenticación completo
- Suscripciones con 5 planes
- Trial de 90 días automático
- Renovación automática (como Netflix)
- Integración Wompi (pagos)
- WhatsApp notificaciones
- Facturación DIAN
- Multi-tenancy (múltiples organizaciones)
- Emails automáticos
- Landing pages

### 📄 Archivos generados:
- `apps/users/models.py` - Suscripciones, pagos, usuarios
- `apps/organizations/plan_features.py` - **TUS módulos personalizados**
- `apps/organizations/decorators.py` - Control de acceso
- `requirements.txt` - Dependencias
- `.env.example` - Variables de entorno
- `README.md` - Documentación personalizada

---

## 🚀 Próximos Pasos para InmobiliariaApp

### 1. Entrar al proyecto
```bash
cd D:\ESCRITORIO\InmobiliariaApp
```

### 2. Crear entorno virtual
```bash
python -m venv .venv
.venv\Scripts\activate
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
# Copiar el template
cp .env.example .env

# Editar .env y agregar:
# - SECRET_KEY (genera una nueva)
# - Credenciales Wompi (de OpticaApp)
# - Credenciales Twilio (de OpticaApp)
# - Email settings (de OpticaApp)
```

### 5. Crear modelos específicos de inmobiliaria

Ahora SÍ debes crear los modelos específicos de tu negocio:

**Crear** `apps/properties/models.py`:
```python
from django.db import models
from apps.organizations.models import Organization

class Property(models.Model):
    """Modelo de Propiedad"""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    title = models.CharField(max_length=200)
    property_type = models.CharField(max_length=50)  # Casa, Apartamento, Lote
    transaction_type = models.CharField(max_length=20)  # Venta, Arriendo
    price = models.DecimalField(max_digits=12, decimal_places=2)
    area = models.DecimalField(max_digits=10, decimal_places=2)
    bedrooms = models.IntegerField()
    bathrooms = models.IntegerField()
    address = models.CharField(max_length=300)
    description = models.TextField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']

class PropertyImage(models.Model):
    """Fotos de la propiedad"""
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/')
    is_main = models.BooleanField(default=False)
```

**Crear** `apps/clients/models.py`:
```python
class Client(models.Model):
    """Cliente potencial o comprador"""
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    budget_min = models.DecimalField(max_digits=12, decimal_places=2)
    budget_max = models.DecimalField(max_digits=12, decimal_places=2)
    interested_in = models.CharField(max_length=50)  # Venta/Arriendo
    preferred_zones = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
```

### 6. Migraciones
```bash
python manage.py makemigrations
python manage.py migrate
```

### 7. Crear planes en la base de datos

**Crear** `create_plans.py`:
```python
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from apps.organizations.models import SubscriptionPlan

plans = [
    {"code": "free", "name": "Gratis", "price": 15, "max_users": 2},
    {"code": "basic", "name": "Básico", "price": 35, "max_users": 5},
    {"code": "professional", "name": "Profesional", "price": 70, "max_users": 10},
    {"code": "premium", "name": "Premium", "price": 120, "max_users": 25},
    {"code": "enterprise", "name": "Empresarial", "price": 250, "max_users": 100},
]

for plan_data in plans:
    plan, created = SubscriptionPlan.objects.get_or_create(
        code=plan_data['code'],
        defaults=plan_data
    )
    if created:
        print(f"✅ Creado plan: {plan.name}")
    else:
        print(f"ℹ️  Ya existe: {plan.name}")
```

```bash
python create_plans.py
```

### 8. Crear superusuario
```bash
python manage.py createsuperuser
```

### 9. Ejecutar servidor
```bash
python manage.py runserver
```

### 10. Acceder
```
http://localhost:8000/admin
```

---

## 🛠️ Lo que debes personalizar

### Apps específicas de tu negocio

#### Para InmobiliariaApp:
- [ ] `apps/properties/` - Gestión de propiedades
- [ ] `apps/clients/` - Gestión de clientes
- [ ] `apps/agents/` - Gestión de asesores
- [ ] `apps/viewings/` - Visitas (appointments ya está copiado)

#### Para CompraVentaApp:
- [ ] `apps/products/` - Catálogo de productos
- [ ] `apps/sales/` - Ventas
- [ ] `apps/purchases/` - Compras
- [ ] `apps/inventory/` - Control de inventario
- [ ] `apps/pos/` - Punto de venta

### Templates personalizados
- [ ] Dashboard específico de tu industria
- [ ] Formularios personalizados
- [ ] Landing page con tus colores/logo

---

## 🔧 Ejemplo: Crear vista protegida

```python
# apps/properties/views.py
from django.shortcuts import render
from apps.organizations.decorators import require_module

@require_module('properties')
def property_list(request):
    """Solo usuarios con módulo 'properties' pueden acceder"""
    properties = Property.objects.filter(
        organization=request.organization
    )
    return render(request, 'properties/list.html', {
        'properties': properties
    })

@require_module('crm')
def leads_dashboard(request):
    """Solo plan Professional o superior"""
    # Tu lógica aquí
    pass
```

---

## 📊 Resumen de diferencias

| Aspecto | OpticaApp | InmobiliariaApp | CompraVentaApp |
|---------|-----------|-----------------|----------------|
| **Core copiado** | Original | ✅ 100% | ✅ 100% |
| **Wompi** | ✅ | ✅ | ✅ |
| **WhatsApp** | ✅ | ✅ | ✅ |
| **DIAN** | ✅ | ✅ | ✅ |
| **Suscripciones** | ✅ | ✅ | ✅ |
| **Módulos** | 20 (healthcare) | 19 (real estate) | 20 (retail) |
| **Models específicos** | Pacientes, Doctores | **TÚ los creas** | **TÚ los creas** |

---

## 🎯 Ventaja Principal

**Sin el paquete**: 
- 2-3 semanas configurando pagos, emails, suscripciones
- Copiar código manualmente
- Adaptar cada archivo

**Con el paquete**:
- ✅ 30 segundos ejecutando el script
- ✅ Todo el core ya funciona
- ✅ Solo creas tus modelos de negocio

---

## 📝 Checklist de implementación

### InmobiliariaApp
- [x] Estructura creada
- [x] Core copiado (users, organizations, billing)
- [x] plan_features.py generado con 19 módulos
- [x] requirements.txt generado
- [x] .env.example generado
- [ ] Crear app `properties`
- [ ] Crear app `clients`
- [ ] Crear app `agents`
- [ ] Personalizar templates
- [ ] Configurar .env con credenciales reales
- [ ] Deploy en Render

### CompraVentaApp
- [x] Estructura creada
- [x] Core copiado
- [x] plan_features.py generado con 20 módulos
- [x] requirements.txt generado
- [ ] Crear app `products`
- [ ] Crear app `sales`
- [ ] Crear app `pos`
- [ ] Crear app `inventory`
- [ ] Personalizar templates
- [ ] Configurar .env
- [ ] Deploy en Render

---

## 🚀 Para crear más proyectos

### Ejemplo: App de Gimnasio

1. **Crear configuración** `templates/gym_config.json`:
```json
{
  "project_name": "GymApp",
  "industry": "fitness",
  "modules": {
    "members": {"name": "Miembros", "icon": "bi-people"},
    "classes": {"name": "Clases", "icon": "bi-calendar"},
    "trainers": {"name": "Entrenadores", "icon": "bi-person"}
  }
}
```

2. **Generar**:
```bash
python setup_new_project.py templates/gym_config.json D:\ESCRITORIO\GymApp
```

¡Y listo! 🎉

---

**Desarrollado por: Daniel (danioso8)**
