import requests

url = "http://84.247.129.180:3000/api/start-session"
headers = {
    "Content-Type": "application/json",
    "x-api-key": "opticaapp_2026_whatsapp_baileys_secret_key_12345"
}
data = {"organization_id": "2"}

print("🔄 Solicitando nuevo QR con auto-eliminación de sesión anterior...")
response = requests.post(url, json=data, headers=headers)
print(f"Status Code: {response.status_code}")
print(f"Response: {response.text}")
