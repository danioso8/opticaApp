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
    Endpoint: /api/appointments/available-dates/
    """
    days = int(request.query_params.get('days', 30))
    dates = get_available_dates(days_ahead=days)
    serializer = AvailableDatesSerializer(dates, many=True)
    return Response(serializer.data)


@api_view(['GET'])
@permission_classes([AllowAny])
def available_slots(request):
    """
    API pública para obtener horarios disponibles de una fecha
    Endpoint: /api/appointments/available-slots/?date=2025-12-01
    """
    date_str = request.query_params.get('date')
    
    if not date_str:
        return Response(
            {'error': 'El parámetro "date" es requerido'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return Response(
            {'error': 'Formato de fecha inválido. Use YYYY-MM-DD'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    slots = get_available_slots_for_date(date)
    serializer = AvailableSlotsSerializer(slots, many=True)
    
    return Response({
        'date': date,
        'slots': serializer.data
    })


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
        "appointment_time": "10:00:00"
    }
    """
    serializer = AppointmentCreateSerializer(data=request.data)
    
    if serializer.is_valid():
        appointment = serializer.save()
        
        # Aquí se puede agregar lógica para enviar SMS/Email de confirmación
        
        return Response({
            'success': True,
            'message': '¡Cita agendada exitosamente!',
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


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def configuration(request):
    """Obtiene la configuración del sistema"""
    if not hasattr(request, 'organization') or not request.organization:
        return Response({'error': 'No hay organización activa'}, status=status.HTTP_400_BAD_REQUEST)
    
    config = AppointmentConfiguration.get_config(request.organization)
    serializer = AppointmentConfigurationSerializer(config)
    return Response(serializer.data)


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
