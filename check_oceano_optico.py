"""Script para verificar la configuración de Oceano Optico SJ"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization, LandingPageConfig

# Buscar la organización
org_slug = 'oceano-optico-sj'
print(f"\n{'='*60}")
print(f"Buscando organización con slug: {org_slug}")
print(f"{'='*60}\n")

try:
    org = Organization.objects.get(slug=org_slug)
    print(f"✓ Organización encontrada:")
    print(f"  - ID: {org.id}")
    print(f"  - Nombre: {org.name}")
    print(f"  - Slug: {org.slug}")
    print(f"  - Activa: {org.is_active}")
    print(f"  - Email: {org.email}")
    
    # Verificar configuración de landing page
    print(f"\n{'='*60}")
    print("Verificando LandingPageConfig...")
    print(f"{'='*60}\n")
    
    try:
        landing_config = LandingPageConfig.objects.get(organization=org)
        print(f"✓ LandingPageConfig encontrada:")
        print(f"  - ID: {landing_config.id}")
        print(f"  - Organización: {landing_config.organization.name}")
        print(f"  - Hero Title: {landing_config.hero_title}")
        print(f"  - Logo: {landing_config.logo}")
    except LandingPageConfig.DoesNotExist:
        print("✗ NO se encontró LandingPageConfig para esta organización")
        print("\nVerificando si hay otras LandingPageConfig...")
        
        all_configs = LandingPageConfig.objects.all()
        if all_configs.exists():
            print(f"\nSe encontraron {all_configs.count()} configuraciones:")
            for config in all_configs:
                print(f"  - Organización: {config.organization.name} (slug: {config.organization.slug})")
        else:
            print("No hay ninguna LandingPageConfig en la base de datos")
    
except Organization.DoesNotExist:
    print(f"✗ NO se encontró organización con slug '{org_slug}'")
    print("\nOrganizaciones disponibles:")
    
    all_orgs = Organization.objects.all()
    if all_orgs.exists():
        for org in all_orgs:
            print(f"  - {org.name} (slug: {org.slug}, activa: {org.is_active})")
    else:
        print("  No hay organizaciones en la base de datos")

print(f"\n{'='*60}\n")
