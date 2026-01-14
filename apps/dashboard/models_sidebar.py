"""
Modelos para personalización del sidebar
"""
from django.db import models
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization

User = get_user_model()


class SidebarCustomization(models.Model):
    """
    Almacena la configuración personalizada del sidebar por usuario y organización
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sidebar_customizations')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='sidebar_customizations')
    config = models.JSONField(default=dict, help_text="Configuración del sidebar en formato JSON")
    version = models.IntegerField(default=1, help_text="Versión de la configuración")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Personalización de Sidebar"
        verbose_name_plural = "Personalizaciones de Sidebar"
        unique_together = ['user', 'organization']
        ordering = ['-updated_at']

    def __str__(self):
        return f"Sidebar de {self.user.get_full_name()} en {self.organization.name}"

    @classmethod
    def get_or_create_config(cls, user, organization):
        """
        Obtiene o crea la configuración del sidebar para un usuario y organización
        """
        config, created = cls.objects.get_or_create(
            user=user,
            organization=organization,
            defaults={'config': cls.get_default_config()}
        )
        return config.config

    @staticmethod
    def get_default_config():
        """
        Retorna la configuración por defecto del sidebar
        """
        return {
            'groups': [],
            'hiddenItems': [],
            'itemOrder': [],
            'customNames': {}
        }
