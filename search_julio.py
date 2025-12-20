import json

# Leer backup
with open('backup_final.json', 'r', encoding='latin-1') as f:
    data = json.load(f)

# Ver todos los modelos
models = {}
for r in data:
    model = r['model']
    if model not in models:
        models[model] = 0
    models[model] += 1

print('📦 MODELOS EN BACKUP:')
for model, count in sorted(models.items()):
    print(f"  - {model}: {count}")

# Buscar cualquier registro con "julio" o "zapata"
print('\n🔍 BÚSQUEDA DE "JULIO" O "ZAPATA" EN TODOS LOS CAMPOS:')
found = []
for r in data:
    # Convertir todo a string y buscar
    json_str = json.dumps(r['fields']).lower()
    if 'julio' in json_str or 'zapata' in json_str:
        found.append(r)
        print(f"\n✅ Encontrado en {r['model']} (PK: {r.get('pk')}):")
        if r['model'] == 'patients.patient':
            print(f"   Nombre: {r['fields'].get('full_name')}")
            print(f"   ID: {r['fields'].get('identification')}")
        elif r['model'] == 'patients.doctor':
            print(f"   Nombre: {r['fields'].get('full_name')}")
            print(f"   Especialidad: {r['fields'].get('specialty')}")
        else:
            print(f"   Campos: {r['fields']}")

print(f"\n📊 Total registros con 'julio' o 'zapata': {len(found)}")
