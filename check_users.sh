#!/bin/bash
cd /var/www/opticaapp
source venv/bin/activate

python << 'PYEOF'
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'optica_project.settings')
django.setup()

from django.contrib.auth.models import User
from apps.organizations.models import Organization
from apps.employees.models import Employee

print('\n=== USUARIOS EN LA BASE DE DATOS ===')
users = User.objects.all()
if not users:
    print('❌ NO HAY USUARIOS EN LA BASE DE DATOS')
else:
    for u in users:
        print(f'\nID: {u.id}')
        print(f'  Username: {u.username}')
        print(f'  Email: {u.email}')
        print(f'  Activo: {u.is_active}')
        print(f'  Staff: {u.is_staff}')
        print(f'  Superuser: {u.is_superuser}')
        print(f'  Último login: {u.last_login}')

print(f'\n\nTotal usuarios: {users.count()}')

print('\n=== EMPLEADOS ===')
employees = Employee.objects.all()
print(f'Total empleados: {employees.count()}')
for emp in employees:
    print(f'  - {emp.first_name} {emp.last_name} (User ID: {emp.user_id if emp.user else "Sin user"})')

print('\n=== ORGANIZACIONES ===')
orgs = Organization.objects.all()
print(f'Total organizaciones: {orgs.count()}')
for org in orgs:
    print(f'  - ID {org.id}: {org.name}')
PYEOF
