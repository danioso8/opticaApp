from django.db import models


class TenantModel(models.Model):
    """
    Modelo abstracto base para todos los modelos que deben ser multi-tenant
    """
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='%(class)s_set',
        verbose_name='Organización',
        null=True,  # Temporal para migración
        blank=True  # Temporal para migración
    )
    
    class Meta:
        abstract = True
        indexes = [
            models.Index(fields=['organization']),
        ]
