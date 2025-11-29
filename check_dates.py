import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from datetime import datetime, timedelta
from django.utils import timezone
from apps.appointments.models import WorkingHours, AppointmentConfiguration
from apps.appointments.utils import get_available_dates

today = timezone.now().date()
print(f"Hoy es: {today}")
print(f"Día de la semana: {today.strftime('%A')} (0=Lunes, {today.weekday()})")
print()

config = AppointmentConfiguration.get_config()
print(f"Sistema abierto: {config.is_open}")
print(f"Días de anticipación: {config.advance_booking_days}")
print()

print("Horarios configurados por día:")
for day in range(7):
    day_names = ['Lunes', 'Martes', 'Miércoles', 'Jueves', 'Viernes', 'Sábado', 'Domingo']
    wh = WorkingHours.objects.filter(day_of_week=day, is_active=True)
    if wh.exists():
        print(f"  {day_names[day]}:")
        for h in wh:
            print(f"    - {h.start_time.strftime('%H:%M')} a {h.end_time.strftime('%H:%M')}")
    else:
        print(f"  {day_names[day]}: Sin horarios")

print()
print("Próximas 10 fechas con horarios disponibles:")
for i in range(30):
    date = today + timedelta(days=i)
    day_of_week = date.weekday()
    has_wh = WorkingHours.objects.filter(day_of_week=day_of_week, is_active=True).exists()
    if has_wh:
        day_name = date.strftime('%A')
        print(f"  {date} ({day_name})")
        if len([d for d in range(i+1) if (today + timedelta(days=d)).weekday() in [0,1,2,3,4,5]]) >= 10:
            break
