"""
Decoradores y utilidades para control de permisos en módulo de nómina
"""
from functools import wraps
from django.contrib import messages
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required


def get_user_payroll_role(user, organization):
    """
    Determina el rol del usuario en el módulo de nómina
    Returns: 'PROPIETARIO', 'CONTADOR', 'ADMIN', or None
    """
    # Verificar si es propietario de la organización
    if hasattr(organization, 'owner') and organization.owner == user:
        return 'PROPIETARIO'
    
    # Verificar si es miembro con rol de contador
    try:
        from apps.organizations.models import Member
        member = Member.objects.filter(
            organization=organization,
            user=user,
            is_active=True
        ).first()
        
        if member:
            if member.role in ['CONTADOR', 'ACCOUNTANT']:
                return 'CONTADOR'
            elif member.role in ['ADMIN', 'ADMINISTRATOR']:
                return 'ADMIN'
    except:
        pass
    
    # Si es superuser
    if user.is_superuser:
        return 'ADMIN'
    
    return None


def payroll_permission_required(allowed_roles=None):
    """
    Decorador para verificar permisos en módulo de nómina
    
    Usage:
        @payroll_permission_required(['PROPIETARIO', 'CONTADOR'])
        def my_view(request):
            ...
    """
    if allowed_roles is None:
        allowed_roles = ['PROPIETARIO', 'CONTADOR', 'ADMIN']
    
    def decorator(view_func):
        @wraps(view_func)
        @login_required
        def _wrapped_view(request, *args, **kwargs):
            organization = getattr(request, 'organization', None)
            
            if not organization:
                messages.error(request, 'No se pudo identificar la organización.')
                return redirect('dashboard:home')
            
            user_role = get_user_payroll_role(request.user, organization)
            
            if user_role not in allowed_roles:
                messages.error(
                    request,
                    f'No tienes permisos para realizar esta acción. '
                    f'Solo {", ".join(allowed_roles)} pueden acceder.'
                )
                return redirect('payroll:payroll_dashboard')
            
            # Agregar el rol al request para uso posterior
            request.payroll_role = user_role
            
            return view_func(request, *args, **kwargs)
        
        return _wrapped_view
    return decorator


def contador_or_owner_required(view_func):
    """
    Decorador simplificado que solo permite contador o propietario
    """
    return payroll_permission_required(['PROPIETARIO', 'CONTADOR'])(view_func)


def owner_only_required(view_func):
    """
    Decorador que solo permite propietario
    """
    return payroll_permission_required(['PROPIETARIO'])(view_func)


def can_approve_payroll(user, organization):
    """
    Verifica si el usuario puede aprobar nóminas
    Solo propietarios y contadores pueden aprobar
    """
    role = get_user_payroll_role(user, organization)
    return role in ['PROPIETARIO', 'CONTADOR']


def can_modify_payroll(user, organization):
    """
    Verifica si el usuario puede modificar nóminas
    Propietarios, contadores y admins pueden modificar
    """
    role = get_user_payroll_role(user, organization)
    return role in ['PROPIETARIO', 'CONTADOR', 'ADMIN']


def log_payroll_action(user, organization, action, description, period=None):
    """
    Registra acciones importantes en el módulo de nómina para auditoría
    """
    try:
        from .models import PayrollCalculationLog
        
        PayrollCalculationLog.objects.create(
            organization=organization,
            payroll_period=period,
            action=action,
            description=description,
            user=user,
            is_success=True
        )
    except Exception as e:
        # No fallar si no se puede registrar el log
        print(f"Error logging payroll action: {e}")
