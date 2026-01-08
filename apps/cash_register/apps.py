from django.apps import AppConfig


class CashRegisterConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.cash_register'
    verbose_name = 'Gestión de Caja'

    def ready(self):
        """Importar señales cuando la app esté lista"""
        import apps.cash_register.signals
