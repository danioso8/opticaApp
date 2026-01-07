#!/bin/bash
cd /var/www/opticaapp
source venv/bin/activate

echo "=== CREANDO USUARIOS NECESARIOS ==="
python manage.py shell << 'EOF'
from django.contrib.auth.models import User

# Crear usuarios necesarios para las organizaciones
usuarios = [
    {'username': 'danioso8', 'email': 'danioso8@gmail.com', 'password': 'Admin123456', 'is_superuser': True, 'is_staff': True, 'first_name': 'Daniel', 'last_name': 'Osorio'},
    {'username': 'OceanoSJ', 'email': 'oceanoptics4@gmail.com', 'password': 'OceanoSJ2026', 'is_superuser': False, 'is_staff': True, 'first_name': 'Oceano', 'last_name': 'Optico'},
    {'username': 'danioso83', 'email': 'danioso83@gmail.com', 'password': 'Temu2026', 'is_superuser': False, 'is_staff': True, 'first_name': 'Daniel', 'last_name': 'Temu'}
]

for user_data in usuarios:
    username = user_data['username']
    password = user_data['password']
    User.objects.filter(username=username).delete()
    user = User.objects.create_user(username=username, password=password, email=user_data['email'], first_name=user_data['first_name'], last_name=user_data['last_name'], is_superuser=user_data['is_superuser'], is_staff=user_data['is_staff'])
    print(f"Usuario creado: {username} - Password: {password}")

print("Usuarios creados correctamente")
EOF

echo ""
echo "=== LIMPIANDO BASE DE DATOS ==="
python manage.py flush --no-input

echo ""
echo "=== RESTAURANDO BACKUP ==="
python manage.py loaddata backup_final.json

echo ""
echo "=== VERIFICANDO RESTAURACION ==="
python manage.py shell << 'EOF'
from django.contrib.auth.models import User
from apps.organizations.models import Organization
from apps.patients.models import Patient

print(f"\nUsuarios: {User.objects.count()}")
for u in User.objects.all():
    print(f"  - {u.username} ({u.email})")

print(f"\nOrganizaciones: {Organization.objects.count()}")
for o in Organization.objects.all():
    owner = o.owner.username if o.owner else 'Sin owner'
    print(f"  - {o.name} (Owner: {owner})")

print(f"\nPacientes: {Patient.objects.count()}")

print("\n" + "="*50)
print("RESTAURACION COMPLETA")
print("="*50)
print("\nCREDENCIALES:")
print("  Username: danioso8")
print("  Password: Admin123456")
print("\nAccede en: http://84.247.129.180")
print("="*50)
EOF
