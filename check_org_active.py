from apps.organizations.models import Organization

org = Organization.objects.get(id=4)
print(f"Organización: {org.name}")
print(f"Activa: {org.is_active}")
print(f"ID: {org.id}")
