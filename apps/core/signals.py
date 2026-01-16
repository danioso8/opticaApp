"""
Signals para manejo automático de carpetas de media
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.organizations.models import Organization
from apps.core.storage_utils import create_organization_media_folders
import logging

logger = logging.getLogger(__name__)


@receiver(post_save, sender=Organization)
def create_organization_folders(sender, instance, created, **kwargs):
    """
    Crea automáticamente la estructura de carpetas cuando se crea una organización
    """
    if created:
        try:
            create_organization_media_folders(instance.id)
            logger.info(f"✅ Carpetas de media creadas para organización #{instance.id} - {instance.name}")
        except Exception as e:
            logger.error(f"❌ Error creando carpetas para organización #{instance.id}: {e}")
