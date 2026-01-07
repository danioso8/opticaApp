"""
Script para probar envío de WhatsApp a la última cita de CompuEasys
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.appointments.models import Appointment
from apps.core.models import Organization
from apps.appointments.notifications import get_notifier

# Obtener última cita de CompuEasys
org = Organization.objects.get(slug='compueasys')
appointment = Appointment.objects.filter(organization=org).order_by('-created_at').first()

if not appointment:
    print("❌ No hay citas registradas para CompuEasys")
    exit(1)

print(f"📋 Cita encontrada:")
print(f"   ID: {appointment.id}")
print(f"   Nombre: {appointment.full_name}")
print(f"   Teléfono: {appointment.phone_number}")
print(f"   Fecha: {appointment.appointment_date} {appointment.appointment_time}")
print(f"   Estado: {appointment.status}")
print()

# Intentar enviar notificación
print("📤 Enviando notificación de WhatsApp...")
try:
    notifier = get_notifier(org)
    result = notifier.send_appointment_confirmation(appointment)
    
    if result:
        print("✅ Notificación enviada exitosamente!")
    else:
        print("⚠️ La notificación retornó False - revisa los logs")
        
except Exception as e:
    print(f"❌ Error al enviar notificación: {e}")
    import traceback
    traceback.print_exc()
