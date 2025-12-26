#!/usr/bin/env bash
# exit on error
set -o errexit

echo "==> Instalando dependencias..."
pip install -r requirements.txt

echo "==> Recolectando archivos estáticos..."
python manage.py collectstatic --no-input

echo "==> Inicializando disco persistente..."
chmod +x init_render_disk.sh
./init_render_disk.sh || true

echo "==> Verificando estado de migraciones..."
# Ejecutar script de verificación automática antes de las migraciones
python pre_migrate_check.py || true

echo "==> Aplicando migraciones..."
# Ejecutar script de reparación de migraciones (incluye sphere fix)
python fix_render_migrations_sphere.py || true

# Aplicar todas las migraciones (--fake-initial marca como fake las migraciones iniciales si las tablas ya existen)
python manage.py migrate --fake-initial --noinput

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
