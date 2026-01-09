"""
Signals para reportes.
"""
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import ScheduledReport


@receiver(post_save, sender=ScheduledReport)
def calculate_next_run_on_create(sender, instance, created, **kwargs):
    """Calcula la próxima ejecución cuando se crea un reporte programado."""
    if created and not instance.next_run_at:
        instance.calculate_next_run()
