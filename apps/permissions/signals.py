"""
Signals para app permissions
"""
from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from apps.permissions.models import UserRole, RolePermission, PermissionCache


@receiver(post_save, sender=UserRole)
@receiver(post_delete, sender=UserRole)
def invalidate_user_permission_cache_on_role_change(sender, instance, **kwargs):
    """
    Invalida el caché de permisos cuando se asigna/remueve un rol
    """
    try:
        cache = PermissionCache.objects.get(
            user=instance.user,
            organization=instance.organization
        )
        cache.refresh_cache()
    except PermissionCache.DoesNotExist:
        # Crear caché si no existe
        cache = PermissionCache.objects.create(
            user=instance.user,
            organization=instance.organization
        )
        cache.refresh_cache()


@receiver(post_save, sender=RolePermission)
@receiver(post_delete, sender=RolePermission)
def invalidate_role_users_cache_on_permission_change(sender, instance, **kwargs):
    """
    Invalida los cachés de todos los usuarios con el rol
    cuando cambian los permisos del rol
    """
    # Obtener usuarios con este rol
    user_ids = UserRole.objects.filter(
        role=instance.role,
        organization=instance.organization,
        is_active=True
    ).values_list('user_id', flat=True)
    
    # Actualizar cachés
    for cache in PermissionCache.objects.filter(user_id__in=user_ids, organization=instance.organization):
        cache.refresh_cache()
