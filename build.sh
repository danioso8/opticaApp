#!/usr/bin/env bash
# exit on error
set -o errexit

echo "==> Instalando dependencias..."
pip install -r requirements.txt

echo "==> Recolectando archivos estáticos..."
python manage.py collectstatic --no-input

echo "==> Aplicando migraciones..."
# Marcar migración 0016 como fake si existe (evita error de triggers en PostgreSQL)
python manage.py migrate patients 0016_auto_20251210_1329 --fake --noinput || true
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
