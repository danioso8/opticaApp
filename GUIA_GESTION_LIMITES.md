# 📖 GUÍA DE GESTIÓN DE LÍMITES Y PLANES

## 🎯 Objetivo

Este sistema permite gestionar de forma centralizada todos los límites y características de los planes de suscripción, facilitando el desarrollo y mantenimiento a medida que se agregan nuevas funcionalidades.

## 📁 Archivos del Sistema

### 1. `plan_limits_config.py`
**Propósito:** Archivo de configuración central con todos los límites de planes

**Contenido:**
- Definición de límites para cada plan
- Configuración de facturación electrónica
- Módulos disponibles por plan
- Funciones de ayuda y validación

### 2. `sync_plan_limits.py`
**Propósito:** Script que sincroniza la configuración con la base de datos

**Uso:**
```bash
python sync_plan_limits.py
```

### 3. `apps/admin_dashboard/templates/admin_dashboard/plan_edit.html`
**Propósito:** Interfaz administrativa para editar planes

**Campos disponibles:**
- Información básica (nombre, tipo, precios)
- Límites (usuarios, organizaciones, citas, pacientes, almacenamiento)
- Facturación electrónica DIAN
- Características legacy
- Módulos del sistema

### 4. `apps/admin_dashboard/views.py` - función `plan_edit()`
**Propósito:** Vista que procesa las ediciones de planes

## 🔄 Flujo de Trabajo

### Opción A: Editar desde Admin Dashboard (Recomendado)
1. Acceder a `/admin-dashboard/plans/`
2. Click en "Editar" en el plan deseado
3. Modificar los valores necesarios
4. Guardar cambios
5. ✅ Los cambios se aplican inmediatamente a la base de datos

### Opción B: Editar desde Configuración y Sincronizar
1. Editar `plan_limits_config.py`
2. Modificar los valores en `PLAN_CONFIGURATIONS`
3. Ejecutar `python sync_plan_limits.py`
4. ✅ Los cambios se sincronizan a la base de datos

## 🆕 Agregar Nueva Funcionalidad con Límites

### Paso 1: Decidir el Nombre del Límite
Ejemplo: Agregar límite de "Campañas de Email Marketing"

### Paso 2: Agregar Campo al Modelo (si es necesario)
Editar `apps/organizations/models.py`:

```python
class SubscriptionPlan(models.Model):
    # ... campos existentes ...
    
    # NUEVO LÍMITE
    max_email_campaigns = models.IntegerField(
        default=0,
        verbose_name='Máx. Campañas Email/Mes',
        help_text='0 = Ilimitado, N = cantidad específica'
    )
```

### Paso 3: Crear Migración
```bash
python manage.py makemigrations
python manage.py migrate
```

### Paso 4: Actualizar Configuración
Editar `plan_limits_config.py`:

```python
PLAN_CONFIGURATIONS = {
    'free': {
        # ... configuración existente ...
        'limits': {
            # ... límites existentes ...
            'max_email_campaigns': 0,  # NUEVO
        },
    },
    'basic': {
        'limits': {
            # ... límites existentes ...
            'max_email_campaigns': 5,  # NUEVO
        },
    },
    'professional': {
        'limits': {
            # ... límites existentes ...
            'max_email_campaigns': 20,  # NUEVO
        },
    },
    'enterprise': {
        'limits': {
            # ... límites existentes ...
            'max_email_campaigns': UNLIMITED,  # NUEVO
        },
    },
}
```

### Paso 5: Actualizar Template de Edición
Editar `apps/admin_dashboard/templates/admin_dashboard/plan_edit.html`:

```html
<div>
    <label class="block text-sm font-medium text-gray-700 mb-2">
        <i class="fas fa-envelope text-indigo-600 mr-1"></i>
        Máx. Campañas Email/Mes
    </label>
    <input type="number" name="max_email_campaigns" 
           value="{{ plan.max_email_campaigns }}" min="0"
           class="w-full px-4 py-2 border-2 border-gray-300 rounded-lg focus:border-indigo-500"
           placeholder="0 para ilimitado">
    <p class="text-xs text-gray-500 mt-1">0 = Ilimitado</p>
</div>
```

### Paso 6: Actualizar Vista
Editar `apps/admin_dashboard/views.py` función `plan_edit()`:

```python
def plan_edit(request, plan_id):
    if request.method == 'POST':
        # ... código existente ...
        
        # NUEVO CAMPO
        plan.max_email_campaigns = request.POST.get('max_email_campaigns', 0)
        
        plan.save()
        # ... resto del código ...
```

