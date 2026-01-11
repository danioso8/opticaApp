import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import Organization
from apps.appointments.models import WorkingHours, AppointmentConfiguration

org = Organization.objects.get(id=4)
print(f"Org: {org.name}")

config = AppointmentConfiguration.get_config(org)
print(f"Config: {config.is_open}")
print(f"Advance days: {config.advance_booking_days}")

from datetime import timedelta, date
from django.utils import timezone
import pytz

local_tz = pytz.timezone('America/Bogota')
today = timezone.now().astimezone(local_tz).date()
print(f"Today: {today}")

working_hours = WorkingHours.objects.filter(organization=org, is_active=True).values_list('day_of_week', flat=True)
working_days = set(working_hours)
print(f"Working days: {working_days}")

available_dates = []
max_days = config.advance_booking_days

for i in range(max_days + 1):
    current_date = today + timedelta(days=i)
    if current_date.weekday() in working_days:
        available_dates.append(str(current_date))

print(f"Total dates: {len(available_dates)}")
print(f"First 5: {available_dates[:5]}")
