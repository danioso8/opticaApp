"""
Script para corregir el saldo de la caja automáticamente
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.cash_register.models import CashRegister, CashMovement
from decimal import Decimal
from django.utils import timezone

# Obtener la caja principal
caja = CashRegister.objects.get(name="Caja Principal")

print(f"=== CORRECCIÓN DE SALDO: {caja.name} ===\n")
print(f"Saldo actual INCORRECTO: ${caja.current_balance:,.2f}")
print(f"Monto de apertura: ${caja.opening_amount:,.2f}")

# Calcular el saldo correcto basado en movimientos del día de hoy
today = timezone.now().date()

movimientos_hoy = CashMovement.objects.filter(
    cash_register=caja,
    created_at__date=today,
    is_deleted=False
).exclude(movement_type='OPENING').order_by('created_at')

print(f"\nMovimientos del día ({today}):")
saldo_calculado = caja.opening_amount
for mov in movimientos_hoy:
    signo = "+" if mov.movement_type == 'INCOME' else "-"
    print(f"  {mov.created_at.strftime('%H:%M')} - {mov.get_movement_type_display()}: {signo}${mov.amount:,.2f}")
    if mov.movement_type == 'INCOME':
        saldo_calculado += mov.amount
    else:
        saldo_calculado -= mov.amount

print(f"\n📊 ANÁLISIS:")
print(f"  Saldo calculado CORRECTO: ${saldo_calculado:,.2f}")
print(f"  Saldo actual en sistema: ${caja.current_balance:,.2f}")
print(f"  Diferencia a corregir: ${caja.current_balance - saldo_calculado:,.2f}")

# Corregir automáticamente
print(f"\n🔧 Aplicando corrección...")
caja.current_balance = saldo_calculado
caja.save()
print(f"✅ Saldo corregido exitosamente a ${saldo_calculado:,.2f}")
print(f"\n✨ Ahora tu caja muestra el saldo correcto!")
