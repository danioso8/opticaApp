import requests

# Probar el endpoint de fechas disponibles para compueasys
org_id = "2"  # compueasys2

url = f"https://www.optikaapp.com/api/available-dates/?organization_id={org_id}"
print(f"📡 Probando: {url}")

response = requests.get(url)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.json()}")
