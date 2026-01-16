import requests

# Probar slots con formato de 12 horas
org_id = "2"  # compueasys2
date = "2026-01-20"

url = f"https://www.optikaapp.com/api/available-slots/?date={date}&organization_id={org_id}"
print(f"📡 Probando: {url}")

response = requests.get(url)
print(f"Status Code: {response.status_code}")
data = response.json()
print(f"\nFecha: {data.get('date')}")
print(f"Slots encontrados: {len(data.get('slots', []))}")
print("\nPrimeros 5 horarios:")
for slot in data.get('slots', [])[:5]:
    print(f"  - {slot['time']} - {'✓ Disponible' if slot['available'] else '✗ Ocupado'}")
