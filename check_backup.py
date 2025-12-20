import json

# Leer backup
with open('backup_final.json', 'r', encoding='latin-1') as f:
    data = json.load(f)

# Buscar usuarios
users = [r for r in data if r['model'] == 'auth.user']
print(f'Total usuarios en backup: {len(users)}')
print('\n👥 USUARIOS EN BACKUP:')
for u in users:
    print(f"  - {u['fields']['username']}: {u['fields'].get('first_name', '')} {u['fields'].get('last_name', '')} ({u['fields'].get('email', '')})")

# Buscar Julio Zapata
print('\n🔍 BÚSQUEDA DE JULIO ZAPATA:')
for u in users:
    full = f"{u['fields'].get('first_name', '')} {u['fields'].get('last_name', '')}".lower()
    if 'julio' in full or 'zapata' in full:
        print(f"  ✅ {u['fields']['username']}: {u['fields'].get('first_name', '')} {u['fields'].get('last_name', '')}")

# Buscar planes
plans = [r for r in data if r['model'] == 'subscriptions.plan']
print(f'\n📋 PLANES EN BACKUP: {len(plans)}')
for p in plans:
    print(f"  - {p['fields']['name']}: ${p['fields'].get('monthly_price', 0)}/mes")

# Buscar suscripciones
subs = [r for r in data if r['model'] == 'subscriptions.subscription']
print(f'\n💳 SUSCRIPCIONES EN BACKUP: {len(subs)}')
for s in subs:
    print(f"  - Org ID: {s['fields'].get('organization')}, Plan ID: {s['fields'].get('plan')}, Status: {s['fields'].get('status')}")

# Buscar organizaciones
orgs = [r for r in data if r['model'] == 'organizations.organization']
print(f'\n🏢 ORGANIZACIONES EN BACKUP: {len(orgs)}')
for o in orgs:
    print(f"  - {o['fields']['name']} (ID: {o.get('pk')})")
