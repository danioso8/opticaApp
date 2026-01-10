"""
Verificar y activar el módulo products
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import PlanFeature

print("\n" + "="*70)
print("🔍 VERIFICANDO MÓDULO PRODUCTS")
print("="*70)

# Verificar products
products = PlanFeature.objects.filter(code='products').first()

if products:
    print(f"\n✅ Módulo 'products' encontrado:")
    print(f"   ID: {products.id}")
    print(f"   Nombre: {products.name}")
    print(f"   Categoría: {products.category}")
    print(f"   Activo: {products.is_active}")
    print(f"   Descripción: {products.description}")
    
    if not products.is_active:
        products.is_active = True
        products.save()
        print(f"\n✅ Módulo activado correctamente")
else:
    print(f"\n❌ Módulo 'products' NO encontrado")
    print("\nCreando módulo products...")
    products = PlanFeature.objects.create(
        code='products',
        name='Catálogo de Productos',
        description='Gestión de productos y catálogo',
        icon='fas fa-box',
        category='sales',
        is_active=True
    )
    print(f"✅ Módulo creado: {products.name}")

# Verificar que ahora aparezca en activos
total_activos = PlanFeature.objects.filter(is_active=True).count()
print(f"\n📊 Total módulos activos: {total_activos}")

print("\n" + "="*70)
print("✅ Verificación completada")
print("="*70 + "\n")
