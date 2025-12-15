#!/usr/bin/env bash
# exit on error
set -o errexit

echo "==> Instalando dependencias..."
pip install -r requirements.txt

echo "==> Recolectando archivos estáticos..."
python manage.py collectstatic --no-input

echo "==> Verificando estado de migraciones..."
# Ejecutar script de verificación automática antes de las migraciones
python pre_migrate_check.py || true

echo "==> Aplicando migraciones..."
# Marcar migración 0016 como fake si existe (evita error de triggers en PostgreSQL)
python manage.py migrate patients 0016_auto_20251210_1329 --fake --noinput || true

# Verificar y corregir migraciones problemáticas de appointments
echo "==> Verificando migraciones de appointments..."
python manage.py shell << END
from django.db import connection
import os

def check_column_exists(table, column):
    with connection.cursor() as cursor:
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name=%s AND column_name=%s", [table, column])
        return cursor.fetchone() is not None

def check_constraint_exists(constraint_name):
    with connection.cursor() as cursor:
        cursor.execute("SELECT constraint_name FROM information_schema.table_constraints WHERE constraint_name=%s", [constraint_name])
        return cursor.fetchone() is not None

# Verificar migración 0011 (campos companion)
if check_column_exists('appointments_appointment', 'companion_name'):
    print('✅ Columnas companion ya existen, marcando 0011 como fake...')
    os.system('python manage.py migrate appointments 0011 --fake --noinput || true')

# Verificar migración 0012 (constraint unique_active_appointment_slot)
if check_constraint_exists('unique_active_appointment_slot'):
    print('✅ Constraint unique_active_appointment_slot ya existe, marcando 0012 como fake...')
    os.system('python manage.py migrate appointments 0012 --fake --noinput || true')

print('✅ Verificaciones completadas')
END

# Aplicar todas las migraciones
python manage.py migrate --noinput

echo "==> Creando superusuario..."
python manage.py shell << END
from django.contrib.auth import get_user_model
User = get_user_model()
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser('admin', 'admin@oceanooptico.com', 'admin123')
    print('✓ Superusuario creado: admin / admin123')
else:
    print('✓ Superusuario ya existe')
END

echo "==> Build completado exitosamente ✓"
