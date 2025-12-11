from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from apps.appointments.models import AppointmentConfiguration, WorkingHours
from apps.appointments.utils import get_available_slots_for_date


def home(request):
    """Página principal pública"""
    from apps.organizations.models import LandingPageConfig
    
    # Para vistas públicas, usar la organización del request si existe, sino la primera disponible
    organization = getattr(request, 'organization', None)
    
    # Si el usuario está autenticado, obtener su primera organización
    first_organization = None
    if request.user.is_authenticated:
        from apps.organizations.models import OrganizationMember
        first_membership = OrganizationMember.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('organization').first()
        
        if first_membership:
            first_organization = first_membership.organization
    
    config = AppointmentConfiguration.get_config(organization or first_organization)
    
    # Obtener configuración de la landing page
    landing_config = None
    if first_organization:
        try:
            landing_config = LandingPageConfig.objects.get(organization=first_organization)
        except LandingPageConfig.DoesNotExist:
            pass
    
    context = {
        'system_open': config.is_open if config else True,
        'organization_data': first_organization,
        'landing_config': landing_config,
    }
    
    return render(request, 'public/home.html', context)


def booking(request):
    """Página de agendamiento de citas"""
    from apps.organizations.models import Organization, LandingPageConfig
    from django.contrib.auth.models import Group
    
    # Obtener todas las organizaciones activas que tienen horarios configurados
    from apps.appointments.models import SpecificDateSchedule
    today = timezone.now().date()
    
    # Obtener organizaciones que tienen horarios específicos configurados
    orgs_with_schedules = SpecificDateSchedule.objects.filter(
        date__gte=today,
        is_active=True
    ).values_list('organization_id', flat=True).distinct()
    
    available_organizations = Organization.objects.filter(
        id__in=orgs_with_schedules,
        is_active=True
    ).order_by('name')
    
    # Si el usuario está autenticado, obtener su primera organización
    first_organization = None
    if request.user.is_authenticated:
        from apps.organizations.models import OrganizationMember
        first_membership = OrganizationMember.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('organization').first()
        
        if first_membership:
            first_organization = first_membership.organization
    
    # Obtener configuración de la landing page
    landing_config = None
    if first_organization:
        try:
            landing_config = LandingPageConfig.objects.get(organization=first_organization)
        except LandingPageConfig.DoesNotExist:
            pass
    
    # Obtener doctores del modelo Doctor
    from apps.patients.models import Doctor
    
    available_doctors = Doctor.objects.filter(
        is_active=True
    ).values('id', 'full_name')
    
    context = {
        'system_closed': False,
        'available_organizations': available_organizations,
        'available_doctors': available_doctors,
        'organization_data': first_organization,
        'landing_config': landing_config,
    }
    
    return render(request, 'public/booking.html', context)


def shop(request):
    """Tienda de monturas (placeholder)"""
    from apps.organizations.models import LandingPageConfig
    
    # Si el usuario está autenticado, obtener su primera organización
    first_organization = None
    if request.user.is_authenticated:
        from apps.organizations.models import OrganizationMember
        first_membership = OrganizationMember.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('organization').first()
        
        if first_membership:
            first_organization = first_membership.organization
    
    # Obtener configuración de la landing page
    landing_config = None
    if first_organization:
        try:
            landing_config = LandingPageConfig.objects.get(organization=first_organization)
        except LandingPageConfig.DoesNotExist:
            pass
    
    context = {
        'organization_data': first_organization,
        'landing_config': landing_config,
    }
    return render(request, 'public/shop.html', context)
