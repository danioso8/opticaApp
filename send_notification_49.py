import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.appointments.models import Appointment
from apps.appointments.signals import notify_new_appointment

# Get appointment #49
appointment = Appointment.objects.get(id=49)

print(f"\n=== ENVIANDO NOTIFICACIÓN PARA CITA #{appointment.id} ===")
print(f"Nombre: {appointment.full_name}")
print(f"Teléfono: {appointment.phone_number}")
print(f"Fecha: {appointment.appointment_date}")
print(f"Hora: {appointment.appointment_time}")
print(f"Doctor: {appointment.doctor.full_name if appointment.doctor else 'Sin asignar'}")
print("\nEnviando notificación...")

try:
    notify_new_appointment(appointment)
    print("\n✅ Notificación enviada exitosamente!")
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
