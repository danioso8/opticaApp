# Errores Comunes y Soluciones - OpticaApp

## 📋 Índice
1. [Error 500: Organization matching query does not exist](#error-500-organization-matching-query-does-not-exist)
2. [Error 500: Column does not exist](#error-500-column-does-not-exist)
3. [Error 500: Template does not exist](#error-500-template-does-not-exist)
4. [Calendario muestra todas las fechas en lugar de fechas específicas](#calendario-muestra-todas-las-fechas)

---

## Error 500: Organization matching query does not exist

### Síntomas
- Error 500 en endpoints públicos (`/api/available-dates/`, `/api/available-slots/`, etc.)
- En el navegador: `SyntaxError: Unexpected token '<', "<!doctype "... is not valid JSON`
- En logs: `Organization matching query does not exist`

### Causa
El **throttling (rate limiting)** de DRF está activo en endpoints públicos. Cuando alguien accede sin autenticación, `IPRateThrottle` intenta crear un `RateLimitRecord` que hereda de `TenantModel` y **requiere una organización**, pero el rate limit por IP no tiene organización asociada.

### Solución

**Archivo:** `apps/appointments/views.py` (o cualquier endpoint público)

```python
from rest_framework.decorators import api_view, permission_classes, throttle_classes

@api_view(['GET'])
@permission_classes([AllowAny])
@throttle_classes([])  # ⭐ Desactivar throttling para endpoint público
def available_dates(request):
    # ... código del endpoint
```

**Aplicar en todos los endpoints públicos:**
- `available_dates`
- `available_slots`
- `book_appointment`

### Cómo identificar el error
```bash
# 1. Activar DEBUG temporalmente
ssh root@84.247.129.180 "cd /var/www/opticaapp && sed -i 's/^DEBUG=False/DEBUG=True/' .env && pm2 restart opticaapp"

# 2. Hacer curl al endpoint
curl -s 'http://127.0.0.1:8000/api/available-dates/?organization_id=4' | grep -A5 'Exception Type'

# 3. Buscar en el error:
# Exception Type: DoesNotExist
# Exception Value: Organization matching query does not exist.
# File: apps/api/throttling.py, line 64, in allow_request

# 4. Desactivar DEBUG
ssh root@84.247.129.180 "cd /var/www/opticaapp && sed -i 's/^DEBUG=True/DEBUG=False/' .env && pm2 restart opticaapp"
```

---

## Error 500: Column does not exist

### Síntomas
- Error 500 al acceder a `/dashboard/employees/` u otras vistas
- En logs: `column dashboard_employee.incluir_en_nomina does not exist`
- Error: `Error sincronizando con dashboard/employees`

### Causa
El modelo tiene un campo nuevo pero **falta la migración** en la base de datos.

### Solución

**1. Crear la migración localmente:**

```python
# apps/dashboard/migrations/0028_employee_payroll_fields.py
from django.db import migrations, models

class Migration(migrations.Migration):
    dependencies = [
        ('dashboard', '0010_delete_auditlog'),  # Última migración
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='incluir_en_nomina',
            field=models.BooleanField(default=False, verbose_name='Incluir en Nómina'),
        ),
        # ... otros campos
    ]
```

**2. Subir al servidor:**
```bash
scp apps/dashboard/migrations/0028_employee_payroll_fields.py root@84.247.129.180:/var/www/opticaapp/apps/dashboard/migrations/
```

**3. Aplicar migración:**
```bash
ssh root@84.247.129.180 "cd /var/www/opticaapp && source venv/bin/activate && python manage.py migrate dashboard"
```

**4. Reiniciar:**
```bash
ssh root@84.247.129.180 "pm2 restart opticaapp"
```

### Verificar última migración
```bash
# Ver nombre de la última migración
Get-ChildItem apps\dashboard\migrations\*.py | Sort-Object Name -Descending | Select-Object -First 1 Name
```

---

## Error 500: Template does not exist

### Síntomas
- Error 500 en vistas específicas
- En logs: `TemplateDoesNotExist: promotions/campaign_detail.html`

### Causa
La vista intenta renderizar un template que **no existe** en el filesystem.

### Solución

**1. Verificar si existe el template:**
```bash
Get-ChildItem -Path apps\promotions\templates -Recurse -Filter *.html | Select-Object FullName
```

**2. Crear el template faltante:**
```django-html
{% extends 'dashboard/base.html' %}
{% load static %}

{% block title %}{{ campaign.name }} - Detalles{% endblock %}

{% block content %}
<!-- Contenido del template -->
{% endblock %}
```

**3. Subir al servidor:**
```bash
scp apps/promotions/templates/promotions/campaign_detail.html root@84.247.129.180:/var/www/opticaapp/apps/promotions/templates/promotions/
```

**4. NO requiere reinicio** - Django carga templates dinámicamente en producción con DEBUG=False.

---

## Calendario muestra todas las fechas

### Síntomas
- El calendario del booking muestra **todos los días laborables** (Lunes-Sábado) en lugar de solo las fechas específicas configuradas
- Muestra 26+ fechas cuando solo hay 2 configuradas

### Causa
El endpoint `available_dates` está generando fechas automáticamente desde `WorkingHours` en lugar de solo mostrar las fechas de `SpecificDateSchedule`.

### Solución

**Archivo:** `apps/appointments/views.py`

**ANTES (incorrecto):**
```python
# Genera fechas desde WorkingHours (todos los días laborables)
working_hours = WorkingHours.objects.filter(organization=organization, is_active=True)
working_days = set(working_hours.values_list('day_of_week', flat=True))

for i in range(max_days + 1):
    current_date = today + timedelta(days=i)
    if current_date.weekday() in working_days:
        available_dates.append(str(current_date))

# Luego agrega fechas específicas
specific_dates = SpecificDateSchedule.objects.filter(...)
```

**DESPUÉS (correcto):**
```python
# SOLO mostrar fechas específicas configuradas
available_dates = []

# Obtener fechas específicas configuradas
filters = {
    'organization': organization,
    'date__gte': today,
    'is_active': True
}

if doctor_id:
    # SOLO fechas del doctor específico
    from django.db.models import Q
    specific_dates = SpecificDateSchedule.objects.filter(
        Q(doctor_profile_id=doctor_id) | Q(doctor_id=doctor_id),
        **filters
    ).values_list('date', flat=True).distinct()
else:
    # Todas las fechas específicas
    specific_dates = SpecificDateSchedule.objects.filter(**filters).values_list('date', flat=True).distinct()

# Agregar solo fechas específicas no bloqueadas
for date in specific_dates:
    is_blocked = BlockedDate.objects.filter(organization=organization, date=date).exists()
    if not is_blocked:
        available_dates.append(str(date))

available_dates.sort()
return Response({'dates': available_dates})
```

### Comportamiento correcto
- **Sin doctor seleccionado:** Muestra todas las fechas configuradas en "Horarios Específicos por Fecha"
- **Con doctor seleccionado:** Solo muestra las fechas de ese doctor específico
- **No genera fechas automáticas** desde WorkingHours

### Aplicar cambios
```bash
scp apps/appointments/views.py root@84.247.129.180:/var/www/opticaapp/apps/appointments/
ssh root@84.247.129.180 "pm2 restart opticaapp"
```

---

## 🔧 Comandos Útiles para Diagnóstico

### Ver logs en tiempo real
```bash
ssh root@84.247.129.180 "pm2 logs opticaapp --lines 50 --nostream | grep -i 'error\|exception'"
```

### Activar/Desactivar DEBUG
```bash
# Activar
ssh root@84.247.129.180 "cd /var/www/opticaapp && sed -i 's/^DEBUG=False/DEBUG=True/' .env && pm2 restart opticaapp"

# Desactivar
ssh root@84.247.129.180 "cd /var/www/opticaapp && sed -i 's/^DEBUG=True/DEBUG=False/' .env && pm2 restart opticaapp"
```

### Verificar migraciones pendientes
```bash
ssh root@84.247.129.180 "cd /var/www/opticaapp && source venv/bin/activate && python manage.py showmigrations dashboard"
```

### Probar endpoint desde servidor
```bash
ssh root@84.247.129.180 "curl -s 'http://127.0.0.1:8000/api/available-dates/?organization_id=4'"
```

### Limpiar cache de Python
```bash
ssh root@84.247.129.180 "cd /var/www/opticaapp && find . -name '*.pyc' -delete && find . -name '__pycache__' -type d -delete"
ssh root@84.247.129.180 "pm2 restart opticaapp"
```

---

## 📝 Checklist antes de Deployment

- [ ] Verificar que no faltan templates
- [ ] Aplicar todas las migraciones localmente
- [ ] Subir migraciones al servidor
- [ ] Ejecutar `python manage.py migrate` en servidor
- [ ] Verificar endpoints públicos tienen `@throttle_classes([])`
- [ ] Limpiar cache de Python
- [ ] Reiniciar PM2
- [ ] Probar endpoints críticos con curl
- [ ] Desactivar DEBUG en producción

---

**Última actualización:** 10 de enero de 2026
