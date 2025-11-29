"""
Script para configurar horarios específicos por fecha
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.appointments.models import WorkingHours, SpecificDateSchedule, AppointmentConfiguration
from datetime import date, time, timedelta
from django.utils import timezone

print("Configurando horarios específicos por fecha...")

# Limpiar horarios recurrentes (WorkingHours)
print("\n1. Limpiando horarios recurrentes...")
deleted_count = WorkingHours.objects.all().delete()[0]
print(f"   ✓ Eliminados {deleted_count} horarios recurrentes")

# Limpiar horarios específicos anteriores
print("\n2. Limpiando horarios específicos anteriores...")
deleted_count = SpecificDateSchedule.objects.all().delete()[0]
print(f"   ✓ Eliminados {deleted_count} horarios específicos")

# Asegurar que el sistema esté abierto
config = AppointmentConfiguration.get_config()
config.is_open = True
config.slot_duration = 30
config.save()
print(f"\n3. Sistema abierto - Duración de cita: {config.slot_duration} minutos")

# Crear horarios específicos de ejemplo
print("\n4. Creando horarios específicos por fecha:")
today = timezone.now().date()

horarios_especificos = [
    # Miércoles 4 de diciembre - 15:00 a 18:00
    {'date': date(2025, 12, 4), 'start': time(15, 0), 'end': time(18, 0), 'notes': 'Tarde especial'},
    
    # Viernes 6 de diciembre - 9:00 a 13:00
    {'date': date(2025, 12, 6), 'start': time(9, 0), 'end': time(13, 0), 'notes': 'Mañana'},
    
    # Lunes 9 de diciembre - 14:00 a 18:00
    {'date': date(2025, 12, 9), 'start': time(14, 0), 'end': time(18, 0), 'notes': 'Tarde completa'},
    
    # Miércoles 11 de diciembre - 10:00 a 12:00 y 15:00 a 17:00
    {'date': date(2025, 12, 11), 'start': time(10, 0), 'end': time(12, 0), 'notes': 'Mañana corta'},
    {'date': date(2025, 12, 11), 'start': time(15, 0), 'end': time(17, 0), 'notes': 'Tarde corta'},
    
    # Sábado 14 de diciembre - 9:00 a 12:00
    {'date': date(2025, 12, 14), 'start': time(9, 0), 'end': time(12, 0), 'notes': 'Sábado especial'},
]

for horario in horarios_especificos:
    SpecificDateSchedule.objects.create(
        date=horario['date'],
        start_time=horario['start'],
        end_time=horario['end'],
        notes=horario['notes'],
        is_active=True
    )
    fecha_str = horario['date'].strftime('%A %d/%m/%Y')
    hora_str = f"{horario['start'].strftime('%H:%M')} - {horario['end'].strftime('%H:%M')}"
    print(f"   ✓ {fecha_str}: {hora_str} ({horario['notes']})")

total = SpecificDateSchedule.objects.count()
print(f"\n✅ Se crearon {total} horarios específicos")
print("\n📅 Ahora solo las fechas configuradas estarán disponibles para agendar citas")
print("   Puedes agregar más fechas desde:")
print("   - Dashboard: http://127.0.0.1:8000/dashboard/configuration/")
print("   - Admin: http://127.0.0.1:8000/admin/appointments/specificdateschedule/")
