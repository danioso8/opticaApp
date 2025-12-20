#!/usr/bin/env python
"""Script para verificar todos los datos en la base de datos de producción"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OpticaApp.settings')
django.setup()

from django.contrib.auth.models import User
from apps.patients.models import Patient, Doctor
from apps.organizations.models import Organization
from apps.subscriptions.models import Plan, Subscription

print("=" * 60)
print("VERIFICACIÓN DE DATOS EN PRODUCCIÓN")
print("=" * 60)

# Conteo general
print("\n📊 CONTEO GENERAL:")
print(f"  👤 Usuarios: {User.objects.count()}")
print(f"  🏥 Pacientes: {Patient.objects.count()}")
print(f"  👨‍⚕️ Doctores: {Doctor.objects.count()}")
print(f"  🏢 Organizaciones: {Organization.objects.count()}")
print(f"  📋 Planes: {Plan.objects.count()}")
print(f"  💳 Suscripciones: {Subscription.objects.count()}")

# Lista de usuarios
print("\n👥 USUARIOS:")
for u in User.objects.all():
    print(f"  - {u.username}: {u.first_name} {u.last_name} ({u.email})")

# Buscar Julio Zapata específicamente
print("\n🔍 BÚSQUEDA DE 'JULIO ZAPATA':")
julio_user = User.objects.filter(first_name__icontains='julio', last_name__icontains='zapata')
if julio_user.exists():
    print(f"  ✅ Encontrado como Usuario: {julio_user.first_name} {julio_user.last_name}")
else:
    print("  ❌ NO encontrado como Usuario")

julio_patient = Patient.objects.filter(full_name__icontains='julio zapata')
if julio_patient.exists():
    for p in julio_patient:
        print(f"  ✅ Encontrado como Paciente: {p.full_name}")
else:
    print("  ❌ NO encontrado como Paciente")

julio_doctor = Doctor.objects.filter(full_name__icontains='julio zapata')
if julio_doctor.exists():
    for d in julio_doctor:
        print(f"  ✅ Encontrado como Doctor: {d.full_name}")
else:
    print("  ❌ NO encontrado como Doctor")

# Lista de organizaciones
print("\n🏢 ORGANIZACIONES:")
for o in Organization.objects.all():
    print(f"  - {o.name} (ID: {o.id}, Owner: {o.owner})")

# Lista de planes
print("\n📋 PLANES:")
for p in Plan.objects.all():
    print(f"  - {p.name}: ${p.monthly_price}/mes")

# Lista de suscripciones
print("\n💳 SUSCRIPCIONES:")
for s in Subscription.objects.all():
    print(f"  - {s.organization.name if s.organization else 'Sin org'}: Plan {s.plan.name if s.plan else 'Sin plan'} - {s.status}")

print("\n" + "=" * 60)
