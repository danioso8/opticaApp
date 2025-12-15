from django.apps import AppConfig


class BillingConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.billing'
    verbose_name = 'Facturación y Pagos'
    
    def ready(self):
        """Importa señales cuando la app está lista"""
        import apps.billing.signals  # noqa
