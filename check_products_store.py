#!/usr/bin/env python
"""
Script para verificar los productos y su configuración de tienda
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.billing.models import InvoiceProduct

print("=" * 60)
print("ESTADO DE PRODUCTOS - TIENDA ONLINE")
print("=" * 60)

total = InvoiceProduct.objects.count()
activos = InvoiceProduct.objects.filter(is_active=True).count()
en_tienda = InvoiceProduct.objects.filter(show_in_store=True).count()

print(f"\n📦 Total productos: {total}")
print(f"✅ Productos activos: {activos}")
print(f"🏪 Productos en tienda: {en_tienda}")

# Mostrar algunos productos
print("\n" + "=" * 60)
print("PRIMEROS 10 PRODUCTOS")
print("=" * 60)

productos = InvoiceProduct.objects.all()[:10]
for p in productos:
    tienda_icon = "🏪" if p.show_in_store else "❌"
    activo_icon = "✅" if p.is_active else "🔴"
    print(f"{tienda_icon} {activo_icon} [{p.codigo}] {p.nombre} - ${p.precio_venta}")

print("\n" + "=" * 60)
