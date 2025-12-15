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
    
    # Si el usuario está autenticado, obtener solo SUS organizaciones
    first_organization = None
    available_organizations = Organization.objects.none()
    
    if request.user.is_authenticated:
        from apps.organizations.models import OrganizationMember
        from apps.appointments.models import SpecificDateSchedule
        today = timezone.now().date()
        
        # Obtener organizaciones del usuario que tienen horarios configurados
        user_org_ids = OrganizationMember.objects.filter(
            user=request.user,
            is_active=True
        ).values_list('organization_id', flat=True)
        
        # Filtrar organizaciones con horarios específicos configurados
        orgs_with_schedules = SpecificDateSchedule.objects.filter(
            date__gte=today,
            is_active=True,
            organization_id__in=user_org_ids  # Solo las del usuario
        ).values_list('organization_id', flat=True).distinct()
        
        available_organizations = Organization.objects.filter(
            id__in=orgs_with_schedules,
            is_active=True
        ).order_by('name')
        
        # Obtener primera organización del usuario
        first_membership = OrganizationMember.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('organization').first()
        
        if first_membership:
            first_organization = first_membership.organization
    else:
        # Si no está autenticado, obtener todas las organizaciones públicas
        from apps.appointments.models import SpecificDateSchedule
        today = timezone.now().date()
        
        orgs_with_schedules = SpecificDateSchedule.objects.filter(
            date__gte=today,
            is_active=True
        ).values_list('organization_id', flat=True).distinct()
        
        available_organizations = Organization.objects.filter(
            id__in=orgs_with_schedules,
            is_active=True
        ).order_by('name')
    
    # Obtener configuración de la landing page
    landing_config = None
    if first_organization:
        try:
            landing_config = LandingPageConfig.objects.get(organization=first_organization)
        except LandingPageConfig.DoesNotExist:
            pass
    
    # Obtener doctores según las organizaciones disponibles
    from apps.patients.models import Doctor
    
    if request.user.is_authenticated and available_organizations.exists():
        # Solo mostrar doctores de las organizaciones del usuario
        org_ids = available_organizations.values_list('id', flat=True)
        available_doctors = Doctor.objects.filter(
            is_active=True,
            organization_id__in=org_ids
        ).values('id', 'full_name')
    else:
        # Para usuarios no autenticados, mostrar doctores de organizaciones públicas
        if available_organizations.exists():
            org_ids = available_organizations.values_list('id', flat=True)
            available_doctors = Doctor.objects.filter(
                is_active=True,
                organization_id__in=org_ids
            ).values('id', 'full_name')
        else:
            available_doctors = Doctor.objects.none()
    
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
