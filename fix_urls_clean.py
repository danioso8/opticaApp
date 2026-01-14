#!/usr/bin/env python3
import os

os.chdir('/var/www/opticaapp')

# Restaurar desde backup
if os.path.exists('config/urls.py.backup_payments'):
    with open('config/urls.py.backup_payments', 'r') as f:
        lines = f.readlines()
else:
    print("ERROR: No hay backup")
    exit(1)

# Buscar línea de cash_register y agregar después
new_lines = []
found = False

for line in lines:
    new_lines.append(line)
    if "path('dashboard/cash/', include('apps.cash_register.urls'))," in line and not found:
        new_lines.append('\n')
        new_lines.append('    # Payments URLs (Módulos À la Carte)\n')
        new_lines.append('    path("payments/", include("apps.payments.urls")),\n')
        found = True

# Escribir archivo
with open('config/urls.py', 'w') as f:
    f.writelines(new_lines)

print('✅ Archivo restaurado y actualizado correctamente')
