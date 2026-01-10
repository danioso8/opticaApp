from apps.organizations.models import Organization
for org in Organization.objects.all():
    print(f"{org.id}: {org.name}")
