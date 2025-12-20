import json
from django.contrib.auth.models import User
from apps.patients.models import Patient, Doctor
from apps.organizations.models import Organization, OrganizationMember, SubscriptionPlan, Subscription

print("=" * 80)
print("DATOS ACTUALES EN PRODUCCIÓN")
print("=" * 80)

print("\n1. USUARIOS:")
users = User.objects.all()
print(f"   Total: {users.count()}")
for u in users:
    print(f"   - {u.username} | {u.first_name} {u.last_name} | {u.email}")

print("\n2. ORGANIZACIONES:")
orgs = Organization.objects.all()
print(f"   Total: {orgs.count()}")
for org in orgs:
    print(f"   - [{org.id}] {org.name} (Owner: {org.owner})")

print("\n3. PLANES DE SUBSCRIPCIÓN:")
plans = SubscriptionPlan.objects.all()
print(f"   Total: {plans.count()}")
for plan in plans:
    print(f"   - [{plan.id}] {plan.name}: ${plan.price}/mes")

print("\n4. SUBSCRIPCIONES:")
subs = Subscription.objects.all()
print(f"   Total: {subs.count()}")
for sub in subs:
    print(f"   - Org: {sub.organization.name} | Plan: {sub.plan.name} | Estado: {sub.status}")

print("\n5. PACIENTES:")
patients = Patient.objects.all()
print(f"   Total: {patients.count()}")

print("\n6. DOCTORES:")
doctors = Doctor.objects.all()
print(f"   Total: {doctors.count()}")

print("\n" + "=" * 80)
print("ANALIZANDO BACKUP")
print("=" * 80)

try:
    with open('backup_final.json', 'r', encoding='latin-1') as f:
        backup_data = json.load(f)
except:
    print("Error leyendo backup, intentando con UTF-8...")
    with open('backup_final.json', 'r', encoding='utf-8', errors='ignore') as f:
        backup_data = json.load(f)

# Buscar Julio Zapata
print("\nBuscando 'Julio Zapata' en backup...")
julio_found = False
for item in backup_data:
    if item['model'] == 'auth.user':
        fields = item['fields']
        username = fields.get('username', '').lower()
        first_name = fields.get('first_name', '').lower()
        last_name = fields.get('last_name', '').lower()
        
        if 'julio' in (username + first_name + last_name) or 'zapata' in (username + first_name + last_name):
            print(f"\n✅ ENCONTRADO en backup:")
            print(f"   PK: {item['pk']}")
            print(f"   Username: {fields.get('username')}")
            print(f"   Nombre: {fields.get('first_name')} {fields.get('last_name')}")
            print(f"   Email: {fields.get('email')}")
            print(f"   Staff: {fields.get('is_staff')}, Superuser: {fields.get('is_superuser')}")
            julio_found = True

if not julio_found:
    print("❌ Julio Zapata NO encontrado en backup")

# Contar planes en backup
print("\nPlanes en backup:")
plan_count = 0
for item in backup_data:
    if item['model'] == 'organizations.subscriptionplan':
        plan_count += 1
        fields = item['fields']
        print(f"   - [{item['pk']}] {fields.get('name')}: ${fields.get('price')}")
print(f"   Total en backup: {plan_count}")

# Contar subscripciones en backup
print("\nSubscripciones en backup:")
sub_count = 0
for item in backup_data:
    if item['model'] == 'organizations.subscription':
        sub_count += 1
        fields = item['fields']
        print(f"   - [{item['pk']}] Org: {fields.get('organization')} | Plan: {fields.get('plan')} | Estado: {fields.get('status')}")
print(f"   Total en backup: {sub_count}")

# Contar usuarios en backup
print("\nUsuarios en backup (además del superusuario):")
user_count = 0
for item in backup_data:
    if item['model'] == 'auth.user':
        user_count += 1
        fields = item['fields']
        if not fields.get('is_superuser'):
            print(f"   - [{item['pk']}] {fields.get('username')} ({fields.get('email')})")
print(f"   Total usuarios en backup: {user_count}")

print("\n" + "=" * 80)
print("RESUMEN")
print("=" * 80)
print(f"Usuarios en producción: {users.count()} | En backup: {user_count}")
print(f"Planes en producción: {plans.count()} | En backup: {plan_count}")
print(f"Subscripciones en producción: {subs.count()} | En backup: {sub_count}")
print(f"Organizaciones en producción: {orgs.count()}")
print(f"Pacientes en producción: {patients.count()}")
print(f"Doctores en producción: {doctors.count()}")
