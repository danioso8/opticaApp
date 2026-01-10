from apps.organizations.models import Organization
from apps.appointments.models import WorkingHours

for org in Organization.objects.all():
    print(f"\nID: {org.id} | Nombre: {org.name}")
    hours = WorkingHours.objects.filter(organization=org, is_active=True)
    print(f"  Horarios activos: {hours.count()}")
