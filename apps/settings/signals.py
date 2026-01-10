"""
Signals para invalidar cache cuando cambian configuraciones.
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from django.core.cache import cache

from .models import AppSetting


@receiver(post_save, sender=AppSetting)
def invalidate_setting_cache_on_save(sender, instance, **kwargs):
    """Invalida el cache cuando se guarda una configuración."""
    cache_key = f"setting_{instance.key}_{instance.organization.id if instance.organization else 'global'}"
    cache.delete(cache_key)


@receiver(post_delete, sender=AppSetting)
def invalidate_setting_cache_on_delete(sender, instance, **kwargs):
    """Invalida el cache cuando se elimina una configuración."""
    cache_key = f"setting_{instance.key}_{instance.organization.id if instance.organization else 'global'}"
    cache.delete(cache_key)
