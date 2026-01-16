#!/usr/bin/env python3
"""
Script de prueba rápida del Booking de Compueasys
Simula exactamente lo que hace el navegador
"""
import requests
import json

print("="*80)
print("🔍 PRUEBA DEL BOOKING DE COMPUEASYS")
print("="*80)
print()

# Configuración
org_id = 2  # CompuEasys
base_url = "https://www.optikaapp.com"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json'
}

# Test 1: Available Dates
print("📅 Test 1: Cargar fechas disponibles")
print("-" * 80)

url = f"{base_url}/api/available-dates/?organization_id={org_id}"
print(f"URL: {url}")

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"✅ Status: {response.status_code}")
    print(f"📦 Content-Type: {response.headers.get('Content-Type')}")
    
    if response.status_code == 200:
        data = response.json()
        dates = data.get('dates', [])
        print(f"📊 Fechas disponibles: {len(dates)}")
        for date in dates:
            print(f"  - {date}")
        
        if not dates:
            print("⚠️  NO HAY FECHAS DISPONIBLES")
            print("   Solución: Agregar horarios en https://www.optikaapp.com/dashboard/schedules/")
    else:
        print(f"❌ Error {response.status_code}")
        print(response.text[:200])
        
except Exception as e:
    print(f"❌ Exception: {e}")

print()

# Test 2: Available Slots
print("⏰ Test 2: Cargar horarios disponibles")
print("-" * 80)

date = "2026-01-20"  # Única fecha disponible
url = f"{base_url}/api/available-slots/?date={date}&organization_id={org_id}"
print(f"URL: {url}")

try:
    response = requests.get(url, headers=headers, timeout=10)
    print(f"✅ Status: {response.status_code}")
    
    if response.status_code == 200:
        data = response.json()
        slots = data.get('slots', [])
        print(f"📊 Horarios encontrados: {len(slots)}")
        print(f"   Primeros 5 horarios:")
        for slot in slots[:5]:
            status = "✓ Disponible" if slot['available'] else "✗ Ocupado"
            print(f"  - {slot['time']} - {status}")
    else:
        print(f"❌ Error {response.status_code}")
        print(response.text[:200])
        
except Exception as e:
    print(f"❌ Exception: {e}")

print()
print("="*80)
print("✅ PRUEBA COMPLETADA")
print("="*80)
print()
print("💡 Si ves errores en tu navegador:")
print("   1. Presiona Ctrl + Shift + Delete")
print("   2. Limpia caché e imágenes")
print("   3. Recarga la página (F5)")
print("   4. O prueba en modo incógnito (Ctrl + Shift + N)")
print()
