from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from apps.appointments.models import AppointmentConfiguration, WorkingHours
from apps.appointments.utils import get_available_slots_for_date


def home(request):
    """Página principal pública"""
    # Para vistas públicas, usar la organización del request si existe, sino la primera disponible
    organization = getattr(request, 'organization', None)
    config = AppointmentConfiguration.get_config(organization)
    
    context = {
        'system_open': config.is_open if config else True,
    }
    
    return render(request, 'public/home.html', context)


def booking(request):
    """Página de agendamiento de citas"""
    organization = getattr(request, 'organization', None)
    config = AppointmentConfiguration.get_config(organization)
    
    if not config or not config.is_open:
        context = {
            'system_closed': True,
        }
        return render(request, 'public/booking.html', context)
    
    # Obtener fechas disponibles (solo fechas con horarios específicos configurados)
    from apps.appointments.models import SpecificDateSchedule, BlockedDate
    today = timezone.now().date()
    available_dates = []
    
    # Filtrar por organización si existe
    org_filter = {'organization': organization} if organization else {}
    
    # Obtener todas las fechas específicas configuradas
    specific_dates = SpecificDateSchedule.objects.filter(
        date__gte=today,
        is_active=True,
        **org_filter
    ).values_list('date', flat=True).distinct().order_by('date')
    
    for date in specific_dates:
        # Verificar si no está bloqueado
        is_blocked = BlockedDate.objects.filter(date=date, **org_filter).exists()
        
        if not is_blocked:
            available_dates.append(date)
    
    context = {
        'system_closed': False,
        'available_dates': available_dates,
        'slot_duration': config.slot_duration,
    }
    
    return render(request, 'public/booking.html', context)


def shop(request):
    """Tienda de monturas (placeholder)"""
    context = {}
    return render(request, 'public/shop.html', context)
