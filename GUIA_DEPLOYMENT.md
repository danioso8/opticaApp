# =============================================================================
# GUÍA COMPLETA DE DEPLOYMENT - SISTEMA DE MÓDULOS À LA CARTE
# =============================================================================

## PASO 1: SUBIR ARCHIVOS AL SERVIDOR

```bash
# Conectar al servidor
cd D:\ESCRITORIO\OpticaApp

# Subir archivos nuevos
scp -r apps/payments root@84.247.129.180:/var/www/opticaapp/
scp apps/dashboard/views_modules.py root@84.247.129.180:/var/www/opticaapp/apps/dashboard/
scp apps/admin_dashboard/views_modules.py root@84.247.129.180:/var/www/opticaapp/apps/admin_dashboard/

# Subir templates
scp -r apps/dashboard/templates/dashboard/modules root@84.247.129.180:/var/www/opticaapp/apps/dashboard/templates/dashboard/
scp -r apps/organizations/templates/emails root@84.247.129.180:/var/www/opticaapp/apps/organizations/templates/

# Subir servicios y tareas
scp apps/organizations/services/notifications.py root@84.247.129.180:/var/www/opticaapp/apps/organizations/services/
scp apps/organizations/tasks.py root@84.247.129.180:/var/www/opticaapp/apps/organizations/
scp apps/organizations/decorators.py root@84.247.129.180:/var/www/opticaapp/apps/organizations/

# Subir scripts
scp create_signals.py root@84.247.129.180:/var/www/opticaapp/
```

## PASO 2: CONFIGURAR SETTINGS

```bash
ssh root@84.247.129.180

cd /var/www/opticaapp
nano config/settings.py
```

**Agregar al final del archivo:**

```python
# Apps
INSTALLED_APPS += ['apps.payments']

# Stripe
STRIPE_PUBLIC_KEY = env('STRIPE_PUBLIC_KEY', default='')
STRIPE_SECRET_KEY = env('STRIPE_SECRET_KEY', default='')
STRIPE_WEBHOOK_SECRET = env('STRIPE_WEBHOOK_SECRET', default='')

# Wompi
WOMPI_PUBLIC_KEY = env('WOMPI_PUBLIC_KEY', default='')
WOMPI_PRIVATE_KEY = env('WOMPI_PRIVATE_KEY', default='')
WOMPI_SANDBOX = env.bool('WOMPI_SANDBOX', default=True)

# Trial
TRIAL_DURATION_DAYS = 30
GRACE_PERIOD_DAYS = 15
ARCHIVE_AFTER_DAYS = 90
DELETE_AFTER_DAYS = 210

# Site
SITE_URL = 'https://www.optikaapp.com'

# Celery Beat Schedule
from celery.schedules import crontab
CELERY_BEAT_SCHEDULE = {
    'check-trials-daily': {
        'task': 'apps.organizations.tasks.check_trial_status_daily',
        'schedule': crontab(hour=9, minute=0),
    },
    'update-usage-stats-daily': {
        'task': 'apps.organizations.tasks.update_module_usage_stats',
        'schedule': crontab(hour=2, minute=0),
    },
    'archive-expired-weekly': {
        'task': 'apps.organizations.tasks.archive_expired_organizations',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),
    },
    'delete-archived-monthly': {
        'task': 'apps.organizations.tasks.delete_archived_organizations',
        'schedule': crontab(hour=4, minute=0, day_of_month=1),
    },
}
```

## PASO 3: ACTUALIZAR URLS

**apps/dashboard/urls.py:**

```python
from apps.dashboard import views_modules

urlpatterns += [
    path('modules/marketplace/', views_modules.module_marketplace, name='module_marketplace'),
    path('modules/my-plan/', views_modules.my_plan, name='my_plan'),
    path('modules/selector/', views_modules.module_selector, name='module_selector'),
    path('modules/checkout/', views_modules.module_checkout, name='module_checkout'),
    path('modules/api/calculate-price/', views_modules.calculate_price, name='calculate_price'),
    path('modules/<int:module_id>/add/', views_modules.add_module, name='add_module'),
    path('modules/<int:module_id>/remove/', views_modules.remove_module, name='remove_module'),
]
```

**apps/admin_dashboard/urls.py:**

```python
from apps.admin_dashboard import views_modules

urlpatterns += [
    path('modules/dashboard/', views_modules.modules_dashboard, name='modules_dashboard'),
    path('modules/management/', views_modules.modules_management, name='modules_management'),
    path('modules/pricing/', views_modules.module_pricing_config, name='module_pricing_config'),
    path('modules/trials/', views_modules.trials_dashboard, name='trials_dashboard'),
    path('modules/trials/<int:trial_id>/', views_modules.trial_detail, name='trial_detail'),
    path('modules/analytics/', views_modules.conversion_analytics, name='conversion_analytics'),
    path('modules/notifications/', views_modules.notifications_log, name='notifications_log'),
    path('modules/api/update-price/<int:module_id>/', views_modules.update_module_price, name='update_module_price'),
    path('modules/api/toggle-status/<int:module_id>/', views_modules.toggle_module_status, name='toggle_module_status'),
]
```

