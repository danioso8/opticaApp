import os
import sys
import django

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization
from apps.appointments.models import SpecificDateSchedule
from datetime import date

print("="*70)
print("VERIFICANDO ORGANIZACIONES DUPLICADAS - COMPUEASYS")
print("="*70)

# Buscar todas las organizaciones con "compu"
orgs = Organization.objects.filter(name__icontains='compu')

print(f"\nTotal encontradas: {orgs.count()}\n")

for org in orgs:
    print(f"{'='*70}")
    print(f"ID: {org.id}")
    print(f"Nombre: {org.name}")
    print(f"Slug: {org.slug}")
    print(f"Activa: {org.is_active}")
    print(f"Creada: {org.created_at}")
    
    # Contar fechas disponibles
    today = date.today()
    dates = SpecificDateSchedule.objects.filter(
        organization=org,
        date__gte=today,
        is_active=True
    ).count()
    
    print(f"Fechas disponibles: {dates}")
    
    # Contar usuarios/miembros
    if hasattr(org, 'userprofile_set'):
        users = org.userprofile_set.count()
        print(f"Usuarios: {users}")
    
    print()

# Verificar si hay duplicados exactos
print("="*70)
print("ANÁLISIS DE DUPLICADOS")
print("="*70)

compueasys_orgs = Organization.objects.filter(name__iexact='compueasys')
print(f"\nOrganizaciones con nombre exacto 'CompuEasys': {compueasys_orgs.count()}")

if compueasys_orgs.count() > 1:
    print("\n❌ HAY DUPLICADOS!")
    print("\nDetalles:")
    for org in compueasys_orgs:
        print(f"  - ID {org.id}: slug='{org.slug}', activa={org.is_active}, creada={org.created_at.strftime('%Y-%m-%d %H:%M')}")
else:
    print("\n✅ No hay duplicados con nombre exacto 'CompuEasys'")

print("\n" + "="*70)
