"""
Vistas para gestionar WhatsApp con Baileys
"""
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
from apps.appointments.whatsapp_baileys_client import whatsapp_baileys_client
from apps.notifications.models_whatsapp_connection import WhatsAppConnection
import logging

logger = logging.getLogger(__name__)


@login_required
def whatsapp_baileys_config(request):
    """Vista para configurar WhatsApp con Baileys"""
    
    if not hasattr(request, 'organization') or not request.organization:
        messages.error(request, 'No hay organización activa')
        return redirect('dashboard:home')
    
    org_id = request.organization.id
    
    # Obtener o crear el registro de conexión en BD
    connection = WhatsAppConnection.get_or_create_for_org(request.organization)
    
    # Obtener estado actual de forma segura
    try:
        status_data = whatsapp_baileys_client.get_status(org_id)
        server_active = whatsapp_baileys_client.healthcheck()
        
        # Sincronizar estado con la base de datos
        if status_data:
            WhatsAppConnection.sync_from_server(org_id, status_data)
            
    except Exception as e:
        logger.error(f"Error al conectar con servidor WhatsApp: {e}")
        status_data = None
        server_active = False
        messages.warning(request, 'No se pudo conectar con el servidor de WhatsApp. El servicio puede estar temporalmente no disponible.')
    
    context = {
        'organization': request.organization,
        'whatsapp_status': status_data or {'connected': False, 'message': 'Servidor no disponible'},
        'server_active': server_active,
        'whatsapp_connection': connection,  # Información de BD
    }
    
    return render(request, 'dashboard/whatsapp_baileys_config.html', context)


