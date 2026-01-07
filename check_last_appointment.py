import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.appointments.models import Appointment
from apps.organizations.models import Organization
from apps.appointments.notifications import get_notifier

# Obtener última cita
org = Organization.objects.get(slug='compueasys')
app = Appointment.objects.filter(organization=org).order_by('-created_at').first()

print(f'Última cita creada:')
print(f'  ID: {app.id}')
print(f'  Nombre: {app.full_name}')
print(f'  Telefono: {app.phone_number}')
print(f'  Fecha: {app.appointment_date} {app.appointment_time}')
print(f'  Creada: {app.created_at}')
print()

# Intentar enviar notificación
print('Enviando notificación...')
notifier = get_notifier(org)
result = notifier.send_appointment_confirmation(app)
print(f'Resultado: {result}')
