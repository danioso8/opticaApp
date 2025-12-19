"""
Script para limpiar el backup y asegurar UTF-8 correcto
"""
import json

# Leer el backup original
with open('backup_clean.json', 'rb') as f:
    content = f.read()

# Intentar decodificar con diferentes encodings
for encoding in ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']:
    try:
        text = content.decode(encoding)
        data = json.loads(text)
        print(f"✓ Decodificado exitosamente con {encoding}")
        print(f"  Registros: {len(data)}")
        
        # Re-escribir con UTF-8 puro y ASCII escapado
        with open('backup_final.json', 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=True, indent=2)
        
        print("✓ Backup final creado: backup_final.json")
        break
    except Exception as e:
        print(f"✗ Error con {encoding}: {e}")
