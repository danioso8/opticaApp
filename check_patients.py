from apps.patients.models import Patient
from apps.organizations.models import Organization

orgs = Organization.objects.all()
print("\n=== ORGANIZACIONES ===")
for o in orgs:
    print(f"- {o.name} (ID: {o.id})")

patients = Patient.objects.all()
print(f"\n=== PACIENTES (Total: {patients.count()}) ===")
for p in patients:
    org_name = p.organization.name if p.organization else "Sin organización"
    print(f"- {p.full_name} ({p.phone_number})")
    print(f"  Organización: {org_name}")
    print(f"  Activo: {p.is_active}")
    print()
