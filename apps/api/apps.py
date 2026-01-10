from django.apps import AppConfig


class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.api'
    verbose_name = 'API REST'

    def ready(self):
        """Import signals when app is ready"""
        try:
            import apps.api.signals  # noqa
        except ImportError:
            pass
