"""
Script para verificar conexión a base de datos de Render
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection
from django.conf import settings

print("\n" + "="*60)
print("🔍 VERIFICACIÓN DE CONEXIÓN A BASE DE DATOS")
print("="*60)

db_settings = connection.settings_dict

print(f"\n✅ Base de datos: {db_settings['NAME']}")
print(f"✅ Usuario: {db_settings['USER']}")
print(f"✅ Host: {db_settings['HOST']}")
print(f"✅ Puerto: {db_settings['PORT']}")
print(f"✅ Motor: {db_settings['ENGINE']}")

# Verificar conexión
try:
    with connection.cursor() as cursor:
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        print(f"\n✅ PostgreSQL Version: {version[:50]}...")
        
        cursor.execute("SELECT current_database(), current_user;")
        db, user = cursor.fetchone()
        print(f"✅ Conectado a DB: {db}")
        print(f"✅ Como usuario: {user}")
        
        # Verificar tablas de billing
        cursor.execute("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name LIKE 'billing_%'
            ORDER BY table_name;
        """)
        billing_tables = cursor.fetchall()
        
        print(f"\n📋 Tablas de Facturación:")
        for table in billing_tables:
            print(f"   - {table[0]}")
            
        # Verificar plans con facturación electrónica
        cursor.execute("""
            SELECT name, allow_electronic_invoicing, max_invoices_month
            FROM organizations_subscriptionplan
            ORDER BY id;
        """)
        plans = cursor.fetchall()
        
        print(f"\n💳 Planes de Suscripción:")
        for name, allow_inv, max_inv in plans:
            status = "✅ Habilitado" if allow_inv else "❌ Deshabilitado"
            limit = "Ilimitado" if max_inv == 0 else f"{max_inv}/mes"
            print(f"   - {name}: Facturación Electrónica {status} ({limit})")
        
except Exception as e:
    print(f"\n❌ Error: {e}")

print("\n" + "="*60)
print("✅ USANDO BASE DE DATOS DE RENDER (PRODUCCIÓN)")
print("="*60 + "\n")
