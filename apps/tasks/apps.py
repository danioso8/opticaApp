from django.apps import AppConfig


class TasksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.tasks'
    verbose_name = 'Gestión de Tareas'

    def ready(self):
        """Import signals when app is ready"""
        try:
            import apps.tasks.signals  # noqa
        except ImportError:
            pass
