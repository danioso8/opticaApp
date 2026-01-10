"""
Signals para documentos.
"""
from django.db.models.signals import post_delete
from django.dispatch import receiver
import os

from .models import Document


@receiver(post_delete, sender=Document)
def delete_file_on_document_delete(sender, instance, **kwargs):
    """Elimina el archivo físico cuando se elimina el documento."""
    if instance.file:
        if os.path.isfile(instance.file.path):
            os.remove(instance.file.path)
