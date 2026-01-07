"""
Script para detectar el error en el dashboard
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from apps.organizations.models import Organization

User = get_user_model()

# Crear un request de prueba
factory = RequestFactory()
request = factory.get('/dashboard/')

# Obtener un usuario
user = User.objects.first()
if not user:
    print("❌ No hay usuarios en la base de datos")
    exit()

print(f"✅ Usuario encontrado: {user.username}")

# Obtener una organización
try:
    org = Organization.objects.first()
    if org:
        print(f"✅ Organización encontrada: {org.name}")
        request.organization = org
    else:
        print("⚠️ No hay organizaciones")
        request.organization = None
except Exception as e:
    print(f"❌ Error al obtener organización: {e}")
    request.organization = None

request.user = user

# Intentar cargar la vista
try:
    from apps.dashboard import views
    print("\n🔍 Intentando cargar dashboard_home...")
    response = views.dashboard_home(request)
    print(f"✅ Vista cargada correctamente. Status: {response.status_code}")
except Exception as e:
    print(f"\n❌ ERROR AL CARGAR LA VISTA:")
    print(f"Tipo: {type(e).__name__}")
    print(f"Mensaje: {str(e)}")
    import traceback
    print("\n📋 Traceback completo:")
    traceback.print_exc()
