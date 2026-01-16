from apps.core.models import User
from apps.organizations.models import Organization
from apps.appointments.models import SpecificDateSchedule, AppointmentConfiguration
from datetime import date, timedelta

# Usuario danioso8329
user = User.objects.filter(username='danioso8329').first()
if user and hasattr(user, 'userprofile') and user.userprofile:
    org = user.userprofile.organization
    print(f"Usuario: {user.username}")
    print(f"Org: {org.name if org else 'NO TIENE'} (ID: {org.id if org else 'N/A'})")
    print(f"Slug: {org.slug if org else 'N/A'}")
    
    if org:
        # Config
        config = AppointmentConfiguration.objects.filter(organization=org).first()
        print(f"\nConfig: {'Existe' if config else 'NO EXISTE'}")
        if config:
            print(f"  Abierto: {config.is_open}")
        
        # Fechas específicas
        today = date.today()
        dates = SpecificDateSchedule.objects.filter(
            organization=org,
            date__gte=today,
            is_active=True
        ).count()
        print(f"SpecificDateSchedule: {dates} fechas disponibles")
        
        if dates == 0:
            print("❌ PROBLEMA: NO hay fechas específicas configuradas")
            print("   Por eso muestra 'error al cargar las fechas'")

# Oceano Optico
oceano = Organization.objects.filter(slug='oceano-optico').first()
if oceano:
    print(f"\n--- OCEANO OPTICO ---")
    dates_oceano = SpecificDateSchedule.objects.filter(
        organization=oceano,
        date__gte=today,
        is_active=True
    ).count()
    print(f"Fechas disponibles: {dates_oceano}")
