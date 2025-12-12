from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from apps.appointments.models import Appointment
from apps.appointments.models_notifications import AppointmentNotification


@login_required
@require_http_methods(["GET"])
def get_new_appointments(request):
    """
    API endpoint para obtener citas nuevas no notificadas
    Usado por el sistema de notificaciones push en tiempo real
    """
    organization = request.user.organization_memberships.first().organization
    
    # Obtener citas nuevas que no han sido notificadas
    new_notifications = AppointmentNotification.objects.filter(
        organization=organization,
        is_notified=False,
        created_from_landing=True
    ).select_related('appointment', 'appointment__patient', 'appointment__doctor')
    
    notifications_data = []
    for notification in new_notifications:
        appointment = notification.appointment
        notifications_data.append({
            'id': notification.id,
            'appointment_id': appointment.id,
            'patient_name': appointment.patient.full_name,
            'patient_phone': appointment.patient.phone_number,
            'doctor_name': appointment.doctor.full_name if appointment.doctor else 'Sin asignar',
            'appointment_date': appointment.appointment_date.strftime('%Y-%m-%d'),
            'appointment_time': appointment.appointment_time.strftime('%H:%M'),
            'created_at': notification.created_at.isoformat(),
        })
        
        # Marcar como notificada
        notification.is_notified = True
        notification.notified_at = timezone.now()
        notification.save()
    
    return JsonResponse({
        'success': True,
        'count': len(notifications_data),
        'notifications': notifications_data
    })


@login_required
@require_http_methods(["POST"])
def mark_notification_read(request):
    """Marca una notificación como leída"""
    try:
        notification_id = request.POST.get('notification_id')
        organization = request.user.organization_memberships.first().organization
        
        notification = AppointmentNotification.objects.get(
            id=notification_id,
            organization=organization
        )
        notification.is_notified = True
        notification.notified_at = timezone.now()
        notification.save()
        
        return JsonResponse({'success': True})
    except AppointmentNotification.DoesNotExist:
        return JsonResponse({'success': False, 'error': 'Notificación no encontrada'}, status=404)
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=500)