@login_required
def whatsapp_start_session(request):
    """Iniciar sesión de WhatsApp (generar QR)"""
    
    if not hasattr(request, 'organization') or not request.organization:
        return JsonResponse({'error': 'No hay organización activa'}, status=400)
    
    org_id = request.organization.id
    
    try:
        result = whatsapp_baileys_client.start_session(org_id)
        
        if result:
            return JsonResponse({
                'success': True,
                'message': 'Sesión iniciada. Escaneando QR...',
                'data': result
            })
        else:
            return JsonResponse({
                'error': 'No se pudo iniciar sesión con el servidor WhatsApp'
            }, status=500)
    
    except Exception as e:
        logger.error(f"Error iniciando sesión WhatsApp: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def whatsapp_get_qr(request):
    """Obtener código QR"""
    
    if not hasattr(request, 'organization') or not request.organization:
        return JsonResponse({'error': 'No hay organización activa'}, status=400)
    
    org_id = request.organization.id
    
    try:
        result = whatsapp_baileys_client.get_qr(org_id)
        
        if result:
            return JsonResponse({
                'success': True,
                'data': result
            })
        else:
            return JsonResponse({
                'error': 'No se pudo obtener el QR'
            }, status=500)
    
    except Exception as e:
        logger.error(f"Error obteniendo QR: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def whatsapp_get_status(request):
    """Obtener estado de la conexión"""
    
    try:
        # Verificar organización
        if not hasattr(request, 'organization') or not request.organization:
            return JsonResponse({
                'success': False, 
                'status': 'not_started',
                'message': 'No hay organización activa'
            })
        
        org_id = request.organization.id
        
        # Verificar salud del servidor WhatsApp primero
        if not whatsapp_baileys_client.healthcheck():
            return JsonResponse({
                'success': False,
                'status': 'server_down',
                'message': 'Servidor WhatsApp no disponible'
            })
        
        result = whatsapp_baileys_client.get_status(org_id)
        
        if result:
            status = result.get('status', 'not_started')
            phone_number = result.get('phone_number')
            qr_code = None
            
            # Si el status es qr_ready y has_qr es true, obtener el QR
            if status == 'qr_ready' and result.get('has_qr'):
                qr_result = whatsapp_baileys_client.get_qr(org_id)
                if qr_result and qr_result.get('qr'):
                    qr_code = qr_result.get('qr')
            
            # Sincronizar estado con la base de datos
            WhatsAppConnection.sync_from_server(org_id, result)
            
            return JsonResponse({
                'success': True,
                'status': status,
                'phone_number': phone_number,
                'qr': qr_code
            })
        else:
            return JsonResponse({
                'success': False,
                'status': 'error',
                'message': 'No se pudo obtener el estado'
            })
    
    except Exception as e:
        logger.error(f"Error obteniendo estado WhatsApp: {e}", exc_info=True)
        return JsonResponse({
            'success': False, 
            'status': 'error',
            'message': 'Error interno del servidor'
        })


@login_required
def whatsapp_logout(request):
    """Cerrar sesión de WhatsApp"""
    
    if not hasattr(request, 'organization') or not request.organization:
        return JsonResponse({'error': 'No hay organización activa'}, status=400)
    
    org_id = request.organization.id
    
    try:
        result = whatsapp_baileys_client.logout(org_id)
        
        if result:
            # Marcar como desconectado manualmente en la BD
            connection = WhatsAppConnection.get_or_create_for_org(request.organization)
            connection.mark_disconnected(
                reason='Desconexión manual del usuario',
                manual=True,
                user=request.user
            )
            
            messages.success(request, 'Sesión de WhatsApp cerrada correctamente')
            return JsonResponse({
                'success': True,
                'message': 'Sesión cerrada'
            })
        else:
            return JsonResponse({
                'error': 'No se pudo cerrar la sesión'
            }, status=500)
    
    except Exception as e:
        logger.error(f"Error cerrando sesión: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def whatsapp_clear_session(request):
    """Limpiar sesión corrupta de WhatsApp"""
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    if not hasattr(request, 'organization') or not request.organization:
        return JsonResponse({'error': 'No hay organización activa'}, status=400)
    
    org_id = request.organization.id
    
    try:
        # Intentar cerrar sesión primero
        try:
            whatsapp_baileys_client.logout(org_id)
        except:
            pass  # Ignorar errores al cerrar sesión corrupta
        
        # Limpiar sesión en el servidor
        result = whatsapp_baileys_client.clear_session(org_id)
        
        if result and result.get('success'):
            # Actualizar estado en BD
            connection = WhatsAppConnection.get_or_create_for_org(request.organization)
            connection.mark_disconnected(
                reason='Sesión corrupta limpiada',
                manual=False,
                user=None
            )
            connection.session_exists = False
            connection.save()
            
            messages.success(request, 'Sesión limpiada correctamente. Ya puedes conectar nuevamente.')
            return JsonResponse({
                'success': True,
                'message': 'Sesión limpiada correctamente'
            })
        else:
            return JsonResponse({
                'error': 'No se pudo limpiar la sesión'
            }, status=500)
    
    except Exception as e:
        logger.error(f"Error limpiando sesión: {e}")
        return JsonResponse({'error': str(e)}, status=500)


@login_required
def whatsapp_test_message(request):
    """Enviar mensaje de prueba"""
    
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    if not hasattr(request, 'organization') or not request.organization:
        return JsonResponse({'error': 'No hay organización activa'}, status=400)
    
    org_id = request.organization.id
    
    # Obtener datos del POST (FormData)
    phone = request.POST.get('phone', '').strip()
    message = request.POST.get('message', 'Hola! Este es un mensaje de prueba desde OpticaApp')
    
    if not phone:
        return JsonResponse({'error': 'El número de teléfono es requerido'}, status=400)
    
    try:
        logger.info(f"Enviando mensaje de prueba a {phone} desde organización {org_id}")
        logger.info(f"Mensaje: {message}")
        
        result = whatsapp_baileys_client.send_message(org_id, phone, message)
        
        if result and result.get('success'):
            return JsonResponse({
                'success': True,
                'message': 'Mensaje enviado exitosamente'
            })
        else:
            error_msg = result.get('error', 'No se pudo enviar el mensaje') if result else 'Error desconocido'
            logger.error(f"Error enviando mensaje: {error_msg}")
            return JsonResponse({
                'error': error_msg
            }, status=500)
    
    except Exception as e:
        logger.error(f"Error enviando mensaje de prueba: {e}", exc_info=True)
        return JsonResponse({'error': str(e)}, status=500)
