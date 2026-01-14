# =============================================================================
# CONFIGURACIÓN PARA SISTEMA DE MÓDULOS À LA CARTE
# =============================================================================

# Agregar a config/settings.py o .env

# ----- APPS INSTALADAS -----
INSTALLED_APPS = [
    # ... apps existentes ...
    'apps.payments',  # ← AGREGAR ESTA LÍNEA
]

# ----- STRIPE CONFIGURATION -----
STRIPE_PUBLIC_KEY = 'pk_test_...'  # Reemplazar con tu clave pública
STRIPE_SECRET_KEY = 'sk_test_...'  # Reemplazar con tu clave secreta
STRIPE_WEBHOOK_SECRET = 'whsec_...'  # Para verificar webhooks

# ----- WOMPI CONFIGURATION (Colombia) -----
WOMPI_PUBLIC_KEY = 'pub_test_...'  # Reemplazar con tu clave pública
WOMPI_PRIVATE_KEY = 'prv_test_...'  # Reemplazar con tu clave privada
WOMPI_SANDBOX = True  # False en producción

# ----- PAYPAL CONFIGURATION (Opcional) -----
PAYPAL_CLIENT_ID = ''
PAYPAL_CLIENT_SECRET = ''
PAYPAL_MODE = 'sandbox'  # 'live' en producción

# ----- TRIAL CONFIGURATION -----
TRIAL_DURATION_DAYS = 30
GRACE_PERIOD_DAYS = 15  # Total: 45 días desde inicio
ARCHIVE_AFTER_DAYS = 90
DELETE_AFTER_DAYS = 210

# ----- EMAIL CONFIGURATION -----
DEFAULT_FROM_EMAIL = 'noreply@optikaapp.com'
TRIAL_NOTIFICATIONS_EMAIL = 'hello@optikaapp.com'

# WhatsApp para notificaciones
LANDING_WHATSAPP_NUMBER = '+573123456789'
LANDING_WHATSAPP_API_URL = 'http://localhost:3000'

# ----- CELERY BEAT SCHEDULE -----
from celery.schedules import crontab

CELERY_BEAT_SCHEDULE = {
    # Verificar trials diariamente a las 9 AM
    'check-trials-daily': {
        'task': 'apps.organizations.tasks.check_trial_status_daily',
        'schedule': crontab(hour=9, minute=0),
    },
    
    # Actualizar estadísticas de uso diariamente a las 2 AM
    'update-usage-stats-daily': {
        'task': 'apps.organizations.tasks.update_module_usage_stats',
        'schedule': crontab(hour=2, minute=0),
    },
    
    # Archivar organizaciones expiradas (domingos a las 3 AM)
    'archive-expired-weekly': {
        'task': 'apps.organizations.tasks.archive_expired_organizations',
        'schedule': crontab(hour=3, minute=0, day_of_week=0),
    },
    
    # Eliminar organizaciones archivadas (día 1 de cada mes a las 4 AM)
    'delete-archived-monthly': {
        'task': 'apps.organizations.tasks.delete_archived_organizations',
        'schedule': crontab(hour=4, minute=0, day_of_month=1),
    },
}

# ----- SITE CONFIGURATION -----
SITE_URL = 'https://www.optikaapp.com'  # URL de tu sitio

# =============================================================================
# INSTRUCCIONES DE DEPLOYMENT
# =============================================================================

"""
1. MIGRAR BASE DE DATOS:
   python manage.py makemigrations organizations
   python manage.py makemigrations payments
   python manage.py migrate

2. POBLAR MÓDULOS:
   python manage.py shell < populate_modules.py

3. CONFIGURAR CELERY BEAT:
   # Asegurarse de que Celery Beat está corriendo
   celery -A config beat -l info

4. CONFIGURAR WEBHOOKS:
   Stripe:
   - URL: https://tudominio.com/payments/webhooks/stripe/
   - Eventos: payment_intent.succeeded, payment_intent.payment_failed
   
   Wompi:
   - URL: https://tudominio.com/payments/webhooks/wompi/
   - Eventos: transaction.updated

5. CREAR SIGNALS:
   # Ejecutar create_signals.py para crear apps/organizations/signals.py
   python manage.py shell < create_signals.py
   
   # Agregar a apps/organizations/apps.py:
   def ready(self):
       import apps.organizations.signals

6. REINICIAR SERVICIOS:
   systemctl restart opticaapp
   systemctl restart celery
   systemctl restart celery-beat

7. VERIFICAR INSTALACIÓN:
   - Visitar /dashboard/modules/marketplace/
   - Crear una organización de prueba
   - Verificar que se crea TrialStatus automáticamente
   - Verificar que Celery Beat está ejecutando las tareas
"""
