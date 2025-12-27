"""Script para verificar TODAS las configuraciones de landing page"""
import os
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization, LandingPageConfig

print(f"\n{'='*80}")
print("TODAS LAS ORGANIZACIONES Y SUS LANDINGPAGECONFIGS")
print(f"{'='*80}\n")

all_configs = LandingPageConfig.objects.select_related('organization').all()

for config in all_configs:
    print(f"ID Config: {config.id}")
    print(f"Organización: {config.organization.name} (ID: {config.organization.id})")
    print(f"Slug: {config.organization.slug}")
    print(f"Hero Title: {config.hero_title}")
    print(f"Logo Path: {config.logo}")
    if config.logo:
        print(f"Logo URL: {config.logo.url}")
    print("-" * 80)
    print()

print(f"\n{'='*80}\n")
