from django.apps import AppConfig


class SettingsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.settings'
    verbose_name = 'Configuraciones'

    def ready(self):
        """Importar signals cuando la app esté lista."""
        import apps.settings.signals  # noqa
