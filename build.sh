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

# Verificar y corregir migración 0011 de appointments (campos companion ya existen)
echo "==> Verificando migración 0011 de appointments..."
python manage.py shell << END
from django.db import connection
def check_column_exists(table, column):
    with connection.cursor() as cursor:
        cursor.execute("SELECT column_name FROM information_schema.columns WHERE table_name=%s AND column_name=%s", [table, column])
        return cursor.fetchone() is not None

# Verificar si las columnas companion_name, companion_relationship, companion_phone existen
if check_column_exists('appointments_appointment', 'companion_name'):
    print('✅ Las columnas de acompañante ya existen en la base de datos')
    print('✅ Marcando migración 0011 como fake...')
    import os
    os.system('python manage.py migrate appointments 0011 --fake --noinput || true')
else:
    print('⏭️ Columnas no existen, la migración se ejecutará normalmente')
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
