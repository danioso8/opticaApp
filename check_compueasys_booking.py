import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opticaapp.settings')
django.setup()

from apps.appointments.models import DoctorSchedule
from apps.organizations.models import Organization

try:
    org = Organization.objects.get(slug='compueasys')
    print(f"✅ Organización encontrada: {org.name} (ID: {org.id})")
    
    schedules = DoctorSchedule.objects.filter(doctor__organization=org)
    print(f"\n📅 Schedules encontrados: {schedules.count()}")
    
    for s in schedules:
        print(f"  - Doctor: {s.doctor.user.get_full_name()}")
        print(f"    Día: {s.day_of_week}, Inicio: {s.start_time}, Fin: {s.end_time}")
        print()
        
except Organization.DoesNotExist:
    print("❌ No se encontró la organización 'compueasys'")
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
