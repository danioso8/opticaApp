"""
Script para probar el envío de mensajes WhatsApp
Ejecutar: python test_whatsapp.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.appointments.whatsapp_local import whatsapp_notifier
from apps.appointments.models import Appointment
from datetime import datetime, timedelta


def test_whatsapp_connection():
    """Verifica si el bot está conectado"""
    print("\n" + "="*60)
    print("🧪 TEST DE CONEXIÓN WHATSAPP")
    print("="*60)
    
    import requests
    try:
        response = requests.get('http://localhost:3000/status', timeout=5)
        data = response.json()
        
        if data.get('connected'):
            print("✅ Bot de WhatsApp CONECTADO")
            return True
        elif data.get('hasQR'):
            print("⚠️  Bot iniciado pero necesitas escanear el QR")
            print("   Ve a: http://localhost:3000/qr")
            return False
        else:
            print("❌ Bot no está conectado")
            return False
    except requests.exceptions.ConnectionError:
        print("❌ Servidor WhatsApp no está corriendo")
        print("   Ejecuta: cd whatsapp-bot && npm start")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False


def test_send_message():
    """Envía un mensaje de prueba"""
    print("\n" + "="*60)
    print("📱 TEST DE ENVÍO DE MENSAJE")
    print("="*60)
    
    # Solicitar número de teléfono
    phone = input("\nIngresa tu número de WhatsApp (ej: 3001234567): ").strip()
    
    if not phone:
        print("❌ Número no válido")
        return
    
    # Mensaje de prueba
    message = """
👓 *OCEANO OPTICO - PRUEBA*

¡Hola! 👋

Este es un mensaje de prueba del sistema de notificaciones.

Si recibes este mensaje, significa que el bot está funcionando correctamente. ✅

🔧 Sistema de citas automatizado
    """.strip()
    
    print(f"\n📤 Enviando mensaje a: {phone}")
    print("-" * 60)
    
    success = whatsapp_notifier.send_message(phone, message)
    
    if success:
        print("\n✅ ¡Mensaje enviado exitosamente!")
        print("   Revisa tu WhatsApp")
    else:
        print("\n❌ Error al enviar mensaje")
        print("   Verifica que:")
        print("   1. El bot esté conectado")
        print("   2. El número sea válido")
        print("   3. El número esté registrado en WhatsApp")


def test_appointment_notification():
    """Simula el envío de una notificación de cita"""
    print("\n" + "="*60)
    print("📅 TEST DE NOTIFICACIÓN DE CITA")
    print("="*60)
    
    # Buscar una cita reciente para probar
    appointments = Appointment.objects.all().order_by('-created_at')[:5]
    
    if not appointments:
        print("⚠️  No hay citas en el sistema")
        print("   Crea una cita primero para probar")
        return
    
    print("\nCitas disponibles:")
    print("-" * 60)
    for i, apt in enumerate(appointments, 1):
        print(f"{i}. {apt.full_name} - {apt.phone_number}")
        print(f"   {apt.appointment_date} {apt.appointment_time}")
    
    try:
        choice = int(input("\nSelecciona una cita (número): "))
        appointment = appointments[choice - 1]
        
        print(f"\n📤 Enviando notificación a: {appointment.full_name}")
        print("-" * 60)
        
        success = whatsapp_notifier.send_appointment_confirmation(appointment)
        
        if success:
            print("\n✅ ¡Notificación enviada exitosamente!")
        else:
            print("\n❌ Error al enviar notificación")
    
    except (ValueError, IndexError):
        print("❌ Selección inválida")


def main():
    """Menú principal"""
    print("\n" + "="*60)
    print("🌊 OCEANO OPTICO - PRUEBAS DE WHATSAPP 👓")
    print("="*60)
    
    # Verificar conexión primero
    if not test_whatsapp_connection():
        return
    
    while True:
        print("\n" + "-"*60)
        print("Opciones:")
        print("1. Enviar mensaje de prueba")
        print("2. Enviar notificación de cita")
        print("3. Verificar conexión nuevamente")
        print("0. Salir")
        print("-"*60)
        
        choice = input("\nSelecciona una opción: ").strip()
        
        if choice == '1':
            test_send_message()
        elif choice == '2':
            test_appointment_notification()
        elif choice == '3':
            test_whatsapp_connection()
        elif choice == '0':
            print("\n👋 ¡Hasta luego!")
            break
        else:
            print("❌ Opción inválida")


if __name__ == '__main__':
    main()
