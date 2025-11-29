#!/usr/bin/env python3
"""
Script para generar las variables de entorno necesarias para Render.
Ejecuta este script localmente y copia las variables generadas a Render.
"""

import secrets
import os

def generate_secret_key():
    """Genera un SECRET_KEY seguro para Django"""
    return secrets.token_urlsafe(50)

def print_env_variables():
    """Imprime todas las variables de entorno necesarias para Render"""
    
    secret_key = generate_secret_key()
    
    print("=" * 70)
    print("VARIABLES DE ENTORNO PARA RENDER")
    print("=" * 70)
    print("\nCopia estas variables en tu servicio de Render:")
    print("\n1. Ve a tu servicio web en Render")
    print("2. Click en 'Environment' en el menú izquierdo")
    print("3. Agrega cada variable abajo:\n")
    print("-" * 70)
    
    env_vars = {
        "SECRET_KEY": secret_key,
        "DEBUG": "False",
        "ALLOWED_HOSTS": "oceano-optico.onrender.com,.onrender.com",
        "PYTHON_VERSION": "3.7.9",
        "BUSINESS_PHONE": "300 123 4567",
        "WEBSITE_URL": "https://oceano-optico.onrender.com",
        "APPOINTMENT_SLOT_DURATION": "30",
        "MAX_DAILY_APPOINTMENTS": "20",
        "ADVANCE_BOOKING_DAYS": "30",
    }
    
    for key, value in env_vars.items():
        print(f"\n{key}")
        print(f"{value}")
        print("-" * 70)
    
    print("\n⚠️  IMPORTANTE:")
    print("=" * 70)
    print("\nTambién necesitas agregar estas variables (obtén los valores de Render):")
    print("\nDATABASE_URL")
    print("<Copia desde tu PostgreSQL 'oceano-optico-db' en Render>")
    print("Ejemplo: postgresql://user:pass@host.oregon-postgres.render.com/db")
    print("-" * 70)
    
    print("\n📱 OPCIONAL - Para notificaciones WhatsApp con Twilio:")
    print("-" * 70)
    print("\nTWILIO_ACCOUNT_SID")
    print("<Tu Account SID de Twilio Console>")
    print("\nTWILIO_AUTH_TOKEN")
    print("<Tu Auth Token de Twilio Console>")
    print("\nTWILIO_WHATSAPP_FROM")
    print("whatsapp:+14155238886")
    print("-" * 70)
    
    print("\n" + "=" * 70)
    print("CREDENCIALES DE ADMIN (se crean automáticamente en el deploy)")
    print("=" * 70)
    print("\nUsuario: admin")
    print("Contraseña: admin123")
    print("\n⚠️  CAMBIA LA CONTRASEÑA después del primer login!")
    print("=" * 70)
    
    # Guardar en archivo para referencia
    with open('.env.render', 'w', encoding='utf-8') as f:
        f.write("# Variables de entorno para Render\n")
        f.write("# NO SUBAS ESTE ARCHIVO A GIT\n\n")
        for key, value in env_vars.items():
            f.write(f"{key}={value}\n")
        f.write("\n# Agregar manualmente desde Render Dashboard:\n")
        f.write("# DATABASE_URL=<desde PostgreSQL en Render>\n")
        f.write("\n# Opcional - Twilio WhatsApp:\n")
        f.write("# TWILIO_ACCOUNT_SID=\n")
        f.write("# TWILIO_AUTH_TOKEN=\n")
        f.write("# TWILIO_WHATSAPP_FROM=whatsapp:+14155238886\n")
    
    print(f"\n✅ Variables guardadas en: .env.render")
    print("   (Este archivo NO se subirá a Git - está en .gitignore)\n")

if __name__ == "__main__":
    print_env_variables()
