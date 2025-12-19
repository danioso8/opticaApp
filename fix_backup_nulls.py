"""
Script para arreglar valores NULL en el backup antes de importar
"""
import json

print("Cargando backup...")
with open('backup_final.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

print(f"Total registros: {len(data)}")

# Campos que necesitan valores por defecto
sphere_fields = [
    'refraction_od_sphere', 'refraction_os_sphere',
    'current_rx_od_sphere', 'current_rx_os_sphere'
]

fixed_count = 0
for item in data:
    if item['model'] == 'patients.clinicalhistory':
        fields = item['fields']
        
        # Arreglar campos sphere que son NULL
        for field in sphere_fields:
            if field in fields and fields[field] is None:
                fields[field] = 'N'  # Valor por defecto: "N" (No aplica)
                fixed_count += 1

print(f"✓ Registros corregidos: {fixed_count}")

# Guardar backup corregido
print("Guardando backup corregido...")
with open('backup_fixed.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=True, indent=2)

print("✓ Backup guardado: backup_fixed.json")
print("\nAhora ejecuta en Render:")
print("  python manage.py loaddata backup_fixed.json")
