import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization

orgs = Organization.objects.filter(is_active=True)
print("\nOrganizaciones activas:")
print("-" * 60)
for org in orgs:
    print(f"ID: {org.id:3d} | Nombre: {org.name:30s} | Slug: {org.slug}")
print("-" * 60)

# Verificar específicamente Oceano Optico
oceano = Organization.objects.filter(name__icontains='oceano').first()
if oceano:
    print(f"\nOceano Optico encontrado:")
    print(f"  ID: {oceano.id}")
    print(f"  Nombre: {oceano.name}")
    print(f"  Slug: {oceano.slug}")
    print(f"  Activo: {oceano.is_active}")
