from apps.appointments.models import Appointment

print("\n=== TODAS LAS CITAS ===\n")
appointments = Appointment.objects.all().select_related('organization')
for apt in appointments:
    org_name = apt.organization.name if apt.organization else "SIN ORGANIZACIÓN"
    print(f"ID: {apt.id} | {apt.full_name} | {apt.appointment_date} | {apt.appointment_time} | Org: {org_name}")

print("\n=== POR ORGANIZACIÓN ===\n")
from apps.organizations.models import Organization
orgs = Organization.objects.all()
for org in orgs:
    count = Appointment.objects.filter(organization=org).count()
    print(f"{org.name}: {count} citas")
