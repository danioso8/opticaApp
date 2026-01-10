import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'opticaapp.settings')
django.setup()

from apps.organizations.models import Organization
from apps.payroll.models import AccrualConcept, DeductionConcept

print('\n📊 RESUMEN DE CONCEPTOS POR ORGANIZACIÓN:\n')
print('=' * 60)

orgs = Organization.objects.all()
for org in orgs:
    devengados = AccrualConcept.objects.filter(organization=org).count()
    deducciones = DeductionConcept.objects.filter(organization=org).count()
    print(f'\n🏢 {org.name}:')
    print(f'   ✓ Devengados: {devengados}')
    print(f'   ✓ Deducciones: {deducciones}')
    print(f'   Total: {devengados + deducciones}')

print('\n' + '=' * 60)
print(f'Total organizaciones: {orgs.count()}')
print('=' * 60)
