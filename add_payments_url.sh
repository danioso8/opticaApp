#!/bin/bash
cd /var/www/opticaapp

# Hacer backup
cp config/urls.py config/urls.py.backup_payments

# Buscar la línea de Cash Register y agregar después
sed -i '/path.*cash_register.urls/a\    \n    # Payments URLs (Módulos À la Carte)\n    path(\"payments/\", include(\"apps.payments.urls\")),' config/urls.py

echo "✅ Ruta de payments agregada"
