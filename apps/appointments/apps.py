from django.apps import AppConfig


class AppointmentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.appointments'
    verbose_name = 'Citas'
    
    def ready(self):
        # Importar signals para conectarlos
        import apps.appointments.signals_setup
