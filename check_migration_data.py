import json

with open('d:/ESCRITORIO/OpticaApp/migration_data.json', encoding='utf-8') as f:
    data = json.load(f)

users = [x for x in data if x.get('model') == 'auth.user']
orgs = [x for x in data if x.get('model') == 'organizations.organization']
patients = [x for x in data if x.get('model') == 'patients.patient']

print(f'\n=== MIGRATION_DATA.JSON ===')
print(f'Total objetos: {len(data)}')
print(f'Usuarios: {len(users)}')
print(f'Organizaciones: {len(orgs)}')
print(f'Pacientes: {len(patients)}')

if users:
    print('\nUSUARIOS:')
    for u in users:
        print(f"  ID: {u['pk']} - {u['fields']['username']} ({u['fields']['email']})")
