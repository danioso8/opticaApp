import os
import django
import sys

# Configurar Django
sys.path.append('d:\\ESCRITORIO\\OpticaApp')
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth import get_user_model
from apps.organizations.models import Organization
from apps.users.models import UserProfile
from apps.patients.models_doctors import Doctor
from apps.patients.models import Patient
from apps.sales.models import Product, Category
from datetime import datetime, timedelta
from django.utils import timezone

User = get_user_model()

print("Creando cuenta DEMO...")

# 1. Crear usuario demo
demo_user, created = User.objects.get_or_create(
    username='demo',
    defaults={
        'email': 'demo@optikaapp.com',
        'first_name': 'Usuario',
        'last_name': 'Demo',
        'is_active': True,
        'is_staff': False,
        'is_superuser': False,
    }
)

if created:
    demo_user.set_password('demo123')
    demo_user.save()
    print("✓ Usuario 'demo' creado con contraseña 'demo123'")
else:
    demo_user.set_password('demo123')
    demo_user.save()
    print("✓ Usuario 'demo' actualizado con contraseña 'demo123'")

# 2. Crear organización demo
org, org_created = Organization.objects.get_or_create(
    name='Óptica Demo',
    defaults={
        'slug': 'optica-demo',
        'legal_name': 'Óptica Demo S.A.S.',
        'tax_id_type': 'NIT',
        'tax_id': '900123456-1',
        'address': 'Calle 123 #45-67',
        'city': 'Bogotá',
        'country': 'Colombia',
        'phone': '601-234-5678',
        'email': 'info@opticademo.com',
        'is_active': True,
        'owner': demo_user,
    }
)
print(f"✓ Organización '{org.name}' {'creada' if org_created else 'actualizada'}")

print("\n✅ CUENTA DEMO CREADA EXITOSAMENTE")
print("\n📋 CREDENCIALES DE ACCESO:")
print("   Usuario: demo")
print("   Contraseña: demo123")
print("\n📊 DATOS CREADOS:")
print(f"   - 1 Organización: {org.name}")
print("\n🌐 Accede a: http://84.247.129.180 o http://optikaapp.com")
print("\nNOTA: Los datos de doctores, pacientes y productos deben agregarse manualmente desde el admin de Django")

