"""
Decoradores para verificar acceso a módulos/características según el plan de suscripción
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse
from django.urls import reverse
from .plan_features import has_module_access, get_required_plan_for_module, get_module_info


def require_module(module_code):
    """
    Decorador que requiere acceso a un módulo específico
    
    Uso:
        @require_module('products')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Verificar si el usuario tiene acceso
            if not has_module_access(request.user, module_code):
                # Obtener información del módulo y plan requerido
                module_info = get_module_info(module_code)
                required_plan = get_required_plan_for_module(module_code)
                
                module_name = module_info.get('name', 'este módulo') if module_info else 'este módulo'
                
                messages.warning(
                    request,
                    f'⚠️ Necesitas actualizar a un plan superior para acceder a {module_name}. '
                    f'Plan requerido: {required_plan.upper()}'
                )
                
                # Redirigir a página de planes
                return redirect('organizations:subscription_plans')
            
            # Si tiene acceso, ejecutar la vista normalmente
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def require_plan(plan_type):
    """
    Decorador que requiere un plan específico o superior
    
    Uso:
        @require_plan('professional')
        def my_view(request):
            ...
    """
    # Orden de planes del menor al mayor
    PLAN_HIERARCHY = ['free', 'basic', 'professional', 'premium', 'enterprise']
    
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Obtener plan del usuario
            try:
                from apps.users.models import UserSubscription
                subscription = UserSubscription.objects.get(user=request.user)
                
                # Verificar que la suscripción esté activa
                if not subscription.is_active:
                    messages.error(request, 'Tu suscripción no está activa.')
                    return redirect('organizations:subscription_plans')
                
                # Verificar trial expirado
                if subscription.needs_payment_after_trial():
                    messages.warning(request, 'Tu período de prueba ha expirado. Por favor, realiza el pago.')
                    return redirect('users:trial_expired_checkout')
                
                # Verificar nivel del plan
                user_plan = subscription.plan.plan_type
                required_index = PLAN_HIERARCHY.index(plan_type)
                user_index = PLAN_HIERARCHY.index(user_plan)
                
                if user_index < required_index:
                    messages.warning(
                        request,
                        f'⚠️ Esta funcionalidad requiere el plan {plan_type.upper()} o superior. '
                        f'Tu plan actual: {user_plan.upper()}'
                    )
                    return redirect('organizations:subscription_plans')
                
            except UserSubscription.DoesNotExist:
                messages.error(request, 'No tienes una suscripción activa.')
                return redirect('organizations:subscription_plans')
            except ValueError:
                # Plan no reconocido
                messages.error(request, 'Plan no reconocido.')
                return redirect('organizations:subscription_plans')
            
            # Si tiene el plan requerido, ejecutar la vista
            return view_func(request, *args, **kwargs)
        
        return wrapper
    return decorator


def trial_required_payment(view_func):
    """
    Decorador que verifica si el trial expiró y necesita pago
    
    Uso:
        @trial_required_payment
        def my_view(request):
            ...
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        try:
            from apps.users.models import UserSubscription
            subscription = UserSubscription.objects.get(user=request.user)
            
            if subscription.needs_payment_after_trial():
                messages.warning(
                    request,
                    '⏰ Tu período de prueba ha expirado. Por favor, actualiza tu suscripción.'
                )
                return redirect('users:trial_expired_checkout')
                
        except UserSubscription.DoesNotExist:
            pass
        
        return view_func(request, *args, **kwargs)
    
    return wrapper


# Decoradores específicos para módulos comunes
def require_inventory(view_func):
    """Requiere acceso a inventario (plan Básico o superior)"""
    return require_module('products')(view_func)


def require_dian(view_func):
    """Requiere acceso a facturación DIAN (plan Profesional o superior)"""
    return require_module('invoices_dian')(view_func)


def require_whatsapp(view_func):
    """Requiere acceso a WhatsApp (plan Profesional o superior)"""
    return require_module('whatsapp')(view_func)


def require_analytics(view_func):
    """Requiere acceso a analytics avanzado (plan Premium o superior)"""
    return require_module('analytics')(view_func)


def require_team_management(view_func):
    """Requiere acceso a gestión de equipo (plan Premium o superior)"""
    return require_module('team_management')(view_func)


def require_api(view_func):
    """Requiere acceso a API (plan Empresarial)"""
    return require_module('api_access')(view_func)


def require_feature(feature_code):
    """
    Decorador que requiere acceso a una feature específica
    Alias de require_module para compatibilidad con el nuevo sistema de planes
    
    Uso:
        @require_feature('promotions')
        def my_view(request):
            ...
    """
    return require_module(feature_code)


# DECORADORES LEGACY (mantener para compatibilidad)
def feature_required(feature_code, redirect_to='dashboard:index'):
    """
    Decorador para vistas que requieren un módulo específico.
    
    Uso:
        @feature_required('whatsapp_integration')
        def my_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # LEGACY: Redirigir al nuevo sistema de módulos
            # Si el código de feature coincide con un código de módulo, usar el nuevo sistema
            if not has_module_access(request.user, feature_code):
                messages.warning(
                    request,
                    f'⚠️ Este módulo no está disponible en tu plan actual. '
                    f'Actualiza tu plan para acceder a esta funcionalidad.'
                )
                return redirect('organizations:subscription_plans')
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator



def api_feature_required(feature_code):
    """
    Decorador para APIs que requieren un módulo específico.
    Retorna JSON en caso de no tener acceso.
    
    Uso:
        @api_feature_required('api_access')
        def my_api_view(request):
            ...
    """
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            # Verificar si hay organización activa
            if not hasattr(request, 'organization') or not request.organization:
                return JsonResponse({
                    'success': False,
                    'error': 'No organization active'
                }, status=403)
            
            # Obtener suscripción activa
            from .models import Subscription
            subscription = Subscription.objects.filter(
                organization=request.organization,
                is_active=True
            ).first()
            
            if not subscription:
                return JsonResponse({
                    'success': False,
                    'error': 'No active subscription'
                }, status=403)
            
            # Verificar si tiene el módulo
            if not subscription.has_feature(feature_code):
                return JsonResponse({
                    'success': False,
                    'error': f'Feature "{feature_code}" not available in your plan',
                    'upgrade_required': True
                }, status=403)
            
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator
