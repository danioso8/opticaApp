"""
Test para verificar que las restricciones de unicidad funcionan correctamente.
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.billing.models import InvoiceConfiguration, DianConfiguration
from apps.organizations.models import Organization
from django.db import IntegrityError

def test_invoice_config_uniqueness():
    """Prueba que no se puedan crear múltiples InvoiceConfiguration para una organización."""
    print("=" * 80)
    print("🧪 TEST: Restricción de unicidad InvoiceConfiguration")
    print("=" * 80)
    print()
    
    org = Organization.objects.first()
    if not org:
        print("❌ No hay organizaciones para probar")
        return False
    
    print(f"📋 Organización de prueba: {org.name}")
    
    # Intentar obtener o crear la configuración (debería funcionar)
    config1, created = InvoiceConfiguration.objects.get_or_create(organization=org)
    print(f"✅ Primera configuración: {'Creada' if created else 'Ya existía'} (ID: {config1.id})")
    
    # Intentar crear otra configuración directamente (debería fallar)
    try:
        config2 = InvoiceConfiguration(organization=org)
        config2.save()
        print("❌ ERROR: Se permitió crear una segunda configuración (no debería ocurrir)")
        return False
    except IntegrityError as e:
        print(f"✅ Restricción funcionó correctamente: No se permite duplicados")
        print(f"   Error capturado: {str(e)[:100]}...")
        return True


def test_dian_config_uniqueness():
    """Prueba que no se puedan crear múltiples DianConfiguration para una organización."""
    print()
    print("=" * 80)
    print("🧪 TEST: Restricción de unicidad DianConfiguration")
    print("=" * 80)
    print()
    
    org = Organization.objects.first()
    if not org:
        print("❌ No hay organizaciones para probar")
        return False
    
    print(f"📋 Organización de prueba: {org.name}")
    
    # Intentar obtener o crear la configuración (debería funcionar)
    from django.contrib.auth.models import User
    admin_user = User.objects.filter(is_staff=True).first()
    
    config1, created = DianConfiguration.objects.get_or_create(
        organization=org,
        defaults={'configurado_por': admin_user}
    )
    print(f"✅ Primera configuración: {'Creada' if created else 'Ya existía'} (ID: {config1.id})")
    
    # Intentar crear otra configuración directamente (debería fallar)
    try:
        config2 = DianConfiguration(
            organization=org,
            configurado_por=admin_user
        )
        config2.save()
        print("❌ ERROR: Se permitió crear una segunda configuración (no debería ocurrir)")
        return False
    except IntegrityError as e:
        print(f"✅ Restricción funcionó correctamente: No se permite duplicados")
        print(f"   Error capturado: {str(e)[:100]}...")
        return True


def main():
    print()
    print("╔" + "=" * 78 + "╗")
    print("║" + " " * 22 + "TEST DE RESTRICCIONES DE UNICIDAD" + " " * 23 + "║")
    print("╚" + "=" * 78 + "╝")
    print()
    
    # Test InvoiceConfiguration
    test1_passed = test_invoice_config_uniqueness()
    
    # Test DianConfiguration
    test2_passed = test_dian_config_uniqueness()
    
    # Resultado final
    print()
    print("=" * 80)
    print("📊 RESULTADOS DE LAS PRUEBAS")
    print("=" * 80)
    print()
    
    if test1_passed and test2_passed:
        print("✅ TODOS LOS TESTS PASARON")
        print()
        print("🎉 Las restricciones de unicidad están funcionando correctamente")
        print("   - No se pueden crear múltiples InvoiceConfiguration por organización")
        print("   - No se pueden crear múltiples DianConfiguration por organización")
        print("   - Siempre usar get_or_create() para obtener/crear configuraciones")
    else:
        print("❌ ALGUNOS TESTS FALLARON")
        print()
        print("⚠️  Revisar las restricciones en los modelos y migraciones")
    
    print()


if __name__ == '__main__':
    main()
