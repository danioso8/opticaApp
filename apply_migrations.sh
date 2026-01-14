#!/bin/bash
cd /var/www/opticaapp
source venv/bin/activate
python manage.py migrate payments
python manage.py migrate
echo "Migraciones completadas"
