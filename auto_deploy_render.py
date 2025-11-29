#!/usr/bin/env python3
"""
Script para configurar automáticamente las variables de entorno en Render
usando la API de Render.

REQUISITOS:
1. Tener una cuenta en Render
2. Generar un API Key desde: https://dashboard.render.com/u/settings#api-keys
3. Tener creado el Web Service y PostgreSQL en Render

USO:
python auto_deploy_render.py
"""

import requests
import secrets
import json
import sys

# ============================================================================
# CONFIGURACIÓN - EDITA ESTOS VALORES
# ============================================================================

# Tu API Key de Render (genera uno en https://dashboard.render.com/u/settings#api-keys)
RENDER_API_KEY = ""  # <-- PEGA TU API KEY AQUÍ

# ID de tu servicio web (lo encuentras en la URL: https://dashboard.render.com/web/srv-XXXXX)
WEB_SERVICE_ID = ""  # <-- Ejemplo: srv-ddkbkbnqaepq-0

# URL de tu PostgreSQL (la que ya tienes)
DATABASE_URL = "postgresql://oceano_admin:GqZwicsr384aWBS8YjwBfMbxWrdq61qT@dpg-d4llkbruibrs7384b38g-a/oceano_optico"

# ============================================================================
# NO EDITES DEBAJO DE ESTA LÍNEA
# ============================================================================

def generate_secret_key():
    """Genera un SECRET_KEY seguro"""
    return secrets.token_urlsafe(50)

def get_render_headers():
    """Retorna los headers para la API de Render"""
    return {
        "Accept": "application/json",
        "Content-Type": "application/json",
        "Authorization": f"Bearer {RENDER_API_KEY}"
    }

def get_current_env_vars(service_id):
    """Obtiene las variables de entorno actuales"""
    url = f"https://api.render.com/v1/services/{service_id}/env-vars"
    response = requests.get(url, headers=get_render_headers())
    
    if response.status_code == 200:
        return response.json()
    else:
        print(f"❌ Error obteniendo variables: {response.status_code}")
        print(response.text)
        return []

def update_env_vars(service_id, env_vars):
    """Actualiza las variables de entorno en Render"""
    url = f"https://api.render.com/v1/services/{service_id}/env-vars"
    
    # Formatear las variables para la API
    env_vars_payload = []
    for key, value in env_vars.items():
        env_vars_payload.append({
            "key": key,
            "value": value
        })
    
    response = requests.put(
        url,
        headers=get_render_headers(),
        json=env_vars_payload
    )
    
    if response.status_code == 200:
        return True
    else:
        print(f"❌ Error actualizando variables: {response.status_code}")
        print(response.text)
        return False

def trigger_deploy(service_id):
    """Dispara un nuevo deploy"""
    url = f"https://api.render.com/v1/services/{service_id}/deploys"
    
    response = requests.post(
        url,
        headers=get_render_headers(),
        json={"clearCache": "clear"}
    )
    
    if response.status_code in [200, 201]:
        return True
    else:
        print(f"❌ Error iniciando deploy: {response.status_code}")
        print(response.text)
        return False

def main():
    print("=" * 70)
    print("🚀 CONFIGURACIÓN AUTOMÁTICA DE RENDER")
    print("=" * 70)
    
    # Validar configuración
    if not RENDER_API_KEY:
        print("\n❌ ERROR: Debes configurar tu RENDER_API_KEY")
        print("\n📝 Pasos:")
        print("1. Ve a https://dashboard.render.com/u/settings#api-keys")
        print("2. Click en 'Create API Key'")
        print("3. Copia el API Key")
        print("4. Pégalo en la variable RENDER_API_KEY de este script")
        sys.exit(1)
    
    if not WEB_SERVICE_ID:
        print("\n❌ ERROR: Debes configurar tu WEB_SERVICE_ID")
        print("\n📝 Pasos:")
        print("1. Ve a tu servicio web en Render")
        print("2. En la URL verás: https://dashboard.render.com/web/srv-XXXXX")
        print("3. Copia el ID (srv-XXXXX)")
        print("4. Pégalo en la variable WEB_SERVICE_ID de este script")
        sys.exit(1)
    
    print(f"\n✅ API Key configurada")
    print(f"✅ Service ID: {WEB_SERVICE_ID}")
    print(f"✅ Database URL configurada")
    
    # Generar SECRET_KEY
    secret_key = generate_secret_key()
    print(f"\n🔑 SECRET_KEY generada: {secret_key[:20]}...")
    
    # Definir todas las variables de entorno
    env_vars = {
        "SECRET_KEY": secret_key,
        "DEBUG": "False",
        "ALLOWED_HOSTS": ".onrender.com",
        "DATABASE_URL": DATABASE_URL,
        "PYTHON_VERSION": "3.7.9",
        "BUSINESS_PHONE": "300 123 4567",
        "WEBSITE_URL": "https://oceano-optico.onrender.com",
        "APPOINTMENT_SLOT_DURATION": "30",
        "MAX_DAILY_APPOINTMENTS": "20",
        "ADVANCE_BOOKING_DAYS": "30"
    }
    
    print("\n📋 Variables a configurar:")
    print("-" * 70)
    for key, value in env_vars.items():
        if key in ["SECRET_KEY", "DATABASE_URL"]:
            print(f"  {key}: {value[:30]}...")
        else:
            print(f"  {key}: {value}")
    print("-" * 70)
    
    # Confirmar
    confirm = input("\n¿Deseas continuar? (si/no): ").lower().strip()
    if confirm not in ["si", "s", "yes", "y"]:
        print("❌ Operación cancelada")
        sys.exit(0)
    
    # Actualizar variables
    print("\n⏳ Actualizando variables de entorno...")
    if update_env_vars(WEB_SERVICE_ID, env_vars):
        print("✅ Variables actualizadas correctamente")
        
        # Guardar en archivo local para referencia
        with open('.env.render', 'w', encoding='utf-8') as f:
            f.write("# Variables configuradas en Render\n")
            f.write("# Generado automáticamente\n\n")
            for key, value in env_vars.items():
                f.write(f"{key}={value}\n")
        print("✅ Copia guardada en .env.render")
        
        # Disparar deploy
        print("\n⏳ Iniciando deploy automático...")
        if trigger_deploy(WEB_SERVICE_ID):
            print("✅ Deploy iniciado correctamente")
            print("\n" + "=" * 70)
            print("🎉 CONFIGURACIÓN COMPLETADA")
            print("=" * 70)
            print("\n📊 Monitorea el progreso en:")
            print(f"   https://dashboard.render.com/web/{WEB_SERVICE_ID}")
            print("\n⏱️  El deploy tomará ~5-10 minutos")
            print("\n🔐 Credenciales de admin (creadas automáticamente):")
            print("   Usuario: admin")
            print("   Contraseña: admin123")
            print("\n⚠️  CAMBIA LA CONTRASEÑA después del primer login!")
        else:
            print("❌ Error iniciando deploy")
            print("💡 Puedes iniciarlo manualmente desde el dashboard")
    else:
        print("❌ Error actualizando variables")
        sys.exit(1)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n❌ Operación cancelada por el usuario")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error inesperado: {e}")
        sys.exit(1)
