"""
Script para probar la vista home en el shell y ver el error exacto
"""

from django.test import RequestFactory
from apps.public.views import home

# Crear un request falso
factory = RequestFactory()
request = factory.get('/')

try:
    response = home(request)
    print(f"✅ Vista funciona! Status: {response.status_code}")
except Exception as e:
    print(f"❌ Error encontrado:")
    print(f"Tipo: {type(e).__name__}")
    print(f"Mensaje: {str(e)}")
    import traceback
    print("\nTraceback completo:")
    traceback.print_exc()
