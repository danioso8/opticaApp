# 🚀 GUÍA DE EJECUCIÓN - SISTEMA DE ADD-ONS

## ⚡ PASOS PARA ACTIVAR TODO

### 1️⃣ GENERAR MIGRACIONES (OBLIGATORIO)

```bash
cd D:\ESCRITORIO\OpticaApp
python create_addon_migrations.py
```

**Esto creará:**
- Nueva migración en `apps/organizations/migrations/`
- Agregará los 3 nuevos modelos a la base de datos
- Actualizará PlanFeature con nuevos campos

---

### 2️⃣ APLICAR MIGRACIONES (OBLIGATORIO)

```bash
python manage.py migrate
```

**Verifica que se ejecuten sin errores:**
```
✅ Applying organizations.000X_organizationfeature... OK
✅ Applying organizations.000X_invoicepackagepurchase... OK
✅ Applying organizations.000X_addonpurchase... OK
```

---

### 3️⃣ ACTUALIZAR PRECIOS DE PLANES (RECOMENDADO)

```bash
python check_and_create_plans.py
```

**Esto hará:**
- Actualizar Plan Gratuito: $0
- Actualizar Plan Básico: $29.900/mes
- Actualizar Plan Profesional: $89.900/mes
- **CREAR** Plan Premium: $149.900/mes
- Actualizar Plan Empresarial: $299.900/mes

**⚠️ IMPORTANTE:** Los usuarios existentes mantendrán su plan actual.

---

### 4️⃣ INICIAR SERVIDOR (PROBAR)

```bash
python manage.py runserver
```

**Acceder a:**
- SaaS-Admin: http://127.0.0.1:8000/saas-admin/
- Dashboard Normal: http://127.0.0.1:8000/dashboard/

---

## 🧪 PRUEBAS RÁPIDAS

### Prueba 1: Ver Módulos de una Organización

1. Login en SaaS-Admin
2. Ir a **Organizaciones**
3. Clic en cualquier organización
4. Clic en **"Gestionar Módulos"** (botón morado)
5. Deberías ver todos los módulos con toggles

**✅ Éxito:** Se muestra la lista de módulos por categoría

---

### Prueba 2: Agregar Paquete de Facturas

1. En detalle de organización
2. Clic en **"Agregar Facturas DIAN"** (botón verde)
3. Seleccionar paquete (ej: 100 facturas)
4. Precio se muestra automáticamente: $35.900
5. Marcar como "Pagado"
6. Guardar

**✅ Éxito:** Mensaje "Paquete de 100 facturas creado para..."

---

### Prueba 3: Agregar Módulo Individual

1. En detalle de organización
2. Clic en **"Agregar Módulo Individual"** (botón azul)
3. Seleccionar módulo de la lista
4. Elegir ciclo (Mensual/Trimestral/Anual/Vitalicio)
5. Precio se calcula automáticamente
6. Marcar como "Pagado"
7. Guardar

**✅ Éxito:** Módulo habilitado y visible en "Gestionar Módulos"

---

## 🔍 VERIFICAR EN BASE DE DATOS

### Verificar Nuevos Modelos

```bash
python manage.py shell
```

```python
from apps.organizations.models import *

# Verificar OrganizationFeature
print(OrganizationFeature.objects.count())

# Verificar InvoicePackagePurchase
print(InvoicePackagePurchase.objects.count())

# Verificar AddonPurchase
print(AddonPurchase.objects.count())

# Verificar nuevos campos en PlanFeature
feature = PlanFeature.objects.first()
print(f"Can purchase: {feature.can_purchase_separately}")
print(f"Price: {feature.price_monthly}")
```

---

## 🎯 CREAR DATOS DE PRUEBA (OPCIONAL)

### Script para Crear Módulos de Ejemplo

```python
# Ejecutar en: python manage.py shell

from apps.organizations.models import PlanFeature

# Crear módulo de WhatsApp
whatsapp = PlanFeature.objects.create(
    code='whatsapp_integration',
    name='Integración WhatsApp',
    description='Envía mensajes automáticos a tus pacientes',
    category='communication',
    icon='fab fa-whatsapp',
    price_monthly=19900.00,
    can_purchase_separately=True,
    is_active=True
)

# Crear módulo de Analytics
analytics = PlanFeature.objects.create(
    code='advanced_analytics',
    name='Analytics Avanzado',
    description='Reportes y estadísticas detalladas',
    category='analytics',
    icon='fas fa-chart-line',
    price_monthly=29900.00,
    can_purchase_separately=True,
    is_active=True
)

# Crear módulo de API
api = PlanFeature.objects.create(
    code='api_access',
    name='Acceso API',
    description='API REST para integrar con otros sistemas',
    category='integration',
    icon='fas fa-code',
    price_monthly=39900.00,
    can_purchase_separately=True,
    is_active=True
)

print("✅ 3 módulos creados exitosamente!")
```

---

## 🚨 SOLUCIÓN DE PROBLEMAS

### Error: "No module named 'organizations'"
**Solución:**
```bash
python manage.py migrate organizations
```

### Error: "Unknown column 'can_purchase_separately'"
**Solución:** No se ejecutaron las migraciones
```bash
python create_addon_migrations.py
python manage.py migrate
```

### Error: "Plan Premium not found"
**Solución:**
```bash
python check_and_create_plans.py
```

### Error 500 en las vistas nuevas
**Verificar:**
1. ¿Las migraciones se aplicaron?
2. ¿Existe plan para la organización?
3. Revisar logs en la terminal

---

## 📋 CHECKLIST DE IMPLEMENTACIÓN

- [ ] Generar migraciones: `python create_addon_migrations.py`
- [ ] Aplicar migraciones: `python manage.py migrate`
- [ ] Actualizar precios: `python check_and_create_plans.py`
- [ ] Iniciar servidor: `python manage.py runserver`
- [ ] Login en SaaS-Admin
- [ ] Probar "Gestionar Módulos"
- [ ] Probar "Agregar Facturas DIAN"
- [ ] Probar "Agregar Módulo Individual"
- [ ] Verificar toggles funcionan
- [ ] Verificar cálculo automático de precios

---

## 🎉 AL COMPLETAR

**Ya puedes:**
- ✅ Gestionar módulos por organización con checkboxes
- ✅ Vender paquetes de facturas DIAN sin cambiar plan
- ✅ Vender módulos individuales sin cambiar plan
- ✅ Tener precios competitivos en COP
- ✅ Control total desde el SaaS-Admin

---

## 📞 SIGUIENTE NIVEL (FUTURO)

### Funcionalidades Adicionales Sugeridas:
1. **Portal del Cliente** - Que ellos compren add-ons
2. **Pasarela de Pagos** - Integrar Wompi/PayU
3. **Notificaciones** - Email cuando se agota un paquete
4. **Dashboard de Facturación** - Reporte de ingresos por add-ons
5. **Cupones de Descuento** - Para promociones

---

**¿Listo para ejecutar?** 
```bash
python create_addon_migrations.py && python manage.py migrate && python check_and_create_plans.py
```
