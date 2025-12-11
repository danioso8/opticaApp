"""
Utilidades para el módulo de citas
"""
from datetime import datetime, timedelta, time
from django.utils import timezone
from .models import (
    AppointmentConfiguration,
    WorkingHours,
    BlockedDate,
    Appointment
)


def generate_time_slots(start_time, end_time, duration_minutes=30):
    """
    Genera slots de tiempo entre start_time y end_time
    
    Args:
        start_time: Hora de inicio (time object)
        end_time: Hora de fin (time object)
        duration_minutes: Duración de cada slot en minutos
    
    Returns:
        Lista de time objects
    """
    slots = []
    current = datetime.combine(datetime.today(), start_time)
    end = datetime.combine(datetime.today(), end_time)
    
    while current < end:
        slots.append(current.time())
        current += timedelta(minutes=duration_minutes)
    
    return slots


def get_available_slots_for_date(date, organization=None):
    """
    Obtiene los horarios disponibles para una fecha específica
    
    Args:
        date: Fecha a consultar (date object)
        organization: Organización (opcional)
    
    Returns:
        Lista de diccionarios con información de slots disponibles
    """
    # Verificar configuración
    config = AppointmentConfiguration.get_config(organization)
    if not config or not config.is_open:
        return []
    
    # Filtrar por organización
    org_filter = {'organization': organization} if organization else {}
    
    # Verificar fecha bloqueada
    if BlockedDate.objects.filter(date=date, **org_filter).exists():
        return []
    
    # Verificar si es fecha pasada
    if date < timezone.now().date():
        return []
    
    # Primero verificar si hay horarios específicos para esta fecha
    from .models import SpecificDateSchedule
    specific_schedules = SpecificDateSchedule.objects.filter(
        date=date,
        is_active=True,
        **org_filter
    )
    
    # Si hay horarios específicos, usar esos (ignora WorkingHours)
    if specific_schedules.exists():
        working_hours = specific_schedules
        # Generar todos los slots posibles de horarios específicos
        all_slots = []
        for wh in working_hours:
            # Usar slot_duration específico del horario si existe, sino usar el de configuración
            duration = getattr(wh, 'slot_duration', config.slot_duration)
            slots = generate_time_slots(
                wh.start_time,
                wh.end_time,
                duration
            )
            all_slots.extend(slots)
    else:
        # Si no hay específicos, usar horarios del día de la semana
        day_of_week = date.weekday()
        working_hours = WorkingHours.objects.filter(
            day_of_week=day_of_week,
            is_active=True,
            **org_filter
        )
        
        if not working_hours.exists():
            return []
        
        # Generar todos los slots posibles
        all_slots = []
        for wh in working_hours:
            slots = generate_time_slots(
                wh.start_time,
                wh.end_time,
                config.slot_duration
            )
            all_slots.extend(slots)
    
    # Obtener citas ya agendadas
    booked_appointments = Appointment.objects.filter(
        appointment_date=date,
        **org_filter
    ).exclude(status='cancelled').values_list('appointment_time', flat=True)
    
    # Filtrar slots disponibles
    available_slots = []
    # Obtener hora local en lugar de UTC
    from datetime import datetime
    import pytz
    local_tz = pytz.timezone('America/Bogota')
    current_time = timezone.now().astimezone(local_tz).time()
    is_today = date == timezone.now().date()
    
    for slot in all_slots:
        # Si es hoy, solo mostrar horarios futuros
        if is_today and slot <= current_time:
            continue
        
        is_available = slot not in booked_appointments
        
        available_slots.append({
            'time': slot,
            'available': is_available
        })
    
    return available_slots


def get_available_dates(days_ahead=30, organization=None):
    """
    Obtiene las fechas disponibles para agendar citas
    Prioriza horarios específicos sobre horarios recurrentes
    
    Args:
        days_ahead: Número de días hacia adelante a consultar
        organization: Organización (opcional)
    
    Returns:
        Lista de diccionarios con fechas y disponibilidad
    """
    config = AppointmentConfiguration.get_config(organization)
    if not config or not config.is_open:
        return []
    
    from .models import SpecificDateSchedule
    today = timezone.now().date()
    dates = []
    org_filter = {'organization': organization} if organization else {}
    
    for i in range(days_ahead):
        date = today + timedelta(days=i)
        
        # Verificar si hay horarios específicos para esta fecha
        has_specific = SpecificDateSchedule.objects.filter(
            date=date,
            is_active=True,
            **org_filter
        ).exists()
        
        # Si tiene horarios específicos O si tiene horarios del día de la semana
        slots = get_available_slots_for_date(date, organization)
        
        available_count = sum(1 for slot in slots if slot['available'])
        
        if slots:  # Solo incluir fechas con horarios
            dates.append({
                'date': date,
                'available_slots': available_count,
                'total_slots': len(slots),
                'is_available': available_count > 0,
                'is_specific': has_specific
            })
    
    return dates


def get_appointments_stats(organization=None):
    """
    Obtiene estadísticas de citas
    
    Args:
        organization: Organización (opcional)
    
    Returns:
        Diccionario con estadísticas
    """
    today = timezone.now().date()
    org_filter = {'organization': organization} if organization else {}
    
    # Citas de hoy
    today_appointments = Appointment.objects.filter(appointment_date=today, **org_filter)
    
    stats = {
        'today': {
            'total': today_appointments.count(),
            'pending': today_appointments.filter(status='pending').count(),
            'confirmed': today_appointments.filter(status='confirmed').count(),
            'completed': today_appointments.filter(status='completed').count(),
            'cancelled': today_appointments.filter(status='cancelled').count(),
            'no_show': today_appointments.filter(status='no_show').count(),
        },
        'system_open': AppointmentConfiguration.get_config(organization).is_open if AppointmentConfiguration.get_config(organization) else True,
    }
    
    return stats


def check_slot_availability(date, time, organization=None):
    """
    Verifica si un slot específico está disponible
    
    Args:
        date: Fecha (date object)
        time: Hora (time object)
        organization: Organización (opcional)
    
    Returns:
        Tuple (is_available: bool, reason: str)
    """
    config = AppointmentConfiguration.get_config(organization)
    
    # Sistema cerrado
    if not config.is_open:
        return False, "Sistema de agendamiento cerrado"
    
    # Fecha pasada
    if date < timezone.now().date():
        return False, "Fecha pasada"
    
    # Si es hoy, verificar hora
    if date == timezone.now().date() and time <= timezone.now().time():
        return False, "Hora pasada"
    
    org_filter = {'organization': organization} if organization else {}
    
    # Fecha bloqueada
    if BlockedDate.objects.filter(date=date, **org_filter).exists():
        return False, "Fecha bloqueada"
    
    # Día sin atención
    day_of_week = date.weekday()
    working_hours = WorkingHours.objects.filter(
        day_of_week=day_of_week,
        is_active=True,
        **org_filter
    )
    
    if not working_hours.exists():
        return False, "Sin atención este día"
    
    # Verificar que esté dentro de horario
    in_working_hours = False
    for wh in working_hours:
        if wh.start_time <= time <= wh.end_time:
            in_working_hours = True
            break
    
    if not in_working_hours:
        return False, "Fuera de horario de atención"
    
    # Verificar si ya está ocupado
    if Appointment.objects.filter(
        appointment_date=date,
        appointment_time=time,
        **org_filter
    ).exclude(status='cancelled').exists():
        return False, "Horario ya ocupado"
    
    return True, "Disponible"
