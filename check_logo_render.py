"""
EJECUTAR ESTE SCRIPT EN EL SHELL DE RENDER
Para ejecutar: cat check_logo_render.py | python manage.py shell
"""

from apps.organizations.models import LandingPageConfig
from django.conf import settings
import os

print("=" * 60)
print("🔍 DIAGNÓSTICO DE CONFIGURACIÓN DE MEDIA")
print("=" * 60)

print(f"\n📁 CONFIGURACIÓN:")
print(f"   MEDIA_ROOT: {settings.MEDIA_ROOT}")
print(f"   MEDIA_URL: {settings.MEDIA_URL}")
print(f"   DEBUG: {settings.DEBUG}")

print(f"\n📂 VERIFICACIÓN DE CARPETAS:")
if os.path.exists(settings.MEDIA_ROOT):
    print(f"   ✅ MEDIA_ROOT existe")
    print(f"   📋 Contenido:")
    for root, dirs, files in os.walk(settings.MEDIA_ROOT):
        level = root.replace(settings.MEDIA_ROOT, '').count(os.sep)
        indent = ' ' * 4 * level
        print(f'{indent}{os.path.basename(root)}/')
        subindent = ' ' * 4 * (level + 1)
        for file in files:
            print(f'{subindent}{file}')
else:
    print(f"   ❌ MEDIA_ROOT NO existe")

print(f"\n🏢 CONFIGURACIONES DE LANDING PAGE:")
configs = LandingPageConfig.objects.all()
print(f"   Total: {configs.count()}")

for config in configs:
    print(f"\n   📌 {config.organization.name}")
    print(f"      ID: {config.id}")
    if config.logo:
        print(f"      ✅ Logo configurado")
        print(f"      📁 Path en DB: {config.logo.name}")
        print(f"      🔗 URL generada: {config.logo.url}")
        full_path = os.path.join(settings.MEDIA_ROOT, config.logo.name)
        print(f"      📂 Path completo: {full_path}")
        if os.path.exists(full_path):
            print(f"      ✅ Archivo existe físicamente")
            print(f"      📊 Tamaño: {os.path.getsize(full_path)} bytes")
        else:
            print(f"      ❌ Archivo NO existe físicamente")
    else:
        print(f"      ❌ Sin logo configurado en la base de datos")

print("\n" + "=" * 60)
print("FIN DEL DIAGNÓSTICO")
print("=" * 60)
