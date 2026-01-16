#!/usr/bin/env python3
"""
Crear usuario de prueba en Contabo para testing de booking
"""
import os, sys, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.organizations.models import Organization
from apps.core.models import UserProfile

# Configuración del usuario
USERNAME = input("Username: ").strip() or "test_booking"
EMAIL = input("Email: ").strip() or "test@compueasys.com"
PASSWORD = input("Password: ").strip() or "Test123456"
FIRST_NAME = input("Nombre: ").strip() or "Usuario"
LAST_NAME = input("Apellido: ").strip() or "Prueba"

print("\n" + "="*70)
print("CREANDO USUARIO DE PRUEBA")
print("="*70)

# Verificar si existe
if User.objects.filter(username=USERNAME).exists():
    print(f"\n❌ Usuario '{USERNAME}' ya existe")
    user = User.objects.get(username=USERNAME)
    print(f"   Email: {user.email}")
    print(f"   Nombre: {user.get_full_name()}")
else:
    # Crear usuario
    user = User.objects.create_user(
        username=USERNAME,
        email=EMAIL,
        password=PASSWORD,
        first_name=FIRST_NAME,
        last_name=LAST_NAME
    )
    print(f"\n✅ Usuario creado: {USERNAME}")

# Asignar a CompuEasys2
org = Organization.objects.get(slug='compueasys2')

# Crear/actualizar UserProfile
profile, created = UserProfile.objects.get_or_create(
    user=user,
    defaults={'organization': org}
)

if not created and profile.organization != org:
    profile.organization = org
    profile.save()

print(f"✅ Asignado a: {org.name}")
print(f"\n{'='*70}")
print("CREDENCIALES:")
print("="*70)
print(f"Username: {USERNAME}")
print(f"Password: {PASSWORD}")
print(f"Email: {EMAIL}")
print(f"\n🌐 Login: https://optikaapp.com/login/")
print(f"🌐 Booking: https://optikaapp.com/booking/compueasys2")
print("="*70)
