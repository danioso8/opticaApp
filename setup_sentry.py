"""
Script de configuración de Sentry para OpticaApp
Ejecutar para obtener instrucciones de configuración
"""
import os


def print_setup_instructions():
    """
    Imprime instrucciones de configuración de Sentry
    """
    print("\n" + "="*80)
    print("🔧 CONFIGURACIÓN DE SENTRY PARA OPTICAAPP")
    print("="*80 + "\n")
    
    print("📋 PASOS PARA CONFIGURAR SENTRY:\n")
    
    print("1️⃣  Crear cuenta en Sentry (GRATIS hasta 5,000 errores/mes)")
    print("   → Ir a: https://sentry.io/signup/")
    print("   → Registrarse con email o GitHub\n")
    
    print("2️⃣  Crear nuevo proyecto")
    print("   → Click en 'Create Project'")
    print("   → Seleccionar plataforma: Django")
    print("   → Nombre del proyecto: opticaapp")
    print("   → Team: Personal (default)\n")
    
    print("3️⃣  Copiar DSN (Data Source Name)")
    print("   → Sentry mostrará algo como:")
    print("     https://1234567890abcdef@o123456.ingest.sentry.io/7654321")
    print("   → COPIAR COMPLETO este URL\n")
    
    print("4️⃣  Configurar en servidor Contabo")
    print("   → SSH al servidor:")
    print("     ssh root@84.247.129.180\n")
    print("   → Editar .env:")
    print("     nano /var/www/opticaapp/.env\n")
    print("   → Agregar al final del archivo:")
    print("     # Sentry Configuration")
    print("     SENTRY_DSN=https://TU_DSN_AQUI@o123456.ingest.sentry.io/7654321")
    print("     ENVIRONMENT=production")
    print("     APP_VERSION=1.0.0\n")
    print("   → Guardar: Ctrl+O, Enter, Ctrl+X\n")
    
    print("5️⃣  Instalar dependencias")
    print("   → En el servidor:")
    print("     cd /var/www/opticaapp")
    print("     source venv/bin/activate")
    print("     pip install sentry-sdk==1.40.0\n")
    
    print("6️⃣  Reiniciar aplicación")
    print("   → En el servidor:")
    print("     pm2 restart opticaapp\n")
    
    print("7️⃣  Verificar instalación")
    print("   → En el servidor, ejecutar:")
    print("     python manage.py shell")
    print("   → Ejecutar:")
    print("     from config.sentry import capture_message")
    print("     capture_message('¡Sentry configurado correctamente!')")
    print("     exit()\n")
    print("   → Ir a Sentry dashboard y verificar que llegó el mensaje\n")
    
    print("8️⃣  Probar captura de errores")
    print("   → Crear un error intencional:")
    print("     python manage.py shell")
    print("   → Ejecutar:")
    print("     from config.sentry import capture_exception")
    print("     try:")
    print("         1 / 0")
    print("     except Exception as e:")
    print("         capture_exception(e)")
    print("     exit()\n")
    print("   → Verificar en Sentry que se capturó el error\n")
    
    print("="*80)
    print("🤖 BOT AUTO-CORRECTOR DE ERRORES")
    print("="*80 + "\n")
    
    print("El bot ya está instalado y configurado.\n")
    
    print("📋 COMANDOS DISPONIBLES:\n")
    
    print("• Ejecutar auto-corrección manual:")
    print("  python manage.py auto_fix_errors\n")
    
    print("• Ejecutar en modo prueba (sin aplicar cambios):")
    print("  python manage.py auto_fix_errors --dry-run\n")
    
    print("• Configurar cron para auto-corrección automática cada hora:")
    print("  crontab -e")
    print("  # Agregar:")
    print("  0 * * * * cd /var/www/opticaapp && source venv/bin/activate && python manage.py auto_fix_errors >> /var/log/opticaapp/auto_fix.log 2>&1\n")
    
    print("="*80)
    print("📊 ERRORES QUE EL BOT PUEDE CORREGIR AUTOMÁTICAMENTE")
    print("="*80 + "\n")
    
    corrections = {
        'DatabaseError': [
            '• Too many connections → Cierra conexiones idle',
            '• Tabla no existe → Ejecuta migraciones',
            '• Deadlock → Limpia transacciones',
        ],
        'ConnectionError': [
            '• Connection refused → Limpia caché de conexiones',
            '• Connection timeout → Espera reconexión',
        ],
        'TimeoutError': [
            '• Timeout → Limpia caché',
        ],
        'MemoryError': [
            '• Memory overflow → Limpia caché + garbage collection',
        ],
        'PermissionError': [
            '• Permisos de archivos → Ajusta permisos (chmod)',
        ],
        'FileNotFoundError': [
            '• Directorio faltante → Crea directorios',
        ],
        'ImportError/ModuleNotFoundError': [
            '• Módulo faltante → Instala paquete (solo desarrollo)',
        ],
    }
    
    for error_type, fixes in corrections.items():
        print(f"🔹 {error_type}:")
        for fix in fixes:
            print(f"  {fix}")
        print()
    
    print("="*80)
    print("⚠️  LIMITACIONES DEL BOT")
    print("="*80 + "\n")
    
    print("❌ El bot NO puede:")
    print("  • Corregir bugs de lógica en tu código")
    print("  • Escribir código nuevo")
    print("  • Corregir errores de sintaxis")
    print("  • Resolver problemas de diseño")
    print("  • Arreglar errores de negocio\n")
    
    print("✅ El bot SÍ puede:")
    print("  • Reiniciar servicios caídos")
    print("  • Limpiar caché corrupto")
    print("  • Ejecutar migraciones faltantes")
    print("  • Ajustar permisos de archivos")
    print("  • Crear directorios faltantes")
    print("  • Optimizar base de datos\n")
    
    print("="*80)
    print("🎯 SIGUIENTE PASO")
    print("="*80 + "\n")
    
    print("1. Sigue los pasos arriba para configurar Sentry")
    print("2. Una vez configurado, ejecuta:")
    print("   python manage.py auto_fix_errors --dry-run")
    print("3. Revisa el log para ver qué errores detectó")
    print("4. Si todo se ve bien, ejecuta sin --dry-run\n")
    
    print("="*80)
    print("📞 SOPORTE")
    print("="*80 + "\n")
    
    print("• Dashboard de errores interno: http://84.247.129.180/saas-admin/errors/")
    print("• Dashboard de Sentry: https://sentry.io/")
    print("• Documentación: SISTEMA_MONITOREO_ERRORES.md\n")
    
    print("="*80 + "\n")


if __name__ == '__main__':
    print_setup_instructions()
