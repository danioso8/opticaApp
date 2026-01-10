from rest_framework import viewsets, status
from rest_framework.decorators import action, api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from django.utils import timezone
from datetime import datetime

from .models import (
    AppointmentConfiguration,
    WorkingHours,
    BlockedDate,
    Appointment,
    TimeSlot
)
from apps.patients.models import Patient
from .serializers import (
    AppointmentConfigurationSerializer,
    WorkingHoursSerializer,
    BlockedDateSerializer,
    AppointmentListSerializer,
    AppointmentDetailSerializer,
    AppointmentCreateSerializer,
    TimeSlotSerializer,
    AvailableSlotsSerializer,
    AvailableDatesSerializer
)
from .utils import (
    get_available_slots_for_date,
    get_available_dates,
    get_appointments_stats,
    check_slot_availability
)


class AppointmentViewSet(viewsets.ModelViewSet):
    """ViewSet para gestión de citas (ADMIN)"""
    queryset = Appointment.objects.all()
    permission_classes = [IsAuthenticated]
    
    def get_serializer_class(self):
        if self.action == 'list':
            return AppointmentListSerializer
        return AppointmentDetailSerializer
    
    def get_queryset(self):
        # Filtrar por organización si existe
        queryset = Appointment.objects.all()
        if hasattr(self.request, 'organization') and self.request.organization:
            queryset = queryset.filter(organization=self.request.organization)
        
        # Filtros
        status_filter = self.request.query_params.get('status', None)
        date_filter = self.request.query_params.get('date', None)
        phone_filter = self.request.query_params.get('phone', None)
        
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        if date_filter:
            queryset = queryset.filter(appointment_date=date_filter)
        
        if phone_filter:
            queryset = queryset.filter(phone_number__icontains=phone_filter)
        
        return queryset
    
    @action(detail=False, methods=['get'])
    def today(self, request):
        """Obtiene las citas del día"""
        today = timezone.now().date()
        appointments = Appointment.objects.filter(appointment_date=today)
        if hasattr(request, 'organization') and request.organization:
            appointments = appointments.filter(organization=request.organization)
        serializer = AppointmentListSerializer(appointments, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """Obtiene estadísticas de citas"""
        stats = get_appointments_stats()
        return Response(stats)
    
    @action(detail=True, methods=['patch'])
    def change_status(self, request, pk=None):
        """Cambia el estado de una cita"""
        appointment = self.get_object()
        new_status = request.data.get('status')
        
        if new_status not in dict(Appointment.STATUS_CHOICES):
            return Response(
                {'error': 'Estado inválido'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        appointment.status = new_status
        appointment.save()
        
        serializer = self.get_serializer(appointment)
        return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def available_dates(request):
    """
    API pública para obtener fechas disponibles
    Endpoint: /api/appointments/available-dates/?organization_id=1
    """
    from apps.organizations.models import Organization
    from .models import SpecificDateSchedule, BlockedDate, WorkingHours, AppointmentConfiguration
    from django.utils import timezone
    from datetime import timedelta
    
    try:
        # Usar request.GET en lugar de query_params para compatibilidad
        org_id = request.GET.get('organization_id') if hasattr(request, 'GET') else request.query_params.get('organization_id')
        
        if not org_id:
            return Response({'dates': [], 'error': 'El parámetro "organization_id" es requerido'})
        
        try:
            organization = Organization.objects.get(id=org_id, is_active=True)
        except Organization.DoesNotExist:
            return Response({'dates': [], 'error': 'Organización no encontrada'})
    except Exception as e:
        return Response({'dates': [], 'error': 'Error al procesar la solicitud'})
    
    # Obtener configuración
    try:
        config = AppointmentConfiguration.get_config(organization)
        if not config.is_open:
            return Response({'dates': [], 'message': 'Sistema de citas cerrado'})
        
        # Usar fecha local de Colombia en lugar de UTC
        import pytz
        local_tz = pytz.timezone('America/Bogota')
        today = timezone.now().astimezone(local_tz).date()
        doctor_id = request.GET.get('doctor_id') if hasattr(request, 'GET') else request.query_params.get('doctor_id')
        
        # Generar fechas basadas en horarios regulares
        available_dates = []
        max_days = config.advance_booking_days
        
        # Obtener horarios regulares activos
        working_hours = WorkingHours.objects.filter(
            organization=organization,
            is_active=True
        ).values_list('day_of_week', flat=True)
        
        working_days = set(working_hours)
        
        # Generar fechas para los próximos N días
        for i in range(max_days + 1):
            current_date = today + timedelta(days=i)
            
            # Verificar si es día laborable
            if current_date.weekday() in working_days:
                # Verificar si no está bloqueada
                is_blocked = BlockedDate.objects.filter(
                    organization=organization,
                    date=current_date
                ).exists()
                
                if not is_blocked:
                    available_dates.append(str(current_date))
        
        # También agregar fechas específicas (por si hay horarios especiales)
        filters = {
            'organization': organization,
            'date__gte': today,
            'is_active': True
        }
        
        if doctor_id:
            from django.db.models import Q
            specific_dates = SpecificDateSchedule.objects.filter(
                Q(doctor_profile_id=doctor_id) | Q(doctor_id=doctor_id) | Q(doctor_profile__isnull=True, doctor__isnull=True),
                **filters
            ).values_list('date', flat=True).distinct()
        else:
            specific_dates = SpecificDateSchedule.objects.filter(**filters).values_list('date', flat=True).distinct()
        
        # Agregar fechas específicas que no estén ya en la lista
        for date in specific_dates:
            date_str = str(date)
            if date_str not in available_dates:
                is_blocked = BlockedDate.objects.filter(
                    organization=organization,
                    date=date
                ).exists()
                if not is_blocked:
                    available_dates.append(date_str)
        
        # Ordenar fechas
        available_dates.sort()
        
        return Response({'dates': available_dates})
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error en available_dates: {str(e)}", exc_info=True)
        return Response({'dates': [], 'error': 'Error al cargar las fechas'})


@api_view(['GET'])
@permission_classes([AllowAny])
def available_slots(request):
    """
    API pública para obtener horarios disponibles de una fecha
    Endpoint: /api/appointments/available-slots/?date=2025-12-01&organization_id=1
    """
    from apps.organizations.models import Organization
    
    try:
        # Usar request.GET para compatibilidad
        date_str = request.GET.get('date') if hasattr(request, 'GET') else request.query_params.get('date')
        org_id = request.GET.get('organization_id') if hasattr(request, 'GET') else request.query_params.get('organization_id')
        
        if not date_str:
            return Response({'slots': [], 'error': 'El parámetro "date" es requerido'})
        
        if not org_id:
            return Response({'slots': [], 'error': 'El parámetro "organization_id" es requerido'})
        
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            return Response({'slots': [], 'error': 'Formato de fecha inválido. Use YYYY-MM-DD'})
        
        try:
            organization = Organization.objects.get(id=org_id, is_active=True)
        except Organization.DoesNotExist:
            return Response({'slots': [], 'error': 'Organización no encontrada'})
        
        # Obtener doctor_id si está presente
        doctor_id = request.GET.get('doctor_id') if hasattr(request, 'GET') else request.query_params.get('doctor_id')
        
        # Obtener solo_disponibles si está presente (por defecto True para modales)
        only_available_param = request.GET.get('only_available', 'true') if hasattr(request, 'GET') else request.query_params.get('only_available', 'true')
        only_available = only_available_param.lower() == 'true'
        
        slots = get_available_slots_for_date(date, organization, doctor_id, only_available)
        serializer = AvailableSlotsSerializer(slots, many=True)
        
        return Response({
            'date': date,
            'slots': serializer.data
        })
    
    except Exception as e:
        import logging
        logger = logging.getLogger(__name__)
        logger.error(f"Error en available_slots: {str(e)}", exc_info=True)
        return Response({'slots': [], 'error': 'Error al cargar los horarios'})


@api_view(['POST'])
@permission_classes([AllowAny])
def book_appointment(request):
    """
    API pública para agendar cita desde landing page
    Endpoint: /api/appointments/book/
    
    Body:
    {
        "full_name": "Juan Pérez",
        "phone_number": "3001234567",
        "appointment_date": "2025-12-01",
        "appointment_time": "10:00:00",
        "organization_id": 1
    }
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        serializer = AppointmentCreateSerializer(data=request.data)
        
        if serializer.is_valid():
            appointment = serializer.save()
            
            # Crear notificación push para el dashboard
            try:
                from apps.appointments.models_notifications import AppointmentNotification
                AppointmentNotification.objects.create(
                    appointment=appointment,
                    organization=appointment.organization,
                    created_from_landing=True,
                    is_notified=False
                )
                logger.info(f"Notificación push creada para cita {appointment.id}")
            except Exception as e:
                logger.error(f"Error creando notificación push: {e}")
            
            # Las notificaciones WhatsApp/Email se envían automáticamente por el signal post_save
            # Ver: apps/appointments/signals_setup.py
            
            return Response({
                'success': True,
                'message': '¡Cita agendada exitosamente! Te enviaremos una confirmación.',
                'appointment': {
                    'id': appointment.id,
                    'full_name': appointment.full_name,
                    'date': appointment.appointment_date,
                    'time': appointment.appointment_time,
                    'status': appointment.status
                }
            }, status=status.HTTP_201_CREATED)
        
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Exception as e:
        logger.error(f"Error en book_appointment: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'error': 'Error interno del servidor',
            'detail': str(e) if request.user.is_authenticated else 'Por favor contacta al administrador'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def configuration(request):
    """Obtiene la configuración del sistema"""
    try:
        if not hasattr(request, 'organization') or not request.organization:
            # Devolver configuración por defecto en lugar de error
            return Response({
                'is_open': False,
                'error': 'No hay organización activa'
            })
        
        config = AppointmentConfiguration.get_config(request.organization)
        serializer = AppointmentConfigurationSerializer(config)
        return Response(serializer.data)
    except Exception as e:
        # Devolver configuración por defecto en caso de error
        return Response({
            'is_open': False,
            'error': 'Error al obtener configuración'
        })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def toggle_system(request):
    """Abre o cierra el sistema de agendamiento"""
    if not hasattr(request, 'organization') or not request.organization:
        return Response({'error': 'No hay organización activa'}, status=status.HTTP_400_BAD_REQUEST)
    
    config = AppointmentConfiguration.get_config(request.organization)
    config.is_open = not config.is_open
    config.save()
    
    serializer = AppointmentConfigurationSerializer(config)
    return Response({
        'success': True,
        'message': f'Sistema {"abierto" if config.is_open else "cerrado"}',
        'config': serializer.data
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def block_date(request):
    """Bloquea una fecha específica"""
    date_str = request.data.get('date')
    reason = request.data.get('reason', 'Bloqueado por administrador')
    
    if not date_str:
        return Response(
            {'error': 'La fecha es requerida'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {'error': 'Formato de fecha inválido'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not hasattr(request, 'organization') or not request.organization:
        return Response({'error': 'No hay organización activa'}, status=status.HTTP_400_BAD_REQUEST)
    
    blocked, created = BlockedDate.objects.get_or_create(
        date=date,
        organization=request.organization,
        defaults={
            'reason': reason,
            'created_by': request.user
        }
    )
    
    if not created:
        return Response(
            {'message': 'Esta fecha ya estaba bloqueada'},
            status=status.HTTP_200_OK
        )
    
    serializer = BlockedDateSerializer(blocked)
    return Response({
        'success': True,
        'message': 'Fecha bloqueada exitosamente',
        'blocked_date': serializer.data
    }, status=status.HTTP_201_CREATED)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def block_slot(request):
    """Bloquea un horario específico"""
    date_str = request.data.get('date')
    time_str = request.data.get('time')
    reason = request.data.get('reason', 'Bloqueado manualmente')
    
    if not date_str or not time_str:
        return Response(
            {'error': 'Fecha y hora son requeridas'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
        time_obj = datetime.strptime(time_str, '%H:%M:%S').time()
    except ValueError:
        return Response(
            {'error': 'Formato inválido'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if not hasattr(request, 'organization') or not request.organization:
        return Response({'error': 'No hay organización activa'}, status=status.HTTP_400_BAD_REQUEST)
    
    slot, created = TimeSlot.objects.get_or_create(
        date=date,
        time=time_obj,
        organization=request.organization,
        defaults={
            'is_available': False,
            'manually_blocked': True,
            'blocked_reason': reason
        }
    )
    
    if not created:
        slot.manually_blocked = True
        slot.is_available = False
        slot.blocked_reason = reason
        slot.save()
    
    return Response({
        'success': True,
        'message': 'Horario bloqueado exitosamente'
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def book_patient_appointment(request):
    """
    API para agendar cita desde el dashboard con paciente existente
    Endpoint: /api/appointments/book-patient/
    
    Body:
    {
        "patient_id": 1,
        "appointment_date": "2025-12-01",
        "appointment_time": "10:00:00",
        "phone": "3001234567",
        "email": "paciente@email.com",
        "notes": "Notas opcionales",
        "doctor_id": 1  // Opcional
    }
    """
    import logging
    logger = logging.getLogger(__name__)
    
    try:
        if not hasattr(request, 'organization') or not request.organization:
            return Response({
                'success': False,
                'message': 'No hay organización activa'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        patient_id = request.data.get('patient_id')
        appointment_date = request.data.get('appointment_date')
        appointment_time = request.data.get('appointment_time')
        phone = request.data.get('phone')
        email = request.data.get('email', '')
        notes = request.data.get('notes', '')
        doctor_id = request.data.get('doctor_id', None)
        
        # Debug logs
        logger.info(f"book_patient_appointment called with doctor_id: {doctor_id}")
        logger.info(f"Full request data: {request.data}")
        
        # Validar campos requeridos
        if not all([patient_id, appointment_date, appointment_time, phone]):
            return Response({
                'success': False,
                'message': 'Faltan campos requeridos'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Obtener el paciente
        try:
            patient = Patient.objects.get(
                id=patient_id,
                organization=request.organization
            )
        except Patient.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Paciente no encontrado'
            }, status=status.HTTP_404_NOT_FOUND)
        
        # Obtener el doctor si se especifica
        doctor = None
        if doctor_id:
            try:
                from apps.patients.models import Doctor
                doctor = Doctor.objects.get(
                    id=doctor_id,
                    organization=request.organization
                )
            except Doctor.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Doctor no encontrado'
                }, status=status.HTTP_404_NOT_FOUND)
        
        # Verificar que el horario esté disponible
        existing = Appointment.objects.filter(
            organization=request.organization,
            appointment_date=appointment_date,
            appointment_time=appointment_time
        ).exclude(status='cancelled').exists()
        
        if existing:
            return Response({
                'success': False,
                'message': 'Este horario ya está ocupado'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Crear la cita
        appointment = Appointment.objects.create(
            organization=request.organization,
            patient=patient,
            doctor=doctor,
            full_name=patient.full_name,
            phone_number=phone,
            email=email,
            appointment_date=appointment_date,
            appointment_time=appointment_time,
            notes=notes,
            status='pending'
        )
        
        logger.info(f"Appointment created with ID: {appointment.id}, Doctor: {appointment.doctor}")
        
        # Enviar notificación (no fallar si hay error)
        try:
            from apps.appointments.signals import notify_new_appointment
            notify_new_appointment(appointment)
        except Exception as e:
            logger.error(f"Error enviando notificación: {e}")
        
        return Response({
            'success': True,
            'message': f'Cita agendada exitosamente para {patient.full_name}',
            'appointment': {
                'id': appointment.id,
                'date': str(appointment.appointment_date),
                'time': str(appointment.appointment_time),
                'status': appointment.status
            }
        }, status=status.HTTP_201_CREATED)
        
    except Exception as e:
        logger.error(f"Error en book_patient_appointment: {str(e)}", exc_info=True)
        return Response({
            'success': False,
            'message': f'Error al crear cita: {str(e)}'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
