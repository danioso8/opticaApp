"""
Prueba 2: Venta con caja ABIERTA
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.sales.models import Sale
from apps.cash_register.models import CashRegister, CashMovement
from apps.organizations.models import Organization
from django.contrib.auth.models import User
from decimal import Decimal
from django.utils import timezone

org = Organization.objects.first()
user = User.objects.first()
caja = CashRegister.objects.get(name="Caja Principal")

print("=" * 60)
print("PRUEBA CON CAJA ABIERTA")
print("=" * 60)

# Abrir la caja
if caja.status == 'CLOSED':
    print(f"\n🔓 Abriendo caja...")
    caja.open_register(user, Decimal('100000.00'))
    print(f"✅ Caja abierta con saldo inicial: ${caja.current_balance:,.2f}")
else:
    print(f"\n✅ La caja ya está abierta")
    print(f"  Saldo actual: ${caja.current_balance:,.2f}")

# Crear venta en efectivo
print(f"\n💵 Creando venta en EFECTIVO...")
venta = Sale.objects.create(
    organization=org,
    sale_number=f"VENTA-{timezone.now().strftime('%Y%m%d%H%M%S')}",
    customer_name="Cliente Test con Caja Abierta",
    sold_by=user,
    payment_method='cash',
    status='completed',
    subtotal=Decimal('75000.00'),
    total=Decimal('75000.00')
)

print(f"✅ Venta creada: {venta.sale_number}")
print(f"  Total: ${venta.total:,.2f}")

# Verificar movimiento
movimiento = CashMovement.objects.filter(sale=venta).first()

if movimiento:
    print(f"\n✅ ¡ÉXITO! Movimiento de caja creado automáticamente:")
    print(f"  Caja: {movimiento.cash_register.name}")
    print(f"  Monto: ${movimiento.amount:,.2f}")
    print(f"  Categoría: {movimiento.get_category_display()}")
    print(f"  Descripción: {movimiento.description}")
    
    # Verificar saldo
    caja.refresh_from_db()
    print(f"\n💰 Saldo actualizado de caja: ${caja.current_balance:,.2f}")
else:
    print(f"\n❌ ERROR: No se creó movimiento de caja")

print(f"\n" + "=" * 60)
