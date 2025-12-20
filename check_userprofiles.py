import json

with open('backup_final.json', 'r', encoding='latin-1') as f:
    backup_data = json.load(f)

print("=" * 80)
print("USERPROFILES EN BACKUP (DETALLADO)")
print("=" * 80)

for item in backup_data:
    if item['model'] == 'users.userprofile':
        print(f"\nUserProfile PK: {item['pk']}")
        fields = item['fields']
        for key, value in fields.items():
            print(f"  {key}: {value}")
