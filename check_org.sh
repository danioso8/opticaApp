#!/bin/bash
cd /var/www/opticaapp
source venv/bin/activate
python manage.py shell <<EOF
from apps.organizations.models import Organization
from apps.whatsapp.models import WhatsAppConnection
import os

org = Organization.objects.get(name__icontains='oceano')
print(f"Org ID: {org.id}")
print(f"Nombre: {org.name}")
print(f"Email: {org.owner.email if org.owner else 'Sin dueño'}")
print(f"Plan: {org.subscription_plan.name if org.subscription_plan else 'Sin plan'}")

try:
    conn = WhatsAppConnection.objects.get(organization=org)
    print(f"WhatsApp conectado: {conn.is_connected}")
    print(f"Número: {conn.phone_number or 'No configurado'}")
    session_path = f"/var/www/opticaapp/whatsapp-server/auth_sessions/{org.id}"
    print(f"Ruta sesión: {session_path}")
    print(f"Existe sesión: {os.path.exists(session_path)}")
    if os.path.exists(session_path):
        files = os.listdir(session_path)
        print(f"Archivos en sesión: {files}")
except WhatsAppConnection.DoesNotExist:
    print("No hay conexión de WhatsApp")
except Exception as e:
    print(f"Error: {e}")
EOF
