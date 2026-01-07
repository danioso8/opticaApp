"""
Script de verificación de configuración de Twilio
"""
import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings

def verify_twilio_config():
    """Verificar que las credenciales de Twilio estén configuradas"""
    print("🔍 Verificando configuración de Twilio...\n")
    
    # Verificar Account SID
    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
    if account_sid:
        print(f"✅ TWILIO_ACCOUNT_SID: {account_sid[:8]}...{account_sid[-4:]}")
    else:
        print("❌ TWILIO_ACCOUNT_SID: No configurado")
        return False
    
    # Verificar Auth Token
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
    if auth_token:
        print(f"✅ TWILIO_AUTH_TOKEN: {'*' * 28}{auth_token[-4:]}")
    else:
        print("❌ TWILIO_AUTH_TOKEN: No configurado")
        return False
    
    # Verificar WhatsApp From
    whatsapp_from = getattr(settings, 'TWILIO_WHATSAPP_FROM', None)
    if whatsapp_from:
        print(f"✅ TWILIO_WHATSAPP_FROM: {whatsapp_from}")
    else:
        print("❌ TWILIO_WHATSAPP_FROM: No configurado")
        return False
    
    print("\n✅ Configuración de Twilio completa y correcta")
    print("🎉 Sistema listo para enviar mensajes de WhatsApp")
    
    return True

if __name__ == '__main__':
    verify_twilio_config()
