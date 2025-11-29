"""
Script para configurar horarios de atención de ejemplo
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.appointments.models import WorkingHours, AppointmentConfiguration
from datetime import time

print("Configurando horarios de atención...")

# Asegurar que el sistema esté abierto
config = AppointmentConfiguration.get_config()
config.is_open = True
config.slot_duration = 30  # 30 minutos por cita
config.save()
print(f"✓ Sistema abierto - Duración de cita: {config.slot_duration} minutos")

# Eliminar horarios existentes para empezar de nuevo
WorkingHours.objects.all().delete()

# Crear horarios de atención de ejemplo
horarios = [
    # Lunes a Viernes: 9am - 12pm y 2pm - 6pm
    {'day': 0, 'start': time(9, 0), 'end': time(12, 0), 'name': 'Lunes Mañana'},
    {'day': 0, 'start': time(14, 0), 'end': time(18, 0), 'name': 'Lunes Tarde'},
    
    {'day': 1, 'start': time(9, 0), 'end': time(12, 0), 'name': 'Martes Mañana'},
    {'day': 1, 'start': time(14, 0), 'end': time(18, 0), 'name': 'Martes Tarde'},
    
    {'day': 2, 'start': time(9, 0), 'end': time(12, 0), 'name': 'Miércoles Mañana'},
    {'day': 2, 'start': time(15, 0), 'end': time(18, 0), 'name': 'Miércoles Tarde'},
    
    {'day': 3, 'start': time(9, 0), 'end': time(12, 0), 'name': 'Jueves Mañana'},
    {'day': 3, 'start': time(14, 0), 'end': time(18, 0), 'name': 'Jueves Tarde'},
    
    {'day': 4, 'start': time(9, 0), 'end': time(12, 0), 'name': 'Viernes Mañana'},
    {'day': 4, 'start': time(14, 0), 'end': time(17, 0), 'name': 'Viernes Tarde'},
    
    # Sábado: solo mañana
    {'day': 5, 'start': time(9, 0), 'end': time(13, 0), 'name': 'Sábado Mañana'},
]

for horario in horarios:
    wh = WorkingHours.objects.create(
        day_of_week=horario['day'],
        start_time=horario['start'],
        end_time=horario['end'],
        is_active=True
    )
    print(f"✓ {horario['name']}: {horario['start'].strftime('%H:%M')} - {horario['end'].strftime('%H:%M')}")

print(f"\n✓ Se crearon {WorkingHours.objects.count()} horarios de atención")
print("\nHorarios configurados:")
print("- Lunes a Viernes: 9:00-12:00 y 14:00-18:00")
print("- Miércoles tarde: 15:00-18:00 (como solicitaste)")
print("- Sábado: 9:00-13:00")
print("- Domingo: Cerrado")
print("\n✅ Ahora puedes ir a la landing page y agendar citas!")
print("   http://127.0.0.1:8000/booking/")
