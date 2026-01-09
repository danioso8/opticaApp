from django.apps import AppConfig


class AuditConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.audit'
    verbose_name = 'Auditoría'

    def ready(self):
        """Importar signals cuando la app esté lista."""
        import apps.audit.signals  # noqa
