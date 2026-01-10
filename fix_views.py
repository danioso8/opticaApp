import re

files = [
    'apps/workflows/views.py',
    'apps/tasks/views.py',
    'apps/reports/views.py',
    'apps/audit/views.py'
]

for file_path in files:
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Eliminar líneas con @organization_required
        content = re.sub(r'^@organization_required\n', '', content, flags=re.MULTILINE)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"✓ Fixed {file_path}")
    except Exception as e:
        print(f"✗ Error in {file_path}: {e}")

print("\nDone!")
