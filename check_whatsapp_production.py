"""
Script para verificar y restaurar la sesión de WhatsApp en el servidor de producción
"""
import subprocess
import sys

def check_whatsapp_server():
    """Verifica el estado del servidor WhatsApp en producción"""
    
    print("=" * 70)
    print("🔍 VERIFICANDO SERVIDOR WHATSAPP EN PRODUCCIÓN")
    print("=" * 70)
    print()
    
    server_ip = "84.247.129.180"
    
    print(f"📡 Servidor: {server_ip}")
    print()
    
    commands = [
        ("Estado del servidor WhatsApp", "pm2 status whatsapp-server"),
        ("Sesiones activas", "ls -la /var/www/whatsapp-server/auth_sessions/"),
        ("Logs recientes", "pm2 logs whatsapp-server --lines 20 --nostream"),
    ]
    
    print("📋 Comandos a ejecutar en el servidor:\n")
    
    for name, cmd in commands:
        print(f"🔹 {name}:")
        print(f"   ssh root@{server_ip} \"{cmd}\"")
        print()
    
    print("=" * 70)
    print("📝 INSTRUCCIONES MANUALES:")
    print("=" * 70)
    print()
    print("1. Conectarte al servidor:")
    print(f"   ssh root@{server_ip}")
    print()
    print("2. Verificar estado de pm2:")
    print("   pm2 status")
    print()
    print("3. Ver logs del servidor WhatsApp:")
    print("   pm2 logs whatsapp-server --lines 50")
    print()
    print("4. Ver sesiones guardadas:")
    print("   ls -la /var/www/whatsapp-server/auth_sessions/")
    print()
    print("5. Si el servidor está caído, reiniciarlo:")
    print("   pm2 restart whatsapp-server")
    print()
    print("6. Si la sesión está corrupta, limpiarla:")
    print("   rm -rf /var/www/whatsapp-server/auth_sessions/23")
    print("   pm2 restart whatsapp-server")
    print()
    print("=" * 70)
    print()
    
    # Intentar conectar automáticamente si SSH está disponible
    print("¿Deseas que intente conectar automáticamente? (s/n): ", end="")
    try:
        response = input().strip().lower()
        
        if response == 's':
            print()
            print("🔄 Conectando al servidor...")
            print()
            
            # Ejecutar comando SSH para verificar estado
            ssh_cmd = f'ssh root@{server_ip} "pm2 status whatsapp-server"'
            
            try:
                result = subprocess.run(ssh_cmd, shell=True, capture_output=True, text=True, timeout=10)
                
                if result.returncode == 0:
                    print("✅ Conexión exitosa!")
                    print()
                    print(result.stdout)
                else:
                    print("❌ Error al conectar:")
                    print(result.stderr)
                    print()
                    print("💡 Usa el comando manual:")
                    print(f"   ssh root@{server_ip}")
                    
            except subprocess.TimeoutExpired:
                print("⏱️ Timeout - la conexión tomó demasiado tiempo")
                print()
                print("💡 Usa el comando manual:")
                print(f"   ssh root@{server_ip}")
            except Exception as e:
                print(f"❌ Error: {e}")
                print()
                print("💡 Usa el comando manual:")
                print(f"   ssh root@{server_ip}")
        else:
            print()
            print("👍 Ok, usa los comandos manuales listados arriba")
            
    except KeyboardInterrupt:
        print()
        print()
        print("❌ Cancelado por el usuario")
    
    print()

if __name__ == "__main__":
    check_whatsapp_server()
