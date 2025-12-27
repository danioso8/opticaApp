"""Verificar qué logo se está mostrando para cada organización"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization, LandingPageConfig
from django.shortcuts import get_object_or_404

# Simular la vista organization_landing para oceano-optico-sj
org_slug = 'oceano-optico-sj'
organization = get_object_or_404(Organization, slug=org_slug, is_active=True)

print(f"\n{'='*80}")
print(f"Organización obtenida por slug '{org_slug}':")
print(f"{'='*80}\n")
print(f"ID: {organization.id}")
print(f"Nombre: {organization.name}")
print(f"Slug: {organization.slug}")

# Obtener configuración de la landing page
landing_config = None
try:
    landing_config = LandingPageConfig.objects.get(organization=organization)
    print(f"\n{'='*80}")
    print("LandingPageConfig asociada:")
    print(f"{'='*80}\n")
    print(f"ID Config: {landing_config.id}")
    print(f"Organización en Config: {landing_config.organization.name}")
    print(f"Organización ID en Config: {landing_config.organization.id}")
    print(f"Hero Title: {landing_config.hero_title}")
    print(f"Logo Path: {landing_config.logo}")
    if landing_config.logo:
        print(f"Logo URL: {landing_config.logo.url}")
except LandingPageConfig.DoesNotExist:
    print("\n✗ NO se encontró LandingPageConfig para esta organización")

print(f"\n{'='*80}\n")

# Verificar también el contexto que se pasaría al template
context = {
    'organization_data': organization,
    'landing_config': landing_config,
    'org_slug': org_slug,
}

print("Contexto que se pasaría al template:")
print(f"organization_data.name: {context['organization_data'].name}")
print(f"landing_config.hero_title: {context['landing_config'].hero_title if context['landing_config'] else 'None'}")
print(f"landing_config.logo: {context['landing_config'].logo if context['landing_config'] else 'None'}")
