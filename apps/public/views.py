from django.shortcuts import render
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from apps.appointments.models import AppointmentConfiguration, WorkingHours
from apps.appointments.utils import get_available_slots_for_date


def home(request):
    """Página principal pública - Redirige a landing de organización si está autenticado, sino muestra landing genérica"""
    from django.shortcuts import redirect
    from apps.organizations.models import OrganizationMember
    
    # Si el usuario está autenticado, redirigir a su landing page específica
    if request.user.is_authenticated:
        first_membership = OrganizationMember.objects.filter(
            user=request.user,
            is_active=True
        ).select_related('organization').first()
        
        if first_membership and first_membership.organization.slug:
            # Redirigir a la landing page específica de su organización
            return redirect('public:organization_landing', org_slug=first_membership.organization.slug)
    
    # Si no está autenticado, mostrar landing page genérica del sistema
    return render(request, 'public/home_generic.html')


def organization_landing(request, org_slug):
    """Landing page específica de una organización por su slug"""
    from apps.organizations.models import LandingPageConfig, Organization
    from django.shortcuts import get_object_or_404
    
    # Obtener la organización por su slug
    organization = get_object_or_404(Organization, slug=org_slug, is_active=True)
    
    config = AppointmentConfiguration.get_config(organization)
    
    # Obtener configuración de la landing page
    landing_config = None
    try:
        landing_config = LandingPageConfig.objects.get(organization=organization)
    except LandingPageConfig.DoesNotExist:
        pass
    
    context = {
        'system_open': config.is_open if config else True,
        'organization_data': organization,
        'landing_config': landing_config,
        'org_slug': org_slug,
    }
    
    return render(request, 'public/organization_landing.html', context)


def booking(request, org_slug=None):
    """Página de agendamiento de citas"""
    from apps.organizations.models import Organization, LandingPageConfig
    from django.contrib.auth.models import Group
    
    # Obtener todas las organizaciones con horarios disponibles
    first_organization = None
    available_organizations = Organization.objects.none()
    
    from apps.appointments.models import SpecificDateSchedule
    import pytz
    from django.conf import settings
    
    # Obtener fecha local de Colombia
    colombia_tz = pytz.timezone(settings.TIME_ZONE)
    today = timezone.now().astimezone(colombia_tz).date()
    
    if request.user.is_authenticated:
        from apps.organizations.models import OrganizationMember
        
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
        # Si no está autenticado, obtener todas las organizaciones públicas con horarios
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
    
    # Si no hay organización del usuario autenticado, usar la del org_slug si existe
    if not first_organization and org_slug:
        try:
            first_organization = Organization.objects.get(slug=org_slug, is_active=True)
        except Organization.DoesNotExist:
            first_organization = Organization.objects.filter(is_active=True).first()
    elif not first_organization:
        # Solo como último recurso, obtener la primera organización activa
        first_organization = Organization.objects.filter(is_active=True).first()
    
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
        'org_slug': org_slug,  # Pasar org_slug al contexto
    }
    
    return render(request, 'public/booking.html', context)


def shop(request):
    """Tienda de monturas (placeholder)"""
    from apps.organizations.models import LandingPageConfig, Organization
    
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
    
    # Si no hay organización del usuario autenticado, obtener la primera organización activa
    if not first_organization:
        first_organization = Organization.objects.filter(is_active=True).first()
    
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
