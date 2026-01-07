import sys
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
import django
django.setup()

from apps.appointments.whatsapp import WhatsAppNotifier

# Crear notificador
notifier = WhatsAppNotifier()

print(f"Twilio habilitado: {notifier.enabled}")
print(f"Account SID: {notifier.account_sid}")
print(f"WhatsApp From: {notifier.whatsapp_from}")
print()

# Probar formateo de número
phone = "3007915262"
formatted = notifier.format_phone_number(phone)
print(f"Número original: {phone}")
print(f"Número formateado: {formatted}")
print()

# Enviar mensaje de prueba
print("Enviando mensaje de prueba...")
try:
    message = notifier.client.messages.create(
        from_=notifier.whatsapp_from,
        body="🧪 Mensaje de prueba desde OpticaApp. Si recibes esto, ¡la configuración de WhatsApp funciona correctamente! ✅",
        to=formatted
    )
    print(f"✅ Mensaje enviado exitosamente!")
    print(f"   SID: {message.sid}")
    print(f"   Status: {message.status}")
except Exception as e:
    print(f"❌ Error: {e}")
