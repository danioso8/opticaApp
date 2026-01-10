"""
Servicio para gestión de permisos
Centraliza toda la lógica de permisos
"""
from django.contrib.auth.models import User
from django.db.models import Q
from apps.permissions.models import Role, Permission, UserRole, RolePermission, PermissionCache


class PermissionService:
    """Servicio centralizado para gestión de permisos"""
    
    def __init__(self, user, organization):
        self.user = user
        self.organization = organization
    
    def get_all_permissions(self):
        """
        Obtiene todos los permisos del usuario en la organización
        Retorna dict con estructura: {module_code: {action: boolean}}
        """
        # Obtener roles activos del usuario
        user_roles = UserRole.objects.filter(
            user=self.user,
            organization=self.organization,
            is_active=True
        ).select_related('role')
        
        # Si no tiene roles, retorna permisos vacíos
        if not user_roles.exists():
            return {}
        
        # Obtener IDs de roles
        role_ids = [ur.role_id for ur in user_roles]
        
        # Obtener permisos de esos roles
        role_permissions = RolePermission.objects.filter(
            role_id__in=role_ids,
            organization=self.organization
        ).select_related('permission', 'permission__module')
        
        # Construir diccionario de permisos
        permissions_dict = {}
        
        for rp in role_permissions:
            perm = rp.permission
            module_code = perm.module.code
            
            # Inicializar módulo si no existe
            if module_code not in permissions_dict:
                permissions_dict[module_code] = {}
            
            # Agregar acciones del permiso
            for action, allowed in perm.actions.items():
                if allowed:
                    permissions_dict[module_code][action] = True
        
        return permissions_dict
    
    def has_permission(self, module_code, action='view'):
        """
        Verifica si el usuario tiene un permiso específico
        Usa caché para mejorar performance
        """
        # Intentar obtener del caché
        try:
            cache = PermissionCache.objects.get(
                user=self.user,
                organization=self.organization
            )
        except PermissionCache.DoesNotExist:
            # Crear caché si no existe
            cache = PermissionCache.objects.create(
                user=self.user,
                organization=self.organization
            )
            cache.refresh_cache()
        
        return cache.has_permission(module_code, action)
    
    def has_module_access(self, module_code):
        """Verifica si el usuario tiene acceso al módulo (al menos view)"""
        return self.has_permission(module_code, 'view')
    
    def get_user_roles(self):
        """Obtiene los roles del usuario"""
        return Role.objects.filter(
            user_roles__user=self.user,
            user_roles__organization=self.organization,
            user_roles__is_active=True
        ).distinct()
    
    def assign_role(self, role, assigned_by=None, expires_at=None):
        """Asigna un rol al usuario"""
        user_role, created = UserRole.objects.get_or_create(
            user=self.user,
            role=role,
            organization=self.organization,
            defaults={
                'assigned_by': assigned_by,
                'expires_at': expires_at
            }
        )
        
        # Actualizar caché
        self.invalidate_cache()
        
        return user_role, created
    
    def remove_role(self, role):
        """Remueve un rol del usuario"""
        deleted_count = UserRole.objects.filter(
            user=self.user,
            role=role,
            organization=self.organization
        ).delete()[0]
        
        # Actualizar caché
        self.invalidate_cache()
        
        return deleted_count > 0
    
    def invalidate_cache(self):
        """Invalida el caché de permisos del usuario"""
        try:
            cache = PermissionCache.objects.get(
                user=self.user,
                organization=self.organization
            )
            cache.refresh_cache()
        except PermissionCache.DoesNotExist:
            # Crear nuevo caché
            cache = PermissionCache.objects.create(
                user=self.user,
                organization=self.organization
            )
            cache.refresh_cache()


class RoleService:
    """Servicio para gestión de roles"""
    
    def __init__(self, organization):
        self.organization = organization
    
    def create_role(self, name, description='', is_system=False, created_by=None):
        """Crea un nuevo rol"""
        role = Role.objects.create(
            organization=self.organization,
            name=name,
            description=description,
            is_system=is_system,
            created_by=created_by
        )
        return role
    
    def assign_permissions(self, role, permission_ids, granted_by=None):
        """Asigna múltiples permisos a un rol"""
        # Eliminar permisos existentes
        RolePermission.objects.filter(
            role=role,
            organization=self.organization
        ).delete()
        
        # Agregar nuevos permisos
        role_permissions = []
        for perm_id in permission_ids:
            role_permissions.append(
                RolePermission(
                    role=role,
                    permission_id=perm_id,
                    organization=self.organization,
                    granted_by=granted_by
                )
            )
        
        RolePermission.objects.bulk_create(role_permissions)
        
        # Invalidar cachés de usuarios con este rol
        self._invalidate_role_users_cache(role)
        
        return len(role_permissions)
    
    def _invalidate_role_users_cache(self, role):
        """Invalida cachés de todos los usuarios con este rol"""
        user_ids = UserRole.objects.filter(
            role=role,
            organization=self.organization,
            is_active=True
        ).values_list('user_id', flat=True)
        
        for cache in PermissionCache.objects.filter(user_id__in=user_ids, organization=self.organization):
            cache.refresh_cache()
    
    def get_role_permissions(self, role):
        """Obtiene todos los permisos de un rol"""
        return Permission.objects.filter(
            permission_roles__role=role,
            permission_roles__organization=self.organization
        ).distinct()
    
    def clone_role(self, source_role, new_name, created_by=None):
        """Clona un rol con todos sus permisos"""
        # Crear nuevo rol
        new_role = self.create_role(
            name=new_name,
            description=f"Clon de {source_role.name}",
            created_by=created_by
        )
        
        # Copiar permisos
        source_permissions = RolePermission.objects.filter(
            role=source_role,
            organization=self.organization
        ).values_list('permission_id', flat=True)
        
        self.assign_permissions(new_role, list(source_permissions), created_by)
        
        return new_role


def create_default_roles(organization, created_by=None):
    """
    Crea roles por defecto para una nueva organización
    """
    service = RoleService(organization)
    
    # Rol: Administrador (acceso completo)
    admin_role = service.create_role(
        name='Administrador',
        description='Acceso completo a todos los módulos',
        is_system=True,
        created_by=created_by
    )
    
    # Rol: Usuario Estándar (acceso limitado)
    user_role = service.create_role(
        name='Usuario Estándar',
        description='Acceso de solo lectura a módulos básicos',
        is_system=True,
        created_by=created_by
    )
    
    # Rol: Recepcionista
    receptionist_role = service.create_role(
        name='Recepcionista',
        description='Gestión de citas y pacientes',
        is_system=False,
        created_by=created_by
    )
    
    return {
        'admin': admin_role,
        'user': user_role,
        'receptionist': receptionist_role
    }
