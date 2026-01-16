import requests
import json

# Simular llamada desde el navegador del usuario
url = "https://www.optikaapp.com/api/available-dates/?organization_id=2"

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Accept': 'application/json'
}

print(f"🔍 Probando desde navegador:")
print(f"URL: {url}")
print()

try:
    response = requests.get(url, headers=headers)
    print(f"✅ Status Code: {response.status_code}")
    print(f"📦 Content-Type: {response.headers.get('Content-Type')}")
    print()
    
    if response.status_code == 200:
        try:
            data = response.json()
            print(f"📊 Response JSON:")
            print(json.dumps(data, indent=2))
        except:
            print(f"⚠️  Response no es JSON:")
            print(response.text[:500])
    else:
        print(f"❌ Error Response:")
        print(response.text[:500])
        
except Exception as e:
    print(f"❌ Exception: {e}")
