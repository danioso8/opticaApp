#!/bin/bash
cd /var/www/opticaapp
source venv/bin/activate

echo "=== CREANDO USUARIOS NECESARIOS ==="
python << 'PYEOF'
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optica_project.settings')
django.setup()

from django.contrib.auth.models import User

# Crear usuarios necesarios para las organizaciones
usuarios = [
    {
        'username': 'danioso8',
        'email': 'danioso8@gmail.com',
        'password': 'Admin123456',
        'is_superuser': True,
        'is_staff': True,
        'first_name': 'Daniel',
        'last_name': 'Osorio'
    },
    {
        'username': 'OceanoSJ',
        'email': 'oceanoptics4@gmail.com',
        'password': 'OceanoSJ2026',
        'is_superuser': False,
        'is_staff': True,
        'first_name': 'Oceano',
        'last_name': 'Optico'
    },
    {
        'username': 'danioso83',
        'email': 'danioso83@gmail.com',
        'password': 'Temu2026',
        'is_superuser': False,
        'is_staff': True,
        'first_name': 'Daniel',
        'last_name': 'Temu'
    }
]

for user_data in usuarios:
    username = user_data.pop('username')
    password = user_data.pop('password')
    
    # Eliminar si existe
    User.objects.filter(username=username).delete()
    
    # Crear nuevo
    user = User.objects.create_user(username=username, password=password, **user_data)
    print(f"✅ Usuario creado: {username} ({user.email})")
    print(f"   Contraseña: {password}")
    print(f"   Superuser: {user.is_superuser}")

print("\n✅ Todos los usuarios creados correctamente")
PYEOF

echo ""
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
    owner = o.owner.username if o.owner else 'Sin owner'
    print(f'   - {o.name} (Owner: {owner})')

print('\n✅ PACIENTES:')
patients = Patient.objects.all()
print(f'   Total: {patients.count()}')

print('\n✅ CITAS:')
appointments = Appointment.objects.all()
print(f'   Total: {appointments.count()}')

print('\n' + '='*50)
print('✅ RESTAURACIÓN COMPLETA')
print('='*50)
print('\n🔑 CREDENCIALES DE ACCESO:')
print('\n1. Usuario Principal (TU USUARIO):')
print('   Username: danioso8')
print('   Password: Admin123456')
print('\n2. Usuario Oceano Optico SJ:')
print('   Username: OceanoSJ')
print('   Password: OceanoSJ2026')
print('\n3. Usuario CompuTemu:')
print('   Username: danioso83')
print('   Password: Temu2026')
print('\n🌐 Accede en: http://84.247.129.180')
print('='*50)
PYEOF
