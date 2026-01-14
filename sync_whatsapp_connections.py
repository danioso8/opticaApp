"""
Script para sincronizar el estado de las conexiones de WhatsApp
desde el servidor Node.js a la base de datos Django

Ejecuta esto periódicamente (cada 5 minutos) con cron o similar para
mantener la base de datos actualizada con el estado real de las conexiones
"""
import os
import sys
import django

# Configurar Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.notifications.models_whatsapp_connection import WhatsAppConnection
from apps.appointments.whatsapp_baileys_client import whatsapp_baileys_client
from apps.organizations.models import Organization
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


def sync_all_connections():
    """
    Sincroniza todas las conexiones de WhatsApp desde el servidor
    """
    print("=" * 60)
    print("🔄 SINCRONIZACIÓN DE CONEXIONES WHATSAPP")
    print("=" * 60)
    
    # Verificar que el servidor esté activo
    if not whatsapp_baileys_client.healthcheck():
        print("❌ Servidor WhatsApp no disponible")
        return False
    
    print("✅ Servidor WhatsApp activo")
    
    # Obtener todas las sesiones del servidor
    try:
        sessions_data = whatsapp_baileys_client.list_sessions()
        
        if not sessions_data:
            print("ℹ️  No hay sesiones en el servidor")
            return True
        
        total = sessions_data.get('total', 0)
        sessions = sessions_data.get('sessions', [])
        
        print(f"\n📊 Total de sesiones en servidor: {total}")
        print("-" * 60)
        
        synced = 0
        errors = 0
        
        for session_info in sessions:
            org_id = session_info.get('organization_id')
            status = session_info.get('status')
            connected = session_info.get('connected', False)
            
            try:
                # Obtener la organización
                org = Organization.objects.get(id=org_id)
                
                # Obtener estado completo
                full_status = whatsapp_baileys_client.get_status(org_id)
                
                if full_status:
                    # Sincronizar con la BD
                    connection = WhatsAppConnection.sync_from_server(org_id, full_status)
                    
                    status_symbol = "✅" if connected else "❌"
                    phone = full_status.get('phone_number', 'N/A')
                    
                    print(f"{status_symbol} Org {org_id} ({org.name})")
                    print(f"   Estado: {status}")
                    print(f"   Teléfono: {phone}")
                    print(f"   Conectado: {connected}")
                    
                    synced += 1
                else:
                    print(f"⚠️  Org {org_id}: No se pudo obtener estado completo")
                    errors += 1
                    
            except Organization.DoesNotExist:
                print(f"⚠️  Org {org_id}: No existe en la base de datos")
                errors += 1
            except Exception as e:
                print(f"❌ Org {org_id}: Error - {e}")
                errors += 1
        
        print("-" * 60)
        print(f"\n📈 Resumen:")
        print(f"   ✅ Sincronizadas: {synced}")
        print(f"   ❌ Errores: {errors}")
        print(f"   📊 Total: {total}")
        
        return True
        
    except Exception as e:
        logger.error(f"Error sincronizando conexiones: {e}", exc_info=True)
        print(f"\n❌ Error general: {e}")
        return False


def check_stale_connections():
    """
    Verifica conexiones que están marcadas como conectadas en BD
    pero no existen en el servidor (posible desincronización)
    """
    print("\n" + "=" * 60)
    print("🔍 VERIFICANDO CONEXIONES OBSOLETAS")
    print("=" * 60)
    
    active_in_db = WhatsAppConnection.objects.filter(status='connected')
    
    if not active_in_db.exists():
        print("ℹ️  No hay conexiones activas en BD")
        return
    
    print(f"\n📊 Conexiones activas en BD: {active_in_db.count()}")
    
    for connection in active_in_db:
        org_id = connection.organization.id
        
        try:
            status = whatsapp_baileys_client.get_status(org_id)
            
            if status:
                if not status.get('connected'):
                    print(f"⚠️  Org {org_id} ({connection.organization.name})")
                    print(f"   BD dice: conectado")
                    print(f"   Servidor dice: {status.get('status')}")
                    print(f"   🔧 Sincronizando...")
                    
                    WhatsAppConnection.sync_from_server(org_id, status)
                    print(f"   ✅ Sincronizado")
            else:
                print(f"⚠️  Org {org_id}: No se pudo verificar en servidor")
                
        except Exception as e:
            print(f"❌ Org {org_id}: Error - {e}")
    
    print("-" * 60)


if __name__ == "__main__":
    print("\n🚀 Iniciando sincronización de conexiones WhatsApp")
    print(f"⏰ Fecha: {django.utils.timezone.now()}\n")
    
    # Sincronizar todas las conexiones
    success = sync_all_connections()
    
    if success:
        # Verificar conexiones obsoletas
        check_stale_connections()
    
    print("\n" + "=" * 60)
    print("✅ SINCRONIZACIÓN COMPLETADA")
    print("=" * 60 + "\n")
