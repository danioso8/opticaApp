from apps.organizations.models import Organization
from apps.appointments.models import AppointmentConfiguration

orgs = Organization.objects.filter(name__icontains='OCÉANO')
if orgs.exists():
    org = orgs.first()
    print(f"=== {org.name} ===")
    config = AppointmentConfiguration.get_config(org)
    print(f"Sistema abierto: {config.is_open}")
    print(f"Días adelante: {config.days_in_advance}")
    print(f"Duración cita: {config.slot_duration} min")
    print(f"Requiere registro: {config.require_account}")
else:
    print("No encontrado")
