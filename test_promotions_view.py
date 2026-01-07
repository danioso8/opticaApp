"""
Script para detectar el error en la vista de promociones
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
request = factory.get('/dashboard/promociones/')

# Obtener un usuario
user = User.objects.first()
request.user = user
request.organization = Organization.objects.first()

print(f"✅ Usuario: {user.username}")
print(f"✅ Organización: {request.organization.name}")

# Intentar cargar la vista
try:
    from apps.promotions import views
    print("\n🔍 Intentando cargar promotion_list...")
    response = views.promotion_list(request)
    print(f"✅ Vista cargada correctamente. Status: {response.status_code}")
except Exception as e:
    print(f"\n❌ ERROR AL CARGAR LA VISTA:")
    print(f"Tipo: {type(e).__name__}")
    print(f"Mensaje: {str(e)}")
    import traceback
    print("\n📋 Traceback completo:")
    traceback.print_exc()
