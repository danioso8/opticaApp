"""
Script de prueba para enviar un WhatsApp con Twilio
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.appointments.whatsapp import WhatsAppNotifier

def test_whatsapp():
    """Enviar mensaje de prueba"""
    print("📱 Iniciando prueba de WhatsApp con Twilio...\n")
    
    # Crear notificador
    notifier = WhatsAppNotifier()
    
    if not notifier.enabled:
        print("❌ WhatsApp no está habilitado")
        print("Verifica que las credenciales de Twilio estén en .env")
        return False
    
    print("✅ Cliente de Twilio inicializado correctamente\n")
    
    # Solicitar número de prueba
    print("=" * 60)
    print("IMPORTANTE: Para recibir mensajes del Sandbox de Twilio:")
    print("1. Abre WhatsApp en tu teléfono")
    print("2. Envía un mensaje a: +1 415 523 8886")
    print("3. El mensaje debe ser: join <código-sandbox>")
    print("   (Encuentra tu código en: https://console.twilio.com/us1/develop/sms/try-it-out/whatsapp-learn)")
    print("=" * 60)
    print()
    
    phone = input("Ingresa el número de WhatsApp para prueba (ej: 3001234567): ").strip()
    
    if not phone:
        print("❌ No ingresaste ningún número")
        return False
    
    # Formatear número
    formatted_phone = notifier.format_phone_number(phone)
    print(f"\n📞 Número formateado: {formatted_phone}")
    
    # Mensaje de prueba
    message = """
🌊 *OCEANO OPTICO* 👓

¡Hola! Este es un mensaje de prueba.

✅ Tu sistema de notificaciones por WhatsApp está funcionando correctamente.

🎉 Configuración exitosa con Twilio

📱 Ahora puedes enviar:
• Confirmaciones de citas
• Recordatorios automáticos
• Notificaciones de cancelación

¡Todo listo para usar! 😊
    """.strip()
    
    try:
        print("\n📤 Enviando mensaje...")
        
        response = notifier.client.messages.create(
            from_=notifier.whatsapp_from,
            body=message,
            to=formatted_phone
        )
        
        print(f"\n✅ ¡Mensaje enviado exitosamente!")
        print(f"📋 SID del mensaje: {response.sid}")
        print(f"📊 Estado: {response.status}")
        print(f"📅 Fecha: {response.date_created}")
        print(f"\n🎉 Revisa tu WhatsApp, deberías recibir el mensaje en unos segundos")
        
        return True
        
    except Exception as e:
        print(f"\n❌ Error al enviar mensaje:")
        print(f"   {str(e)}")
        print(f"\n💡 Posibles causas:")
        print(f"   • El número no está unido al sandbox de Twilio")
        print(f"   • Las credenciales son incorrectas")
        print(f"   • El número está en formato incorrecto")
        return False

if __name__ == '__main__':
    test_whatsapp()
