from django.db import models
from django.contrib.auth.models import User
from apps.organizations.base_models import TenantModel
import json


class JSONFieldCompatible(models.TextField):
    """
    Campo compatible con SQLite y PostgreSQL
    Almacena JSON como texto en SQLite, JSONField en PostgreSQL
    """
    def __init__(self, *args, **kwargs):
        kwargs.pop('default', None)
        super().__init__(*args, **kwargs)
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def to_python(self, value):
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return {}
    
    def get_prep_value(self, value):
        if value is None:
            return '{}'
        return json.dumps(value)
    
    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)


class Role(TenantModel):
    """
    Rol personalizado para agrupar permisos
    Ejemplos: Administrador, Doctor, Recepcionista, Vendedor, etc.
    """
    name = models.CharField(
        max_length=100,
        verbose_name='Nombre del Rol'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    is_system = models.BooleanField(
        default=False,
        verbose_name='Es Rol del Sistema',
        help_text='Los roles del sistema no se pueden eliminar'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_roles',
        verbose_name='Creado por'
    )
    
    class Meta:
        verbose_name = 'Rol'
        verbose_name_plural = 'Roles'
        ordering = ['name']
        unique_together = [['organization', 'name']]
    
    def __str__(self):
        return self.name
    
    @property
    def user_count(self):
        """Cantidad de usuarios con este rol"""
        return self.user_roles.count()
    
    @property
    def permission_count(self):
        """Cantidad de permisos asignados a este rol"""
        return self.role_permissions.count()


class Permission(TenantModel):
    """
    Permiso específico sobre un módulo
    Ejemplos:
    - patients.view (Ver pacientes)
    - patients.add (Agregar pacientes)
    - billing.delete (Eliminar facturas)
    """
    codename = models.CharField(
        max_length=100,
        verbose_name='Código',
        help_text='Formato: modulo.accion (ej: patients.view)'
    )
    name = models.CharField(
        max_length=255,
        verbose_name='Nombre Descriptivo'
    )
    module = models.ForeignKey(
        'organizations.ModulePermission',
        on_delete=models.CASCADE,
        related_name='detailed_permissions',
        verbose_name='Módulo'
    )
    description = models.TextField(
        blank=True,
        verbose_name='Descripción'
    )
    
    # Acciones disponibles (JSON)
    # Ejemplo: {"view": true, "add": true, "change": false, "delete": false}
    actions = JSONFieldCompatible(
        verbose_name='Acciones Permitidas',
        help_text='view, add, change, delete, export, etc.',
        blank=True
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    class Meta:
        verbose_name = 'Permiso'
        verbose_name_plural = 'Permisos'
        ordering = ['module__name', 'codename']
        unique_together = [['organization', 'codename']]
        indexes = [
            models.Index(fields=['codename']),
            models.Index(fields=['module']),
        ]
    
    def __str__(self):
        return f"{self.module.name} - {self.name}"
    
    def has_action(self, action):
        """Verifica si el permiso incluye una acción específica"""
        return self.actions.get(action, False)


class RolePermission(TenantModel):
    """
    Relación entre Roles y Permisos
    Un rol puede tener múltiples permisos
    """
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='role_permissions',
        verbose_name='Rol'
    )
    permission = models.ForeignKey(
        Permission,
        on_delete=models.CASCADE,
        related_name='permission_roles',
        verbose_name='Permiso'
    )
    granted_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Otorgado el'
    )
    granted_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='role_permissions_granted',
        verbose_name='Otorgado por'
    )
    
    class Meta:
        verbose_name = 'Permiso de Rol'
        verbose_name_plural = 'Permisos de Roles'
        unique_together = [['role', 'permission']]
        indexes = [
            models.Index(fields=['role', 'permission']),
        ]
    
    def __str__(self):
        return f"{self.role.name} - {self.permission.name}"


class UserRole(TenantModel):
    """
    Asignación de roles a usuarios
    Un usuario puede tener múltiples roles
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name='Usuario'
    )
    role = models.ForeignKey(
        Role,
        on_delete=models.CASCADE,
        related_name='user_roles',
        verbose_name='Rol'
    )
    assigned_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Asignado el'
    )
    assigned_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='assigned_user_roles',
        verbose_name='Asignado por'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Expira el',
        help_text='Opcional: fecha de expiración del rol'
    )
    
    class Meta:
        verbose_name = 'Rol de Usuario'
        verbose_name_plural = 'Roles de Usuarios'
        unique_together = [['user', 'role']]
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['role', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.role.name}"
    
    def is_expired(self):
        """Verifica si el rol ha expirado"""
        if not self.expires_at:
            return False
        from django.utils import timezone
        return timezone.now() > self.expires_at


class PermissionCache(models.Model):
    """
    Caché de permisos de usuario para mejorar performance
    Se actualiza cuando cambian los roles/permisos del usuario
    """
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name='permission_cache',
        verbose_name='Usuario'
    )
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name='Organización'
    )
    
    # Caché de permisos en JSON
    # Ejemplo: {"patients": {"view": true, "add": true}, "billing": {"view": true}}
    cached_permissions = JSONFieldCompatible(
        verbose_name='Permisos en Caché',
        blank=True
    )
    
    last_updated = models.DateTimeField(
        auto_now=True,
        verbose_name='Última Actualización'
    )
    
    class Meta:
        verbose_name = 'Caché de Permisos'
        verbose_name_plural = 'Cachés de Permisos'
        unique_together = [['user', 'organization']]
        indexes = [
            models.Index(fields=['user', 'organization']),
        ]
    
    def __str__(self):
        return f"Cache: {self.user.username} - {self.organization.name}"
    
    def has_permission(self, module_code, action='view'):
        """Verifica si el usuario tiene un permiso específico"""
        module_perms = self.cached_permissions.get(module_code, {})
        return module_perms.get(action, False)
    
    def refresh_cache(self):
        """Actualiza el caché de permisos del usuario"""
        from apps.permissions.services import PermissionService
        service = PermissionService(self.user, self.organization)
        self.cached_permissions = service.get_all_permissions()
        self.save()
