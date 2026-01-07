from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from .models import Organization, OrganizationMember


@receiver(post_save, sender=Organization)
def create_owner_membership(sender, instance, created, **kwargs):
    """
    Cuando se crea una organización, automáticamente agregar al owner como miembro
    """
    if created and instance.owner_id:
        OrganizationMember.objects.create(
            organization=instance,
            user=instance.owner,
            role='owner'
        )
