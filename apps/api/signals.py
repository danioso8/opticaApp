"""
Signals para API
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.api.models import APIKey


@receiver(post_save, sender=APIKey)
def apikey_post_save(sender, instance, created, **kwargs):
    """
    Signal después de crear/actualizar API Key
    """
    if created:
        # Log o notificación de creación de nueva API key
        print(f"Nueva API Key creada: {instance.name} ({instance.key_prefix}...)")
