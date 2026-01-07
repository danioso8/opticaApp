from django.apps import AppConfig


class PromotionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.promotions'
    verbose_name = 'Promociones y Campañas'
    
    def ready(self):
        """Importar signals cuando la app esté lista"""
        pass
