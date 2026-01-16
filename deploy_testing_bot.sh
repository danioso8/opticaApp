#!/bin/bash

echo "🚀 DEPLOYMENT BOT DE TESTING"
echo "========================================"
echo ""

# 1. Subir archivos
echo "📤 1. Subiendo archivos..."
scp -r apps/testing root@84.247.129.180:/var/www/opticaapp/apps/
scp config/urls.py root@84.247.129.180:/var/www/opticaapp/config/

# 2. Agregar app a INSTALLED_APPS
echo "⚙️  2. Configurando INSTALLED_APPS..."
ssh root@84.247.129.180 "cd /var/www/opticaapp && source venv/bin/activate && python -c \"
import re
with open('config/settings.py', 'r') as f:
    content = f.read()
if 'apps.testing' not in content:
    # Agregar antes de la última app
    content = content.replace(
        '    \\\'apps.audit\\\',',
        '    \\\'apps.audit\\\',\\n    \\\'apps.testing\\\','
    )
    with open('config/settings.py', 'w') as f:
        f.write(content)
    print('✅ App agregada a INSTALLED_APPS')
else:
    print('✅ App ya está en INSTALLED_APPS')
\""

# 3. Crear migraciones
echo "📝 3. Creando migraciones..."
ssh root@84.247.129.180 'cd /var/www/opticaapp && source venv/bin/activate && python manage.py makemigrations testing'

# 4. Aplicar migraciones
echo "🔄 4. Aplicando migraciones..."
ssh root@84.247.129.180 'cd /var/www/opticaapp && source venv/bin/activate && python manage.py migrate'

# 5. Reiniciar servidor
echo "♻️  5. Reiniciando servidor..."
ssh root@84.247.129.180 'pm2 restart opticaapp'

echo ""
echo "✅ DEPLOYMENT COMPLETADO"
echo "========================================"
echo ""
echo "Accede a: https://www.optikaapp.com/saas-admin/testing/"
echo ""
