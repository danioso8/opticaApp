"""
Vistas para la API de personalización del sidebar
"""
import json
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from .models_sidebar import SidebarCustomization


@login_required
@require_http_methods(["GET"])
def get_sidebar_config(request):
    """
    Obtiene la configuración del sidebar del usuario actual
    """
    if not request.organization:
        return JsonResponse({'error': 'No hay organización seleccionada'}, status=400)
    
    config = SidebarCustomization.get_or_create_config(
        user=request.user,
        organization=request.organization
    )
    
    return JsonResponse({
        'success': True,
        'config': config
    })


@login_required
@require_http_methods(["POST"])
def save_sidebar_config(request):
    """
    Guarda la configuración del sidebar del usuario actual
    """
    if not request.organization:
        return JsonResponse({'error': 'No hay organización seleccionada'}, status=400)
    
    try:
        data = json.loads(request.body)
        config_data = data.get('config', {})
        
        # Validar estructura básica
        if not isinstance(config_data, dict):
            return JsonResponse({'error': 'Configuración inválida'}, status=400)
        
        # Actualizar o crear configuración
        customization, created = SidebarCustomization.objects.update_or_create(
            user=request.user,
            organization=request.organization,
            defaults={
                'config': config_data,
                'version': config_data.get('version', 1)
            }
        )
        
        return JsonResponse({
            'success': True,
            'message': 'Configuración guardada correctamente',
            'created': created
        })
        
    except json.JSONDecodeError:
        return JsonResponse({'error': 'JSON inválido'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


@login_required
@require_http_methods(["POST"])
def reset_sidebar_config(request):
    """
    Restaura la configuración del sidebar a los valores por defecto
    """
    if not request.organization:
        return JsonResponse({'error': 'No hay organización seleccionada'}, status=400)
    
    try:
        SidebarCustomization.objects.filter(
            user=request.user,
            organization=request.organization
        ).delete()
        
        return JsonResponse({
            'success': True,
            'message': 'Configuración restaurada a valores por defecto'
        })
        
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)
