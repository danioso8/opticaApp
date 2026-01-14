"""
Script para solucionar problemas con la sesión de WhatsApp
Limpia sesiones corruptas y permite reconectar
"""
import os
import shutil
import sys

def clear_whatsapp_session(org_id):
    """Limpiar sesión corrupta de WhatsApp"""
    session_path = f"whatsapp-server/auth_sessions/{org_id}"
    
    if os.path.exists(session_path):
        try:
            shutil.rmtree(session_path)
            print(f"✅ Sesión de organización {org_id} eliminada correctamente")
            print(f"📂 Carpeta eliminada: {session_path}")
            print("\n🔄 Próximos pasos:")
            print("1. Inicia el servidor WhatsApp: cd whatsapp-server && npm start")
            print("2. Ve a /dashboard/whatsapp-baileys/ en tu navegador")
            print("3. Click en 'Conectar WhatsApp'")
            print("4. Escanea el nuevo código QR con tu WhatsApp")
            return True
        except Exception as e:
            print(f"❌ Error al eliminar sesión: {e}")
            return False
    else:
        print(f"ℹ️ No existe sesión guardada para organización {org_id}")
        print(f"📂 Ruta buscada: {session_path}")
        return True

def list_sessions():
    """Listar todas las sesiones guardadas"""
    sessions_dir = "whatsapp-server/auth_sessions"
    
    if not os.path.exists(sessions_dir):
        print("ℹ️ No existe el directorio de sesiones")
        return
    
    sessions = [d for d in os.listdir(sessions_dir) if os.path.isdir(os.path.join(sessions_dir, d))]
    
    if sessions:
        print(f"\n📋 Sesiones guardadas ({len(sessions)}):")
        for session in sessions:
            session_path = os.path.join(sessions_dir, session)
            size = sum(os.path.getsize(os.path.join(session_path, f)) 
                      for f in os.listdir(session_path) if os.path.isfile(os.path.join(session_path, f)))
            print(f"   - Organización {session} ({size / 1024:.1f} KB)")
    else:
        print("ℹ️ No hay sesiones guardadas")

if __name__ == "__main__":
    print("=" * 60)
    print("🔧 SOLUCIÓN DE PROBLEMAS DE WHATSAPP")
    print("=" * 60)
    
    # Listar sesiones existentes
    list_sessions()
    
    print("\n" + "=" * 60)
    
    # Solicitar ID de organización
    if len(sys.argv) > 1:
        org_id = sys.argv[1]
    else:
        org_id = input("\n🔢 Ingresa el ID de tu organización (presiona Enter para 23): ").strip()
        if not org_id:
            org_id = "23"
    
    print(f"\n🧹 Limpiando sesión corrupta de organización {org_id}...")
    
    if clear_whatsapp_session(org_id):
        print("\n✅ LISTO! La sesión ha sido limpiada.")
    else:
        print("\n❌ Hubo un problema. Verifica los permisos de archivo.")
    
    print("\n" + "=" * 60)
