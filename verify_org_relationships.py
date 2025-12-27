"""Verificar relaciones entre organizaciones y landing pages"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization, LandingPageConfig

print(f"\n{'='*80}")
print("VERIFICACIÓN DE RELACIONES ORGANIZACIÓN - LANDING PAGE")
print(f"{'='*80}\n")

# Verificar Oceano Optico SJ
print("1. OCEANO OPTICO SJ:")
print("-" * 80)
oceano = Organization.objects.get(slug='oceano-optico-sj')
print(f"   ID: {oceano.id}")
print(f"   Nombre: {oceano.name}")
print(f"   Slug: {oceano.slug}")

try:
    oceano_landing = LandingPageConfig.objects.get(organization=oceano)
    print(f"\n   Landing Page Config:")
    print(f"   - Config ID: {oceano_landing.id}")
    print(f"   - Organización en config: {oceano_landing.organization.name}")
    print(f"   - Organización ID en config: {oceano_landing.organization_id}")
    print(f"   - Hero Title: {oceano_landing.hero_title}")
except LandingPageConfig.DoesNotExist:
    print("   ✗ NO tiene LandingPageConfig")

# Verificar CompuEasys
print(f"\n\n2. COMPUEASYS:")
print("-" * 80)
try:
    compueasys = Organization.objects.get(slug='compueasys')
    print(f"   ID: {compueasys.id}")
    print(f"   Nombre: {compueasys.name}")
    print(f"   Slug: {compueasys.slug}")
    
    try:
        compueasys_landing = LandingPageConfig.objects.get(organization=compueasys)
        print(f"\n   Landing Page Config:")
        print(f"   - Config ID: {compueasys_landing.id}")
        print(f"   - Organización en config: {compueasys_landing.organization.name}")
        print(f"   - Organización ID en config: {compueasys_landing.organization_id}")
        print(f"   - Hero Title: {compueasys_landing.hero_title}")
    except LandingPageConfig.DoesNotExist:
        print("   ✗ NO tiene LandingPageConfig")
except Organization.DoesNotExist:
    print("   ✗ NO existe esta organización")

# Verificar si hay configuraciones huérfanas o duplicadas
print(f"\n\n3. VERIFICACIÓN DE INTEGRIDAD:")
print("-" * 80)

all_configs = LandingPageConfig.objects.all()
print(f"\nTotal de LandingPageConfigs: {all_configs.count()}")

for config in all_configs:
    print(f"\n   Config ID {config.id}:")
    print(f"   - organization_id: {config.organization_id}")
    print(f"   - organization.name: {config.organization.name}")
    print(f"   - organization.slug: {config.organization.slug}")
    
    # Verificar si la organización existe
    try:
        org_exists = Organization.objects.get(id=config.organization_id)
        print(f"   - ✓ Organización existe")
    except Organization.DoesNotExist:
        print(f"   - ✗ Organización HUÉRFANA!")

# Verificar si hay organizaciones con múltiples configs (no debería pasar)
print(f"\n\n4. VERIFICACIÓN DE DUPLICADOS:")
print("-" * 80)

for org in Organization.objects.all():
    configs_count = LandingPageConfig.objects.filter(organization=org).count()
    if configs_count > 1:
        print(f"   ✗ {org.name} tiene {configs_count} configs (debería tener 1)")
    elif configs_count == 1:
        print(f"   ✓ {org.name} tiene 1 config")
    else:
        print(f"   - {org.name} no tiene config")

print(f"\n{'='*80}\n")
