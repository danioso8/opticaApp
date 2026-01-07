"""
Script para crear una cita de prueba y verificar que se envíe la notificación por WhatsApp
"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')psql -h localhost -U opticaapp_user -d opticaapp_db -c "SELECT COUNT(*) FROM organizations_organization;"
psql -h localhost -U opticaapp_user -d opticaapp_db -c "SELECT COUNT(*) FROM patients_patient;"
psql -h localhost -U opticaapp_user -d opticaapp_db -c "SELECT COUNT(*) FROM appointments_appointment;"
django.setup()

from apps.appointments.models import Appointment
from apps.organizations.models import Organization
from apps.patients.models import Doctor

# Obtener organización
org = Organization.objects.get(id=23)

# Obtener un doctor
doctor = Doctor.objects.filter(organization=org).first()
if not doctor:
    print("⚠️  No hay doctores en la organización, creando cita sin doctor asignado")
    doctor = None

# Crear cita de prueba con hora única
tomorrow = datetime.now().date() + timedelta(days=1)
# Usar la hora actual para evitar duplicados
current_time = datetime.now()
appointment_time = current_time.replace(second=0, microsecond=0).time()

print(f"📅 Creando cita para {tomorrow} a las {appointment_time}")

appointment = Appointment(
    organization=org,
    full_name="Prueba WhatsApp ✅",
    phone_number="3007915262",
    appointment_date=tomorrow,
    appointment_time=appointment_time,
    status='confirmed'
)
appointment.save()  # Esto dispara el signal post_save

print("✅ Cita creada exitosamente:")
print(f"   ID: {appointment.id}")
print(f"   Nombre: {appointment.full_name}")
print(f"   Teléfono: {appointment.phone_number}")
print(f"   Fecha: {appointment.appointment_date}")
print(f"   Hora: {appointment.appointment_time}")
print("")
print("🔔 La notificación debería enviarse automáticamente...")
print("   Revisa tu WhatsApp en el número 3007915262!")
