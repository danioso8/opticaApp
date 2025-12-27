"""Actualizar el logo de Oceano Optico SJ"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import LandingPageConfig

# Obtener la configuración de Oceano Optico SJ
oceano_config = LandingPageConfig.objects.get(id=1)

print(f"\n{'='*80}")
print("Configuración actual de Oceano Optico SJ:")
print(f"{'='*80}\n")
print(f"Organización: {oceano_config.organization.name}")
print(f"Logo actual: {oceano_config.logo}")
print(f"Hero Title: {oceano_config.hero_title}")

# Limpiar el logo para que use el del navbar por defecto
print(f"\n{'='*80}")
print("Actualizando configuración...")
print(f"{'='*80}\n")

# Opción 1: Limpiar el logo para que use el logo por defecto del navbar (ícono)
oceano_config.logo = None
oceano_config.save()

print("✓ Logo limpiado. Ahora usará el ícono por defecto del navbar.")
print(f"\nLogo después de actualizar: {oceano_config.logo}")

print(f"\n{'='*80}\n")
