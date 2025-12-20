import os
import sys
import django
import json

# Configure Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'OpticaApp.settings')
django.setup()

from django.contrib.auth.models import User
from apps.patients.models import Patient, Doctor
from apps.organizations.models import Organization, OrganizationMember, SubscriptionPlan, Subscription

print("=" * 80)
print("VERIFICACIÓN DE DATOS EN PRODUCCIÓN")
print("=" * 80)

# Verificar usuarios
print("\n1. USUARIOS:")
users = User.objects.all()
print(f"   Total usuarios: {users.count()}")
for user in users:
    print(f"   - {user.username} ({user.email}) - Staff: {user.is_staff}, Superuser: {user.is_superuser}")

# Buscar Julio Zapata específicamente
julio_users = User.objects.filter(username__icontains='julio') | User.objects.filter(first_name__icontains='julio') | User.objects.filter(last_name__icontains='zapata')
if julio_users.exists():
    print(f"\n   ¡JULIO ENCONTRADO!")
    for u in julio_users:
        print(f"   - {u.username} - {u.first_name} {u.last_name} ({u.email})")
else:
    print(f"\n   ❌ Julio Zapata NO encontrado en producción")

# Verificar organizaciones
print("\n2. ORGANIZACIONES:")
orgs = Organization.objects.all()
print(f"   Total organizaciones: {orgs.count()}")
for org in orgs:
    print(f"   - ID: {org.id} - {org.name} (Owner: {org.owner})")

# Verificar miembros de organizaciones
print("\n3. MIEMBROS DE ORGANIZACIONES:")
members = OrganizationMember.objects.all()
print(f"   Total miembros: {members.count()}")
for member in members:
    print(f"   - {member.user.username} en {member.organization.name} (Role: {member.role})")

# Verificar planes de subscripción
print("\n4. PLANES DE SUBSCRIPCIÓN:")
plans = SubscriptionPlan.objects.all()
print(f"   Total planes: {plans.count()}")
for plan in plans:
    print(f"   - {plan.name}: ${plan.price}/mes - Límites: {plan.max_patients} pacientes, {plan.max_users} usuarios")

# Verificar subscripciones activas
print("\n5. SUBSCRIPCIONES ACTIVAS:")
subscriptions = Subscription.objects.all()
print(f"   Total subscripciones: {subscriptions.count()}")
for sub in subscriptions:
    print(f"   - Org: {sub.organization.name} - Plan: {sub.plan.name} - Estado: {sub.status} - Activo: {sub.is_active()}")

# Verificar pacientes
print("\n6. PACIENTES:")
patients = Patient.objects.all()
print(f"   Total pacientes: {patients.count()}")

# Verificar doctores
print("\n7. DOCTORES:")
doctors = Doctor.objects.all()
print(f"   Total doctores: {doctors.count()}")

print("\n" + "=" * 80)
print("VERIFICACIÓN DEL BACKUP")
print("=" * 80)

# Leer el backup
try:
    with open('backup_final.json', 'r', encoding='latin-1') as f:
        backup_data = json.load(f)
    
    # Contar por modelo
    models_count = {}
    for item in backup_data:
        model = item['model']
        models_count[model] = models_count.get(model, 0) + 1
    
    print("\nCONTENIDO DEL BACKUP:")
    for model, count in sorted(models_count.items()):
        print(f"   {model}: {count} registros")
    
    # Buscar Julio Zapata en el backup
    print("\n\nBUSCANDO JULIO ZAPATA EN EL BACKUP:")
    for item in backup_data:
        fields = item.get('fields', {})
        # Buscar en usuarios
        if item['model'] == 'auth.user':
            username = fields.get('username', '')
            first_name = fields.get('first_name', '')
            last_name = fields.get('last_name', '')
            email = fields.get('email', '')
            
            if 'julio' in username.lower() or 'julio' in first_name.lower() or 'zapata' in last_name.lower():
                print(f"   ✅ ENCONTRADO en backup:")
                print(f"      Username: {username}")
                print(f"      Nombre: {first_name} {last_name}")
                print(f"      Email: {email}")
                print(f"      PK: {item['pk']}")
        
        # Buscar en pacientes/doctores por nombre
        if item['model'] in ['patients.patient', 'patients.doctor']:
            full_name = fields.get('full_name', '')
            if 'julio' in full_name.lower() and 'zapata' in full_name.lower():
                print(f"   ✅ ENCONTRADO como {item['model']}:")
                print(f"      Nombre: {full_name}")
                print(f"      Identification: {fields.get('identification', '')}")
    
    # Mostrar planes del backup
    print("\n\nPLANES EN EL BACKUP:")
    for item in backup_data:
        if item['model'] == 'organizations.subscriptionplan':
            fields = item['fields']
            print(f"   - {fields.get('name')}: ${fields.get('price')}/mes")
    
    # Mostrar subscripciones del backup
    print("\nSUBSCRIPCIONES EN EL BACKUP:")
    for item in backup_data:
        if item['model'] == 'organizations.subscription':
            fields = item['fields']
            print(f"   - Org ID: {fields.get('organization')} - Plan ID: {fields.get('plan')} - Estado: {fields.get('status')}")

except FileNotFoundError:
    print("   ❌ Archivo backup_final.json no encontrado")
except Exception as e:
    print(f"   ❌ Error leyendo backup: {e}")

print("\n" + "=" * 80)
print("RESUMEN DE DATOS FALTANTES")
print("=" * 80)
