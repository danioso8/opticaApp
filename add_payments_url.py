#!/usr/bin/env python3
import os

os.chdir('/var/www/opticaapp')

# Leer archivo
with open('config/urls.py', 'r') as f:
    lines = f.readlines()

# Hacer backup
with open('config/urls.py.backup_payments', 'w') as f:
    f.writelines(lines)

# Buscar línea de cash_register y agregar después
new_lines = []
found = False

for line in lines:
    new_lines.append(line)
    if 'cash_register.urls' in line and not found:
        new_lines.append('\n')
        new_lines.append('    # Payments URLs (Módulos À la Carte)\n')
        new_lines.append('    path("payments/", include("apps.payments.urls")),\n')
        found = True
        print('✅ Agregada ruta de payments después de cash_register')

# Escribir archivo
with open('config/urls.py', 'w') as f:
    f.writelines(new_lines)

print('✅ Archivo actualizado correctamente')
