#!/usr/bin/env python3
import os

os.chdir('/var/www/opticaapp')

with open('config/urls.py', 'r') as f:
    content = f.read()

# Corregir línea mal formateada
old_line = 'path(" payments/, include(pps.payments.urls)),'
new_line = '    path("payments/", include("apps.payments.urls")),'

content = content.replace(old_line, new_line)

with open('config/urls.py', 'w') as f:
    f.write(content)

print('Corregido')
