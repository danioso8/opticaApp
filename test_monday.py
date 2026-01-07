import os
os.environ['DJANGO_SETTINGS_MODULE'] = 'config.settings'
import django
django.setup()

from datetime import date, timedelta
from apps.organizations.models import Organization
from apps.appointments.utils import get_available_slots_for_date

org = Organization.objects.get(slug='compueasys')
monday = date.today() + timedelta(days=2)
slots = get_available_slots_for_date(monday, org)
available = [s for s in slots if s['available']]

print(f'Lunes {monday}:')
print(f'  Total slots: {len(slots)}')
print(f'  Disponibles: {len(available)}')
if slots:
    print(f'  Primeros 8: {[str(s["time"]) for s in slots[:8]]}')
