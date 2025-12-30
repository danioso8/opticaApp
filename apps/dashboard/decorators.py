"""
Decoradores para control de permisos por módulo
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from apps.organizations.models import OrganizationMember


def require_module_permission(module_code, permission_type='view'):
    """
    Decorador para verificar permisos de módulo
    
    Uso:
        @require_module_permission('patients', 'view')
        def patient_list(request):
            ...
    
    Args:
        module_code: Código del módulo (ej: 'patients', 'appointments', 'sales')
        permission_type: Tipo de permiso ('view', 'create', 'edit', 'delete')
    """
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def wrapped_view(request, *args, **kwargs):
            # Obtener membership del usuario
            membership = OrganizationMember.objects.filter(
                user=request.user,
                is_active=True
            ).select_related('organization').first()
            
            if not membership:
                messages.error(request, 'No tienes una organización asignada.')
                return redirect('dashboard:home')
            
            # Owner y Admin tienen acceso total
            if membership.role in ['owner', 'admin']:
                return view_func(request, *args, **kwargs)
            
            # Verificar permiso específico según el tipo
            has_permission = False
            
            if permission_type == 'view':
                has_permission = membership.can_view(module_code)
            elif permission_type == 'create':
                has_permission = membership.can_create(module_code)
            elif permission_type == 'edit':
                has_permission = membership.can_edit(module_code)
            elif permission_type == 'delete':
                has_permission = membership.can_delete(module_code)
            
            if not has_permission:
                messages.error(
                    request, 
                    f'No tienes permisos para {permission_type} en este módulo.'
                )
                return redirect('dashboard:home')
            
            # Agregar membership al request para usarlo en las vistas
            request.user_membership = membership
            
            return view_func(request, *args, **kwargs)
        
        return wrapped_view
    return decorator


def get_user_permissions(user):
    """
    Obtiene todos los permisos de un usuario para usar en templates
    
    Retorna un diccionario con los códigos de módulos y sus permisos
    """
    membership = OrganizationMember.objects.filter(
        user=user,
        is_active=True
    ).first()
    
    if not membership:
        return {}
    
    # Owner y Admin tienen todos los permisos
    if membership.role in ['owner', 'admin']:
        return {'is_admin': True, 'all_access': True}
    
    from apps.organizations.models import MemberModulePermission
    
    permissions = {}
    for perm in MemberModulePermission.objects.filter(member=membership).select_related('module'):
        permissions[perm.module.code] = {
            'can_view': perm.can_view,
            'can_create': perm.can_create,
            'can_edit': perm.can_edit,
            'can_delete': perm.can_delete,
        }
    
    return permissions