### Paso 7: Sincronizar
```bash
python sync_plan_limits.py
```

### Paso 8: Verificar
```bash
python verify_all_plans.py
```

## 🛡️ Implementar Verificación de Límites en el Código

Cuando implementes la funcionalidad, verifica el límite:

```python
from apps.users.models import UserSubscription

def create_email_campaign(request):
    # Obtener suscripción del usuario
    try:
        subscription = UserSubscription.objects.get(user=request.user)
        plan = subscription.plan
        
        # Verificar límite
        current_campaigns = EmailCampaign.objects.filter(
            user=request.user,
            created_at__month=timezone.now().month
        ).count()
        
        max_allowed = plan.max_email_campaigns
        
        # Si no es ilimitado (0 o >= 999999) y alcanzó el límite
        if max_allowed > 0 and max_allowed < 999999:
            if current_campaigns >= max_allowed:
                messages.error(
                    request, 
                    f'Has alcanzado el límite de {max_allowed} campañas/mes. '
                    f'Actualiza tu plan para crear más.'
                )
                return redirect('plans:upgrade')
        
        # Proceder con la creación...
        
    except UserSubscription.DoesNotExist:
        messages.error(request, 'No tienes una suscripción activa.')
        return redirect('plans:list')
```

## 📊 Valores Especiales

### Ilimitado
```python
UNLIMITED = 999999
```

Para indicar límite ilimitado:
- Usar `999999` en la base de datos
- Usar `UNLIMITED` en código
- Usar `0` para facturación electrónica ilimitada

### Verificar si es Ilimitado
```python
from plan_limits_config import is_unlimited

if is_unlimited(plan.max_users):
    # El plan tiene usuarios ilimitados
    pass
```

## 🔍 Scripts de Utilidad

### Verificar Configuración
```bash
python plan_limits_config.py
```

### Sincronizar Planes
```bash
python sync_plan_limits.py
```

### Verificar Todos los Planes
```bash
python verify_all_plans.py
```

### Ver Estado de Usuario Específico
```bash
python check_user_orgs.py
```

## 📝 Convenciones

### Nombres de Campos
- Usar prefijo `max_` para límites: `max_users`, `max_campaigns`
- Usar `allow_` para permisos booleanos: `allow_electronic_invoicing`
- Usar sufijo `_month` para límites mensuales: `max_appointments_month`

### Valores por Defecto
- Límites numéricos: `0` o el mínimo razonable
- Booleanos: `False` (deshabilitado por defecto)
- Ilimitado: `999999` o `UNLIMITED`

### Orden de Planes
Siempre mantener este orden:
1. Free (gratuito)
2. Basic (básico)
3. Professional (profesional)
4. Enterprise (empresarial)

## ⚠️ Consideraciones Importantes

1. **Usuarios Existentes:** Los cambios en límites afectan inmediatamente a usuarios activos
2. **Valores Negativos:** Nunca usar valores negativos
3. **Facturación:** `0` significa ilimitado solo en `max_invoices_month`
4. **Consistencia:** Siempre usar `999999` para otros límites ilimitados
5. **Testing:** Después de cambios, ejecutar `verify_all_plans.py`

## 🎨 Iconos Recomendados (Font Awesome)

```python
ICONS = {
    'users': 'fas fa-users',
    'organizations': 'fas fa-building',
    'appointments': 'fas fa-calendar',
    'patients': 'fas fa-user-injured',
    'storage': 'fas fa-database',
    'invoicing': 'fas fa-file-invoice',
    'email': 'fas fa-envelope',
    'sms': 'fas fa-sms',
    'reports': 'fas fa-chart-bar',
    'analytics': 'fas fa-chart-line',
}
```

## 🚀 Roadmap de Funcionalidades Futuras

Cuando implementes estas funcionalidades, sigue esta guía:

- [ ] Campañas de Email Marketing
- [ ] SMS Marketing
- [ ] Reportes Personalizados
- [ ] Integraciones con Terceros
- [ ] Plantillas de Documentos
- [ ] Usuarios Adicionales
- [ ] Almacenamiento en Cloud
- [ ] Backup Automático

## 📞 Soporte

Si tienes dudas sobre cómo agregar límites para nuevas funcionalidades, revisa los ejemplos en este documento o consulta los archivos existentes como referencia.