**config/urls.py principal:**

```python
from django.urls import path, include

urlpatterns += [
    path('payments/', include('apps.payments.urls')),
]
```

## PASO 4: MIGRACIONES

```bash
cd /var/www/opticaapp
source venv/bin/activate

# Crear migraciones
python manage.py makemigrations organizations
python manage.py makemigrations payments

# Aplicar migraciones
python manage.py migrate

# Poblar módulos
python manage.py shell < populate_modules.py
```

## PASO 5: CONFIGURAR SIGNALS

```bash
# Ejecutar script de signals
python manage.py shell < create_signals.py

# Editar apps/organizations/apps.py
nano apps/organizations/apps.py
```

Agregar:
```python
def ready(self):
    import apps.organizations.signals
```

## PASO 6: INSTALAR DEPENDENCIAS

```bash
pip install stripe
pip install requests
```

## PASO 7: CONFIGURAR VARIABLES DE ENTORNO

```bash
nano .env
```

Agregar:
```
STRIPE_PUBLIC_KEY=pk_test_...
STRIPE_SECRET_KEY=sk_test_...
STRIPE_WEBHOOK_SECRET=whsec_...

WOMPI_PUBLIC_KEY=pub_test_...
WOMPI_PRIVATE_KEY=prv_test_...
WOMPI_SANDBOX=True
```

## PASO 8: CONFIGURAR CELERY BEAT

```bash
# Crear archivo de servicio para Celery Beat
nano /etc/systemd/system/celery-beat.service
```

Contenido:
```ini
[Unit]
Description=Celery Beat Service
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/var/www/opticaapp
Environment="PATH=/var/www/opticaapp/venv/bin"
ExecStart=/var/www/opticaapp/venv/bin/celery -A config beat -l info --scheduler django_celery_beat.schedulers:DatabaseScheduler

Restart=always
RestartSec=10

[Install]
WantedBy=multi-user.target
```

```bash
# Habilitar y arrancar
systemctl daemon-reload
systemctl enable celery-beat
systemctl start celery-beat
systemctl status celery-beat
```

## PASO 9: REINICIAR SERVICIOS

```bash
systemctl restart opticaapp
systemctl restart celery
systemctl restart celery-beat

# Verificar que todo está corriendo
systemctl status opticaapp
systemctl status celery
systemctl status celery-beat
```

## PASO 10: CONFIGURAR WEBHOOKS

**Stripe:**
1. Ir a https://dashboard.stripe.com/webhooks
2. Agregar endpoint: https://www.optikaapp.com/payments/webhooks/stripe/
3. Eventos a escuchar:
   - payment_intent.succeeded
   - payment_intent.payment_failed
4. Copiar el webhook secret a .env

**Wompi:**
1. Ir a https://comercios.wompi.co/webhooks
2. Agregar URL: https://www.optikaapp.com/payments/webhooks/wompi/
3. Eventos: transaction.updated

## PASO 11: VERIFICACIÓN

```bash
# Verificar que las tareas están registradas
cd /var/www/opticaapp
source venv/bin/activate
python manage.py shell

>>> from apps.organizations.tasks import check_trial_status_daily
>>> result = check_trial_status_daily.delay()
>>> result.get()
```

**En el navegador:**
1. Visitar: https://www.optikaapp.com/dashboard/modules/marketplace/
2. Crear una organización de prueba
3. Verificar que se crea TrialStatus automáticamente
4. Ver logs: `tail -f /var/log/celery/worker.log`

## PASO 12: MONITOREO

```bash
# Ver logs de Celery
tail -f /var/log/celery/worker.log
tail -f /var/log/celery/beat.log

# Ver logs de Gunicorn
tail -f /var/log/gunicorn/error.log

# Verificar tareas programadas
python manage.py shell
>>> from django_celery_beat.models import PeriodicTask
>>> PeriodicTask.objects.all()
```

## TROUBLESHOOTING

**Si Celery Beat no arranca:**
```bash
# Verificar logs
journalctl -u celery-beat -f

# Verificar permisos
chown -R root:root /var/www/opticaapp
chmod +x /var/www/opticaapp/venv/bin/celery
```

**Si las migraciones fallan:**
```bash
# Rollback y reintentar
python manage.py migrate organizations zero
python manage.py migrate organizations
```

**Si los webhooks no funcionan:**
```bash
# Verificar que CSRF está exento
# Las vistas de webhook usan @csrf_exempt
# Verificar logs de Nginx/Gunicorn
```

## MÉTRICAS A MONITOREAR

1. **Conversión de trials:** Admin Dashboard > Modules > Trials
2. **MRR (Monthly Recurring Revenue):** Admin Dashboard > Modules > Dashboard
3. **Módulos más populares:** Admin Dashboard > Modules > Analytics
4. **Notificaciones enviadas:** Admin Dashboard > Modules > Notifications
5. **Transacciones:** Admin Dashboard > Modules > Analytics

¡DEPLOYMENT COMPLETO! 🎉
