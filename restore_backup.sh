#!/bin/bash
cd /var/www/opticaapp
source venv/bin/activate

echo "=== LIMPIANDO BASE DE DATOS ==="
python manage.py flush --no-input

echo ""
echo "=== RESTAURANDO BACKUP ==="
python manage.py loaddata backup_final.json

echo ""
echo "=== VERIFICANDO DATOS RESTAURADOS ==="
python << 'PYEOF'
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optica_project.settings')
django.setup()

from django.contrib.auth.models import User
from apps.organizations.models import Organization
from apps.patients.models import Patient
from apps.appointments.models import Appointment

print('\n✅ USUARIOS:')
users = User.objects.all()
print(f'   Total: {users.count()}')
for u in users:
    print(f'   - {u.username} ({u.email}) - Superuser: {u.is_superuser}')

print('\n✅ ORGANIZACIONES:')
orgs = Organization.objects.all()
print(f'   Total: {orgs.count()}')
for o in orgs:
    print(f'   - {o.name}')

print('\n✅ PACIENTES:')
patients = Patient.objects.all()
print(f'   Total: {patients.count()}')

print('\n✅ CITAS:')
appointments = Appointment.objects.all()
print(f'   Total: {appointments.count()}')

print('\n✅ RESTAURACIÓN COMPLETA')
PYEOF
