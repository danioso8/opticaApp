#!/bin/bash
cd /var/www/opticaapp
source venv/bin/activate
python manage.py shell << 'PYEOF'
from apps.organizations.models import Organization
print('\nOrganizaciones disponibles:')
for o in Organization.objects.all():
    print(f'ID: {o.id} - {o.name}')
PYEOF
