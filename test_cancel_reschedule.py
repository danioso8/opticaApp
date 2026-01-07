import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.appointments.models import Appointment
from apps.organizations.models import Organization
from django.utils import timezone

# Organización CompuEasys
org = Organization.objects.get(slug='compueasys')
print(f"\n=== TRABAJANDO CON: {org.name} (ID: {org.id}) ===\n")

# Ver todas las citas de esta organización
all_appointments = Appointment.objects.filter(organization=org).order_by('-id')[:10]
print(f"Total de citas recientes: {all_appointments.count()}\n")

for apt in all_appointments:
    print(f"ID: {apt.id} | {apt.full_name} | {apt.phone_number} | {apt.status} | {apt.appointment_date} {apt.appointment_time}")

print("\n" + "="*70)
print("\n=== PRUEBA 1: CREAR NUEVA CITA PARA CANCELAR ===\n")

# Crear una nueva cita con hora única
tomorrow = timezone.now().date() + timedelta(days=2)
current_time = timezone.now()
unique_time = f"{current_time.hour:02d}:{current_time.minute:02d}:00"

new_appointment = Appointment.objects.create(
    organization=org,
    full_name="Test Cancelación Usuario",
    phone_number="3009787566",
    email="test@cancel.com",
    appointment_date=tomorrow,
    appointment_time=unique_time,
    status="scheduled"
)

print(f"✅ Cita creada: #{new_appointment.id}")
print(f"   Paciente: {new_appointment.full_name}")
print(f"   Teléfono: {new_appointment.phone_number}")
print(f"   Estado: {new_appointment.status}")
print(f"   Fecha: {new_appointment.appointment_date} {new_appointment.appointment_time}")

print(f"\n🔄 Esperando 2 segundos...")
import time
time.sleep(2)

print(f"\n❌ CANCELANDO CITA #{new_appointment.id}...")
new_appointment.status = 'cancelled'
new_appointment.save()

print(f"✅ Cita cancelada. Estado: {new_appointment.status}")
print("🔔 Verifica si llegó el WhatsApp de cancelación")

print("\n" + "="*70)
print("\n=== PRUEBA 2: CREAR NUEVA CITA PARA REAGENDAR ===\n")

# Crear otra cita para reagendar con hora diferente
day_after = tomorrow + timedelta(days=1)
unique_time2 = f"{(current_time.hour + 1) % 24:02d}:{current_time.minute:02d}:00"

reschedule_appointment = Appointment.objects.create(
    organization=org,
    full_name="Test Reagendar Usuario",
    phone_number="3009787566",
    email="test@reschedule.com",
    appointment_date=day_after,
    appointment_time=unique_time2,
    status="scheduled"
)

print(f"✅ Cita creada: #{reschedule_appointment.id}")
print(f"   Paciente: {reschedule_appointment.full_name}")
print(f"   Teléfono: {reschedule_appointment.phone_number}")
print(f"   Fecha original: {reschedule_appointment.appointment_date} {reschedule_appointment.appointment_time}")

print(f"\n🔄 Esperando 2 segundos...")
time.sleep(2)

# Reagendar
old_date = reschedule_appointment.appointment_date
old_time = reschedule_appointment.appointment_time
new_date = old_date + timedelta(days=2)
# Usar hora y minutos actuales para evitar conflictos
current_time = datetime.now(timezone.utc)
new_hour = (current_time.hour + 1) % 24
new_minute = current_time.minute
new_time = f"{new_hour:02d}:{new_minute:02d}:00"

print(f"\n🔄 REAGENDANDO CITA #{reschedule_appointment.id}...")
print(f"   De: {old_date} {old_time}")
print(f"   A:  {new_date} {new_time}")

reschedule_appointment.appointment_date = new_date
reschedule_appointment.appointment_time = new_time
reschedule_appointment.save()

print(f"✅ Cita reagendada")
print(f"   Nueva fecha: {reschedule_appointment.appointment_date} {reschedule_appointment.appointment_time}")
print("🔔 Verifica si llegó el WhatsApp de reagendamiento")

print("\n" + "="*70)
print("\n✅ Pruebas completadas. Verifica tus mensajes de WhatsApp.")
print(f"   - Cancelación de cita #{new_appointment.id}")
print(f"   - Reagendamiento de cita #{reschedule_appointment.id}")

