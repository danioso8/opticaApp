"""
Script para crear datos de ejemplo de ventas
"""
import os
import django
import random
from datetime import datetime, timedelta
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.contrib.auth.models import User
from apps.sales.models import Category, Product, Sale, SaleItem
from apps.patients.models import Patient

print("Creando datos de ejemplo para el módulo de ventas...")

# Crear categorías
categories_data = [
    {'name': 'Monturas', 'description': 'Monturas y armazones para lentes'},
    {'name': 'Lentes', 'description': 'Lentes oftálmicos y de contacto'},
    {'name': 'Accesorios', 'description': 'Estuches, limpiadores y más'},
    {'name': 'Gafas de Sol', 'description': 'Gafas de sol de protección'},
]

categories = []
for cat_data in categories_data:
    category, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    categories.append(category)
    if created:
        print(f"✓ Categoría creada: {category.name}")

# Crear productos
products_data = [
    # Monturas
    {'name': 'Montura Ray-Ban Clásica', 'sku': 'MON-001', 'category': 0, 'price': 150000, 'cost': 80000, 'stock': 15},
    {'name': 'Montura Oakley Deportiva', 'sku': 'MON-002', 'category': 0, 'price': 200000, 'cost': 100000, 'stock': 10},
    {'name': 'Montura Gucci Fashion', 'sku': 'MON-003', 'category': 0, 'price': 350000, 'cost': 180000, 'stock': 8},
    {'name': 'Montura Infantil Flexible', 'sku': 'MON-004', 'category': 0, 'price': 80000, 'cost': 40000, 'stock': 20},
    
    # Lentes
    {'name': 'Lentes Monofocales', 'sku': 'LEN-001', 'category': 1, 'price': 120000, 'cost': 60000, 'stock': 30},
    {'name': 'Lentes Bifocales', 'sku': 'LEN-002', 'category': 1, 'price': 180000, 'cost': 90000, 'stock': 25},
    {'name': 'Lentes Progresivos', 'sku': 'LEN-003', 'category': 1, 'price': 280000, 'cost': 140000, 'stock': 20},
    {'name': 'Lentes de Contacto (Par)', 'sku': 'LEN-004', 'category': 1, 'price': 50000, 'cost': 25000, 'stock': 50},
    
    # Accesorios
    {'name': 'Estuche Rígido Premium', 'sku': 'ACC-001', 'category': 2, 'price': 25000, 'cost': 12000, 'stock': 40},
    {'name': 'Limpiador de Lentes 100ml', 'sku': 'ACC-002', 'category': 2, 'price': 15000, 'cost': 7000, 'stock': 60},
    {'name': 'Paño de Microfibra', 'sku': 'ACC-003', 'category': 2, 'price': 8000, 'cost': 3000, 'stock': 100},
    {'name': 'Cordón para Gafas', 'sku': 'ACC-004', 'category': 2, 'price': 12000, 'cost': 5000, 'stock': 35},
    
    # Gafas de Sol
    {'name': 'Gafas de Sol Ray-Ban Aviador', 'sku': 'SOL-001', 'category': 3, 'price': 220000, 'cost': 110000, 'stock': 12},
    {'name': 'Gafas de Sol Oakley Sport', 'sku': 'SOL-002', 'category': 3, 'price': 250000, 'cost': 125000, 'stock': 8},
    {'name': 'Gafas de Sol Polarizadas', 'sku': 'SOL-003', 'category': 3, 'price': 180000, 'cost': 90000, 'stock': 15},
]

products = []
for prod_data in products_data:
    product, created = Product.objects.get_or_create(
        sku=prod_data['sku'],
        defaults={
            'name': prod_data['name'],
            'category': categories[prod_data['category']],
            'price': Decimal(prod_data['price']),
            'cost': Decimal(prod_data['cost']),
            'stock': prod_data['stock'],
            'min_stock': 5
        }
    )
    products.append(product)
    if created:
        print(f"✓ Producto creado: {product.name}")

# Obtener usuarios y pacientes
users = list(User.objects.all())
patients = list(Patient.objects.all())

if not users:
    print("❌ No hay usuarios. Crea un superusuario primero.")
    exit()

# Crear ventas de ejemplo (últimos 60 días)
print("\nCreando ventas de ejemplo...")
sale_counter = 1

for i in range(60):
    # Número de ventas por día (aleatorio entre 1-5)
    num_sales = random.randint(1, 5)
    sale_date = datetime.now() - timedelta(days=59-i)
    
    for j in range(num_sales):
        # Crear venta
        sale = Sale.objects.create(
            sale_number=f'VTA-{sale_counter:06d}',
            patient=random.choice(patients) if patients and random.random() > 0.3 else None,
            customer_name=f'Cliente {random.randint(1, 100)}' if random.random() > 0.7 else '',
            sold_by=random.choice(users),
            payment_method=random.choice(['cash', 'card', 'transfer', 'mixed']),
            status='completed',
            created_at=sale_date
        )
        
        # Agregar items (1-4 productos por venta)
        num_items = random.randint(1, 4)
        selected_products = random.sample(products, min(num_items, len(products)))
        
        for product in selected_products:
            quantity = random.randint(1, 3)
            discount = Decimal(random.choice([0, 0, 0, 5000, 10000]))  # Mayoría sin descuento
            
            SaleItem.objects.create(
                sale=sale,
                product=product,
                quantity=quantity,
                price=product.price,
                discount=discount
            )
        
        # Calcular totales
        sale.calculate_totals()
        sale_counter += 1

print(f"\n✓ Se crearon {sale_counter - 1} ventas de ejemplo")
print("✓ Datos de ejemplo creados exitosamente!")
print("\nEstadísticas:")
print(f"- Categorías: {Category.objects.count()}")
print(f"- Productos: {Product.objects.count()}")
print(f"- Ventas: {Sale.objects.count()}")
print(f"- Items vendidos: {SaleItem.objects.count()}")
