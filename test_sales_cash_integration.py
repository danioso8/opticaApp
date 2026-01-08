"""
Script de prueba para verificar la integración automática Ventas → Caja
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.sales.models import Sale
from apps.cash_register.models import CashRegister, CashMovement
from apps.patients.models import Patient
from apps.organizations.models import Organization
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone

print("=" * 60)
print("PRUEBA DE INTEGRACIÓN AUTOMÁTICA: VENTAS → CAJA")
print("=" * 60)

# Obtener organización y usuario
org = Organization.objects.first()
user = User.objects.first()

print(f"\n📊 ESTADO INICIAL:")
print(f"  Organización: {org.name}")
print(f"  Usuario: {user.username}")

# Verificar estado de la caja
caja = CashRegister.objects.filter(
    organization=org,
    name="Caja Principal"
).first()

if caja:
    print(f"\n💰 CAJA PRINCIPAL:")
    print(f"  Estado: {caja.get_status_display()}")
    print(f"  Saldo: ${caja.current_balance:,.2f}")
    
    if caja.status == 'CLOSED':
        print(f"\n⚠️  La caja está CERRADA")
        print(f"  ✅ La venta debería crearse SIN registrar movimiento en caja")
    else:
        print(f"\n✅ La caja está ABIERTA")
        print(f"  ✅ La venta debería registrar movimiento automáticamente")
else:
    print(f"\n⚠️  No hay caja registrada")
    print(f"  ✅ La venta debería crearse SIN registrar movimiento en caja")

# Contar movimientos actuales
movimientos_antes = CashMovement.objects.filter(
    organization=org,
    created_at__date=timezone.now().date()
).count()

print(f"\n📝 Movimientos en caja HOY: {movimientos_antes}")

# PRUEBA 1: Venta en EFECTIVO
print(f"\n" + "=" * 60)
print(f"PRUEBA 1: Crear venta en EFECTIVO")
print("=" * 60)

venta_efectivo = Sale.objects.create(
    organization=org,
    sale_number=f"TEST-{timezone.now().strftime('%Y%m%d%H%M%S')}",
    customer_name="Cliente de Prueba",
    sold_by=user,
    payment_method='cash',
    status='completed',
    subtotal=Decimal('50000.00'),
    total=Decimal('50000.00')
)

print(f"✅ Venta creada: {venta_efectivo.sale_number}")
print(f"  Total: ${venta_efectivo.total:,.2f}")
print(f"  Método de pago: {venta_efectivo.get_payment_method_display()}")

# Verificar si se creó movimiento
movimiento = CashMovement.objects.filter(
    sale=venta_efectivo
).first()

if movimiento:
    print(f"\n✅ MOVIMIENTO DE CAJA CREADO AUTOMÁTICAMENTE:")
    print(f"  Monto: ${movimiento.amount:,.2f}")
    print(f"  Caja: {movimiento.cash_register.name}")
    print(f"  Categoría: {movimiento.get_category_display()}")
    print(f"  Referencia: {movimiento.reference}")
else:
    print(f"\n⚠️  NO se creó movimiento de caja (esperado si la caja está cerrada)")

# PRUEBA 2: Venta con TARJETA
print(f"\n" + "=" * 60)
print(f"PRUEBA 2: Crear venta con TARJETA")
print("=" * 60)

venta_tarjeta = Sale.objects.create(
    organization=org,
    sale_number=f"TEST-{timezone.now().strftime('%Y%m%d%H%M%S')}-T",
    customer_name="Cliente Tarjeta",
    sold_by=user,
    payment_method='card',
    status='completed',
    subtotal=Decimal('100000.00'),
    total=Decimal('100000.00')
)

print(f"✅ Venta creada: {venta_tarjeta.sale_number}")
print(f"  Total: ${venta_tarjeta.total:,.2f}")
print(f"  Método de pago: {venta_tarjeta.get_payment_method_display()}")

# Verificar que NO se creó movimiento
movimiento_tarjeta = CashMovement.objects.filter(
    sale=venta_tarjeta
).first()

if movimiento_tarjeta:
    print(f"\n❌ ERROR: Se creó movimiento para venta con tarjeta (no debería)")
else:
    print(f"\n✅ Correcto: NO se creó movimiento (venta con tarjeta no va a caja física)")

# Verificar estado final
movimientos_despues = CashMovement.objects.filter(
    organization=org,
    created_at__date=timezone.now().date()
).count()

print(f"\n📊 RESUMEN FINAL:")
print(f"  Movimientos antes: {movimientos_antes}")
print(f"  Movimientos después: {movimientos_despues}")
print(f"  Nuevos movimientos: {movimientos_despues - movimientos_antes}")

if caja and caja.status == 'OPEN':
    caja.refresh_from_db()
    print(f"  Saldo final de caja: ${caja.current_balance:,.2f}")

print(f"\n" + "=" * 60)
print(f"✅ PRUEBAS COMPLETADAS")
print("=" * 60)

print(f"\n💡 PARA LIMPIAR LAS VENTAS DE PRUEBA:")
print(f"   python manage.py shell")
print(f"   >>> Sale.objects.filter(sale_number__startswith='TEST-').delete()")
