#!/usr/bin/env python3
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.appointments.whatsapp_baileys_client import whatsapp_baileys_client
import json

print("\n=== TEST WHATSAPP BAILEYS CLIENT ===\n")

# Test para org 4 (Oceano Optico)
org_id = 4
print(f"Verificando org {org_id} (OCÉANO ÓPTICO)...")
print("-" * 60)

# 1. Get Status
status = whatsapp_baileys_client.get_status(org_id)
print(f"\n1. Status:")
print(json.dumps(status, indent=2))

# 2. Verify and Recover Connection
print(f"\n2. Verify and Recover Connection:")
is_connected, phone = whatsapp_baileys_client.verify_and_recover_connection(org_id)
print(f"   Is Connected: {is_connected}")
print(f"   Phone: {phone}")

# 3. Try to send test message
if is_connected:
    print(f"\n3. Intentando enviar mensaje de prueba...")
    result = whatsapp_baileys_client.send_message(
        org_id, 
        '573126809496',  # El número de WhatsApp de Oceano Optico
        'Test desde script Python',
        auto_recover=False  # Ya verificamos conexión
    )
    print(f"   Result:")
    print(json.dumps(result, indent=2))
else:
    print(f"\n3. No se puede enviar mensaje - WhatsApp no conectado")

print("\n" + "=" * 60 + "\n")
