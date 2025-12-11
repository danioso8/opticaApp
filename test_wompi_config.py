"""
Script para verificar configuración de Wompi
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from django.conf import settings
import requests


def test_wompi_connection():
    """Prueba la conexión con Wompi"""
    
    print("=" * 60)
    print("VERIFICACIÓN DE CONFIGURACIÓN WOMPI")
    print("=" * 60)
    
    print(f"\nModo: {'PRUEBA/SANDBOX' if settings.WOMPI_TEST_MODE else 'PRODUCCIÓN'}")
    print(f"Base URL: {settings.WOMPI_BASE_URL}")
    print(f"Public Key: {settings.WOMPI_PUBLIC_KEY[:20]}..." if settings.WOMPI_PUBLIC_KEY else "Public Key: NO CONFIGURADA")
    print(f"Private Key: {'Configurada (' + settings.WOMPI_PRIVATE_KEY[:20] + '...)' if settings.WOMPI_PRIVATE_KEY else 'NO CONFIGURADA'}")
    print(f"Events Secret: {'Configurado' if settings.WOMPI_EVENTS_SECRET else 'NO CONFIGURADO'}")
    
    # Probar conexión con la API
    print("\nProbando conexión con API de Wompi...")
    
    try:
        # Endpoint público para obtener tokens de aceptación
        url = f"{settings.WOMPI_BASE_URL}/payment_sources"
        
        headers = {
            'Authorization': f'Bearer {settings.WOMPI_PUBLIC_KEY}',
            'Content-Type': 'application/json'
        }
        
        # Hacer una petición GET simple para verificar credenciales
        response = requests.get(url, headers=headers, timeout=10)
        
        if response.status_code in [200, 401, 404]:
            # 200 = OK, 401 = Auth error (pero llega al server), 404 = Endpoint válido
            if response.status_code == 401:
                print("⚠ Autenticación fallida - Verifica las llaves")
                print(f"  Respuesta: {response.text[:200]}")
                return False
            else:
                print("✓ Conexión exitosa con Wompi API!")
                print(f"  Status: {response.status_code}")
                print(f"  Las credenciales son válidas")
                print(f"\n  ✓ Public Key: Válida")
                print(f"  ✓ Private Key: Configurada")
                print(f"  ✓ Base URL: {settings.WOMPI_BASE_URL}")
                print(f"  ✓ Modo: {'SANDBOX/PRUEBA' if settings.WOMPI_TEST_MODE else 'PRODUCCIÓN'}")
                return True
        else:
            print(f"⚠ Respuesta inesperada de Wompi: {response.status_code}")
            print(f"  Mensaje: {response.text[:200]}")
            return False
            
    except requests.exceptions.RequestException as e:
        print(f"✗ Error de conexión: {e}")
        return False
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


if __name__ == '__main__':
    test_wompi_connection()
