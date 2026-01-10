from django.apps import AppConfig


class PermissionsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.permissions'
    verbose_name = 'Gestión de Permisos'
    
    def ready(self):
        """Importar signals cuando la app esté lista"""
        import apps.permissions.signals
