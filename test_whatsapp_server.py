"""
Script de prueba para verificar conexión con servidor WhatsApp
"""
import requests

# Configuración
BASE_URL = "http://localhost:3000"
API_KEY = "opticaapp_2026_whatsapp_baileys_secret_key_12345"
HEADERS = {
    'X-API-Key': API_KEY,
    'Content-Type': 'application/json'
}

print("="*50)
print("🧪 PRUEBA DE SERVIDOR WHATSAPP")
print("="*50)

# 1. Health Check
print("\n1️⃣ Probando health check...")
try:
    response = requests.get(f"{BASE_URL}/health", timeout=5)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Servidor activo")
        print(f"   📊 Sesiones activas: {data.get('sessions', 0)}")
    else:
        print(f"   ❌ Error: {response.status_code}")
except Exception as e:
    print(f"   ❌ Error de conexión: {e}")
    exit(1)

# 2. Iniciar sesión de prueba
print("\n2️⃣ Iniciando sesión para organización 23...")
try:
    response = requests.post(
        f"{BASE_URL}/api/start-session",
        json={'organization_id': '23'},
        headers=HEADERS,
        timeout=10
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ {data.get('message')}")
        print(f"   📍 Estado: {data.get('status')}")
    else:
        print(f"   ❌ Error: {response.json()}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 3. Obtener QR
print("\n3️⃣ Esperando código QR (5 segundos)...")
import time
time.sleep(5)

try:
    response = requests.get(
        f"{BASE_URL}/api/qr/23",
        headers=HEADERS,
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        if data.get('has_qr'):
            print(f"   ✅ QR generado!")
            print(f"   📱 Estado: {data.get('status')}")
            print(f"\n   🔗 Escanea el QR en el dashboard:")
            print(f"      http://localhost:8000/dashboard/whatsapp-baileys/")
        else:
            print(f"   ⏳ QR no disponible aún. Estado: {data.get('status')}")
    else:
        print(f"   ❌ Error: {response.json()}")
except Exception as e:
    print(f"   ❌ Error: {e}")

# 4. Ver estado
print("\n4️⃣ Verificando estado de la sesión...")
try:
    response = requests.get(
        f"{BASE_URL}/api/status/23",
        headers=HEADERS,
        timeout=5
    )
    
    if response.status_code == 200:
        data = response.json()
        print(f"   📊 Estado: {data.get('status')}")
        print(f"   🔌 Conectado: {data.get('connected')}")
        print(f"   📱 Tiene QR: {data.get('has_qr')}")
    else:
        print(f"   ❌ Error: {response.json()}")
except Exception as e:
    print(f"   ❌ Error: {e}")

print("\n" + "="*50)
print("✅ PRUEBA COMPLETADA")
print("="*50)
print("\n📋 Próximos pasos:")
print("   1. Inicia Django: python manage.py runserver")
print("   2. Ve a: http://localhost:8000/dashboard/whatsapp-baileys/")
print("   3. Haz clic en 'Conectar WhatsApp'")
print("   4. Escanea el código QR con tu WhatsApp")
print("   5. ¡Listo para enviar notificaciones!\n")
