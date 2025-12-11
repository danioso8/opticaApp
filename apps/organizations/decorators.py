"""
Decoradores para verificar acceso a módulos/características según el plan de suscripción
"""
from functools import wraps
from django.shortcuts import redirect
from django.contrib import messages
from django.http import JsonResponse


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
            # Verificar si hay organización activa
            if not hasattr(request, 'organization') or not request.organization:
                messages.error(request, 'No tienes una organización activa')
                return redirect('dashboard:index')
            
            # Obtener suscripción activa
            from .models import Subscription
            subscription = Subscription.objects.filter(
                organization=request.organization,
                is_active=True
            ).first()
            
            if not subscription:
                messages.error(request, 'No tienes una suscripción activa')
                return redirect(redirect_to)
            
            # Verificar si tiene el módulo
            if not subscription.has_feature(feature_code):
                messages.error(
                    request, 
                    f'Este módulo no está disponible en tu plan actual. '
                    f'Actualiza tu plan para acceder a esta funcionalidad.'
                )
                return redirect(redirect_to)
            
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
