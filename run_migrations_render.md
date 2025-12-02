# Ejecutar Migraciones en Render

## Opción 1: Desde el Shell de Render (RECOMENDADO)

1. Ve a tu servicio en Render Dashboard
2. Haz clic en la pestaña "Shell"
3. Ejecuta:
```bash
python manage.py migrate
python manage.py createsuperuser
python manage.py shell < crear_plan_basico.py
```

## Opción 2: Conectarse desde Local (Requiere permitir IP)

Si quieres conectarte desde tu máquina local, Render debe permitir tu IP pública.

### Paso 1: Verificar si Render permite conexiones externas

1. Ve a tu base de datos en Render Dashboard
2. Busca la sección "Access Control" o "Connections"
3. Verifica si está activado el acceso externo

### Paso 2: Usar URL Interna (Solo funciona desde Render)

La URL interna es:
```
dpg-d44ba4zs1cra77045d6g-a
```

Esta solo funciona desde servicios dentro de Render.

## Opción 3: Ejecutar migraciones con el deploy

Puedes configurar que las migraciones se ejecuten automáticamente en cada deploy.

En `build.sh`:
```bash
#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

# Ejecutar migraciones automáticamente
python manage.py migrate --no-input
python manage.py collectstatic --no-input
```

## Recomendación

Para tu caso, usa la **Opción 1** (Shell de Render) porque:
- Es la forma más directa
- No requiere configurar acceso externo
- Es la forma estándar para bases de datos en Render

## Crear superuser en Render

```bash
# En el Shell de Render
python manage.py createsuperuser
# Username: tu_usuario
# Email: tu_email@example.com
# Password: tu_contraseña_segura
```

## Crear planes de suscripción

```bash
# En el Shell de Render
python manage.py shell
```

Luego ejecuta:
```python
from apps.organizations.models import SubscriptionPlan

# Plan Básico
basic = SubscriptionPlan.objects.create(
    name="Plan Básico",
    description="Plan básico para pequeñas ópticas",
    price=0.00,
    max_users=5,
    max_patients=500,
    features={
        "appointments": True,
        "sales": True,
        "inventory": False,
        "whatsapp": False
    },
    is_active=True
)

# Plan Profesional
pro = SubscriptionPlan.objects.create(
    name="Plan Profesional",
    description="Plan profesional con todas las funciones",
    price=29.99,
    max_users=20,
    max_patients=5000,
    features={
        "appointments": True,
        "sales": True,
        "inventory": True,
        "whatsapp": True
    },
    is_active=True
)

print(f"Planes creados: {SubscriptionPlan.objects.count()}")
exit()
```
