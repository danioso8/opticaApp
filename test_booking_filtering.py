"""Simular la vista booking con org_slug"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization
from apps.appointments.models import SpecificDateSchedule
from django.utils import timezone

org_slug = 'oceano-optico-sj'

print(f"\n{'='*80}")
print(f"Simulando booking con org_slug='{org_slug}'")
print(f"{'='*80}\n")

try:
    specific_org = Organization.objects.get(slug=org_slug, is_active=True)
    print(f"✓ Organización encontrada:")
    print(f"  - ID: {specific_org.id}")
    print(f"  - Nombre: {specific_org.name}")
    
    today = timezone.now().date()
    
    # Verificar horarios
    schedules = SpecificDateSchedule.objects.filter(
        date__gte=today,
        is_active=True,
        organization=specific_org
    )
    
    print(f"\n  Horarios configurados: {schedules.count()}")
    
    if schedules.exists():
        print(f"  ✓ Tiene horarios configurados")
        
        # Obtener organizaciones disponibles (debería ser solo una)
        available_organizations = Organization.objects.filter(id=specific_org.id)
        
        print(f"\n  Organizaciones disponibles para agendar:")
        for org in available_organizations:
            print(f"    - {org.name} (ID: {org.id}, slug: {org.slug})")
        
        print(f"\n  Total organizaciones: {available_organizations.count()}")
        
        if available_organizations.count() == 1:
            print(f"\n  ✓ ¡CORRECTO! Solo se muestra 1 organización")
        else:
            print(f"\n  ✗ ERROR: Se muestran {available_organizations.count()} organizaciones")
    else:
        print(f"  ✗ NO tiene horarios configurados")
        print(f"  Resultado: available_organizations será vacío")

except Organization.DoesNotExist:
    print(f"✗ Organización no encontrada con slug '{org_slug}'")

print(f"\n{'='*80}")

# Ahora verificar qué pasa sin org_slug (modo normal)
print(f"\n{'='*80}")
print("Simulando booking SIN org_slug (modo normal)")
print(f"{'='*80}\n")

today = timezone.now().date()

orgs_with_schedules = SpecificDateSchedule.objects.filter(
    date__gte=today,
    is_active=True
).values_list('organization_id', flat=True).distinct()

available_organizations = Organization.objects.filter(
    id__in=orgs_with_schedules,
    is_active=True
).order_by('name')

print(f"Organizaciones disponibles (todas las públicas):")
for org in available_organizations:
    print(f"  - {org.name} (ID: {org.id}, slug: {org.slug})")

print(f"\nTotal: {available_organizations.count()} organizaciones")

print(f"\n{'='*80}\n")
