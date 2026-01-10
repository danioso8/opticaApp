from apps.organizations.models import Organization
from apps.appointments.models import WorkingHours, SpecificDateSchedule

orgs = Organization.objects.filter(name__icontains='OCÉANO')
if orgs.exists():
    for org in orgs:
        print(f"=== {org.name} ===")
        print(f"ID: {org.id}")
        regular_hours = WorkingHours.objects.filter(organization=org)
        print(f"Horarios Regulares: {regular_hours.count()}")
        for wh in regular_hours:
            print(f"  {wh.get_day_display()}: {wh.start_time} - {wh.end_time} - Activo: {wh.is_active}")
        specific_schedules = SpecificDateSchedule.objects.filter(organization=org)
        print(f"Horarios Específicos: {specific_schedules.count()}")
        for ss in specific_schedules:
            print(f"  {ss.date}: {ss.start_time} - {ss.end_time} - Activo: {ss.is_active}")
else:
    print("No encontrado")
