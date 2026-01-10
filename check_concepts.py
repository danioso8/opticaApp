from apps.payroll.models import DeductionConcept, AccrualConcept
from apps.organizations.models import Organization

print('=' * 80)
print('VERIFICACIÓN DE CONCEPTOS DE NÓMINA')
print('=' * 80)

total_dev = AccrualConcept.objects.count()
total_ded = DeductionConcept.objects.count()

print(f'\nTotal Devengados: {total_dev}')
print(f'Total Deducciones: {total_ded}')

# Ver primeras 5 deducciones
print('\n--- Primeras 5 deducciones ---')
for d in DeductionConcept.objects.all()[:5]:
    org_name = d.organization.name if d.organization else 'SIN ORG'
    print(f'  {d.codigo} - {d.nombre} - Org: {org_name}')

# Ver organizaciones
print('\n--- Organizaciones ---')
for org in Organization.objects.all()[:5]:
    dev_count = AccrualConcept.objects.filter(organization=org).count()
    ded_count = DeductionConcept.objects.filter(organization=org).count()
    print(f'  {org.name}: {dev_count} devengados, {ded_count} deducciones')

# Ver deducciones sin organización
sin_org = DeductionConcept.objects.filter(organization__isnull=True).count()
print(f'\nDeducciones SIN organización: {sin_org}')
