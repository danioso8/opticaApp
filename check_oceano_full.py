from apps.organizations.models import Organization
from apps.appointments.models import AppointmentConfiguration, WorkingHours
from datetime import date

org = Organization.objects.get(id=4)
print(f"=== {org.name} ===")

config = AppointmentConfiguration.get_config(org)
print(f"\nCONFIGURACION:")
print(f"  Abierto: {config.is_open}")
print(f"  Dias adelante: {config.advance_booking_days}")
print(f"  Duracion: {config.slot_duration} min")

hours = WorkingHours.objects.filter(organization=org, is_active=True).order_by('day_of_week')
print(f"\nHORARIOS ({hours.count()}):")
for h in hours:
    print(f"  {h.get_day_of_week_display()}: {h.start_time}-{h.end_time}")
