import os
import sys

# Agregar el directorio al path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')

import django
django.setup()

from django.contrib.auth.models import User
from apps.patients.models import Patient, Doctor
from apps.organizations.models import Organization
from apps.subscriptions.models import Plan, Subscription

print("=" * 70)
print("DATOS ACTUALES EN PRODUCCIÓN")
print("=" * 70)

# Usuarios
users = User.objects.all()
print(f"\n👥 USUARIOS ({users.count()}):")
for u in users:
    print(f"  - {u.username}: {u.first_name} {u.last_name} ({u.email})")

# Pacientes
patients = Patient.objects.all()
print(f"\n🏥 PACIENTES ({patients.count()}):")
for p in patients[:5]:  # Primeros 5
    print(f"  - {p.full_name} (ID: {p.identification})")
if patients.count() > 5:
    print(f"  ... y {patients.count() - 5} más")

# Buscar Julio específicamente
julio_patient = Patient.objects.filter(full_name__icontains='julio')
print(f"\n🔍 PACIENTES CON 'JULIO' ({julio_patient.count()}):")
for p in julio_patient:
    print(f"  - {p.full_name} (ID: {p.identification})")

# Doctores
doctors = Doctor.objects.all()
print(f"\n👨‍⚕️ DOCTORES ({doctors.count()}):")
for d in doctors:
    print(f"  - {d.full_name} - {d.specialty}")

# Organizaciones
orgs = Organization.objects.all()
print(f"\n🏢 ORGANIZACIONES ({orgs.count()}):")
for o in orgs:
    print(f"  - {o.name} (ID: {o.id}, Owner: {o.owner.username if o.owner else 'Sin owner'})")

# Planes
plans = Plan.objects.all()
print(f"\n📋 PLANES ({plans.count()}):")
for p in plans:
    print(f"  - {p.name}: ${p.monthly_price}/mes - {p.max_users} usuarios, {p.max_patients} pacientes")

# Suscripciones
subs = Subscription.objects.all()
print(f"\n💳 SUSCRIPCIONES ({subs.count()}):")
for s in subs:
    org_name = s.organization.name if s.organization else 'Sin org'
    plan_name = s.plan.name if s.plan else 'Sin plan'
    print(f"  - {org_name}: {plan_name} - {s.status}")

print("\n" + "=" * 70)
