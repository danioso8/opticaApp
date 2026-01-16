#!/usr/bin/env python
"""
Script de diagnóstico y reparación del servidor WhatsApp
"""
import requests
import json

BASE_URL = "http://84.247.129.180:3000"
API_KEY = "opticaapp_2026_whatsapp_baileys_secret_key_12345"

headers = {
    "Content-Type": "application/json",
    "X-API-Key": API_KEY
}

print("=" * 80)
print("🔍 DIAGNÓSTICO DEL SERVIDOR WHATSAPP")
print("=" * 80)
print()

# 1. Verificar salud del servidor
print("1. Verificando salud del servidor...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    if response.status_code == 200:
        print("   ✅ Servidor respondiendo correctamente")
    else:
        print(f"   ❌ Servidor respondió con código {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")
print()

# 2. Ver todas las sesiones
print("2. Revisando sesiones activas...")
try:
    response = requests.get(f"{BASE_URL}/api/sessions", headers=headers, timeout=5)
    if response.status_code == 200:
        sessions = response.json().get('sessions', {})
        print(f"   📊 Total de sesiones: {len(sessions)}")
        for org_id, session in sessions.items():
            print(f"   - Org {org_id}: {session.get('status', 'unknown')}")
    else:
        print(f"   ❌ Error obteniendo sesiones: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error: {e}")
print()

# 3. Verificar estado de cada organización
print("3. Verificando estado individual de organizaciones...")
for org_id in ['2', '3', '4']:
    try:
        response = requests.get(
            f"{BASE_URL}/api/status/{org_id}", 
            headers=headers, 
            timeout=5
        )
        if response.status_code == 200:
            data = response.json()
            status = data.get('status', 'unknown')
            phone = data.get('phone_number', 'N/A')
            print(f"   Org {org_id}: {status} - Tel: {phone}")
        else:
            print(f"   Org {org_id}: ❌ Error {response.status_code}")
    except Exception as e:
        print(f"   Org {org_id}: ❌ Error - {e}")
print()

# 4. Iniciar sesiones para organizaciones que lo necesiten
print("4. Intentando iniciar sesiones...")
for org_id in ['2', '3', '4']:
    try:
        # Verificar estado primero
        response = requests.get(
            f"{BASE_URL}/api/status/{org_id}", 
            headers=headers, 
            timeout=5
        )
        
        if response.status_code == 200:
            status = response.json().get('status')
            
            if status not in ['connected', 'connecting', 'qr_ready']:
                print(f"   🔄 Iniciando sesión para org {org_id}...")
                
                response = requests.post(
                    f"{BASE_URL}/api/start-session",
                    headers=headers,
                    json={"organization_id": org_id},
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.json()
                    if result.get('qr'):
                        print(f"   ✅ QR generado para org {org_id}")
                        print(f"      URL del QR: {BASE_URL}/api/qr/{org_id}")
                    else:
                        print(f"   ⏳ Sesión iniciando para org {org_id}")
                else:
                    print(f"   ❌ Error iniciando sesión: {response.status_code}")
            else:
                print(f"   ℹ️  Org {org_id} ya está {status}")
                
    except Exception as e:
        print(f"   ❌ Error con org {org_id}: {e}")
print()

# 5. Mostrar URLs de QR
print("5. URLs para escanear QR:")
print(f"   Org 2: {BASE_URL}/api/qr/2")
print(f"   Org 3: {BASE_URL}/api/qr/3")
print(f"   Org 4: {BASE_URL}/api/qr/4")
print()

print("=" * 80)
print("✅ DIAGNÓSTICO COMPLETADO")
print("=" * 80)
print()
print("📋 INSTRUCCIONES:")
print("1. Abre las URLs de QR en el navegador")
print("2. Escanea con WhatsApp (WhatsApp > Dispositivos vinculados)")
print("3. El servidor debería conectarse automáticamente")
print()
