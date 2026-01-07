import requests
import json
from datetime import datetime, timedelta

# URL del endpoint
url = "http://127.0.0.1:8001/api/appointments/book/"

# Calcular una fecha y hora futuras (mañana a las 11:00)
tomorrow = datetime.now() + timedelta(days=1)
appointment_date = tomorrow.strftime('%Y-%m-%d')

# Datos de la cita (simular el formulario web)
data = {
    "full_name": "Test Usuario WhatsApp",
    "phone_number": "3009787566",  # Mi número para testing
    "email": "test@example.com",
    "appointment_date": appointment_date,
    "appointment_time": "11:00:00",
    "organization_id": 23
}

print("\n=== PROBANDO ENDPOINT DE AGENDAMIENTO ===")
print(f"URL: {url}")
print(f"Datos: {json.dumps(data, indent=2)}")
print("\nEnviando petición...")

try:
    response = requests.post(url, json=data)
    
    print(f"\nEstado: {response.status_code}")
    print(f"Respuesta: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        print("\n✅ CITA CREADA EXITOSAMENTE!")
        print("Verifica si llegó el mensaje de WhatsApp")
    else:
        print(f"\n❌ Error al crear cita")
        
except Exception as e:
    print(f"\n❌ Error: {e}")
    import traceback
    traceback.print_exc()
