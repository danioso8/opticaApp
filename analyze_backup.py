import json

print("ANALIZANDO BACKUP backup_final.json")
print("=" * 80)

with open('backup_final.json', 'r', encoding='latin-1') as f:
    backup_data = json.load(f)

# Contar modelos
models_count = {}
for item in backup_data:
    model = item['model']
    models_count[model] = models_count.get(model, 0) + 1

print("\nCONTENIDO DEL BACKUP:")
for model, count in sorted(models_count.items()):
    print(f"  {model}: {count}")

# Buscar Julio Zapata
print("\n" + "=" * 80)
print("BUSCANDO 'JULIO ZAPATA'")
print("=" * 80)

for item in backup_data:
    if item['model'] == 'auth.user':
        fields = item['fields']
        username = fields.get('username', '').lower()
        first_name = fields.get('first_name', '').lower()
        last_name = fields.get('last_name', '').lower()
        full_text = username + ' ' + first_name + ' ' + last_name
        
        if 'julio' in full_text or 'zapata' in full_text:
            print(f"\n✅ USUARIO ENCONTRADO:")
            print(f"   PK: {item['pk']}")
            print(f"   Username: {fields.get('username')}")
            print(f"   Nombre: {fields.get('first_name')} {fields.get('last_name')}")
            print(f"   Email: {fields.get('email')}")
            print(f"   is_staff: {fields.get('is_staff')}")
            print(f"   is_superuser: {fields.get('is_superuser')}")
            print(f"   is_active: {fields.get('is_active')}")

# Mostrar todos los usuarios
print("\n" + "=" * 80)
print("TODOS LOS USUARIOS EN BACKUP")
print("=" * 80)

for item in backup_data:
    if item['model'] == 'auth.user':
        fields = item['fields']
        print(f"\n[{item['pk']}] {fields.get('username')}")
        print(f"    Nombre: {fields.get('first_name')} {fields.get('last_name')}")
        print(f"    Email: {fields.get('email')}")
        print(f"    Staff: {fields.get('is_staff')}, Superuser: {fields.get('is_superuser')}, Active: {fields.get('is_active')}")

# Mostrar planes
print("\n" + "=" * 80)
print("PLANES DE SUBSCRIPCIÓN EN BACKUP")
print("=" * 80)

for item in backup_data:
    if item['model'] == 'organizations.subscriptionplan':
        fields = item['fields']
        print(f"\n[{item['pk']}] {fields.get('name')}")
        print(f"    Precio: ${fields.get('price')}")
        print(f"    Límites: {fields.get('max_patients')} pacientes, {fields.get('max_users')} usuarios")
        print(f"    Activo: {fields.get('is_active')}")

# Mostrar subscripciones
print("\n" + "=" * 80)
print("SUBSCRIPCIONES EN BACKUP")
print("=" * 80)

for item in backup_data:
    if item['model'] == 'organizations.subscription':
        fields = item['fields']
        print(f"\n[{item['pk']}] Organización: {fields.get('organization')}, Plan: {fields.get('plan')}")
        print(f"    Estado: {fields.get('status')}")
        print(f"    Fecha inicio: {fields.get('start_date')}")
        print(f"    Fecha fin: {fields.get('end_date')}")
        print(f"    Auto-renovar: {fields.get('auto_renew')}")

print("\n" + "=" * 80)
print("RESUMEN")
print("=" * 80)
print(f"Total registros en backup: {len(backup_data)}")
for model, count in sorted(models_count.items()):
    print(f"  {model}: {count}")
