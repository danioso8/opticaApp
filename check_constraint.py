#!/usr/bin/env python
"""
Script para verificar y marcar migraciones problemáticas en Render
"""
import os
import sys
import django

# Configurar Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.db import connection

def check_constraint():
    """Verifica si el constraint unique_active_appointment_slot existe"""
    cursor = connection.cursor()
    
    print("=" * 70)
    print("🔍 VERIFICANDO CONSTRAINTS EN LA BASE DE DATOS")
    print("=" * 70)
    
    # Ver todos los constraints que empiecen con "unique"
    print("\n📋 Todos los constraints que empiezan con 'unique':")
    cursor.execute("SELECT conname FROM pg_constraint WHERE conname LIKE 'unique%'")
    constraints = cursor.fetchall()
    for constraint in constraints:
        print(f"  - {constraint[0]}")
    
    # Ver específicamente el que buscamos
    print(f"\n🔎 Buscando constraint 'unique_active_appointment_slot':")
    cursor.execute("SELECT conname FROM pg_constraint WHERE conname = 'unique_active_appointment_slot'")
    result = cursor.fetchone()
    
    if result:
        print(f"  ✅ EXISTE: {result[0]}")
        print("\n💡 SOLUCIÓN: Ejecuta estos comandos:")
        print("  python manage.py migrate appointments --fake")
        print("  python manage.py migrate")
        return True
    else:
        print("  ❌ NO EXISTE")
        print("\n💡 El constraint no existe, las migraciones deberían ejecutarse normalmente")
        return False
    
def main():
    constraint_exists = check_constraint()
    
    print("\n" + "=" * 70)
    print("📊 RESUMEN")
    print("=" * 70)
    
    if constraint_exists:
        print("⚠️  El constraint YA EXISTE en la base de datos")
        print("🔧 Necesitas marcar las migraciones como fake")
        print("\n🚀 EJECUTA AHORA:")
        print("  python manage.py migrate appointments --fake")
        print("  python manage.py migrate")
    else:
        print("✅ El constraint NO existe")
        print("✅ Las migraciones pueden ejecutarse normalmente")
    
    print("=" * 70)

if __name__ == '__main__':
    main()
