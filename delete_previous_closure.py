"""
Script para eliminar el cierre de caja anterior y permitir crear uno nuevo
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.cash_register.models import CashRegister, CashClosure
from django.utils import timezone

# Obtener la caja principal
caja = CashRegister.objects.get(name="Caja Principal")
today = timezone.now().date()

# Buscar cierres de hoy
cierres_hoy = CashClosure.objects.filter(
    cash_register=caja,
    closure_date=today
)

print(f"=== CIERRES DE CAJA: {caja.name} - {today} ===\n")

if cierres_hoy.exists():
    print(f"Se encontraron {cierres_hoy.count()} cierre(s) para hoy:")
    for cierre in cierres_hoy:
        print(f"\n  ID: {cierre.id}")
        print(f"  Fecha: {cierre.closure_date}")
        print(f"  Estado: {cierre.get_status_display()}")
        print(f"  Esperado: ${cierre.expected_amount:,.2f}")
        print(f"  Contado: ${cierre.total_counted:,.2f}")
        print(f"  Diferencia: ${cierre.difference:,.2f}")
        print(f"  Creado: {cierre.created_at.strftime('%H:%M:%S')}")
    
    print(f"\n🗑️  Eliminando cierre(s) anterior(es)...")
    count = cierres_hoy.count()
    cierres_hoy.delete()
    print(f"✅ {count} cierre(s) eliminado(s)")
    print(f"\n✨ Ahora puedes cerrar la caja nuevamente")
else:
    print("No hay cierres registrados para hoy.")
    print("El error puede ser de otra causa.")
