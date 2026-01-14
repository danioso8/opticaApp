"""
Sistema Auto-Corrector de Errores
Bot que detecta errores comunes y los soluciona automáticamente
"""
import logging
import os
import subprocess
from django.core.management import call_command
from django.core.cache import cache
from django.db import connection
from .models import ErrorLog
import traceback


logger = logging.getLogger(__name__)


class ErrorAutoFix:
    """
    Sistema inteligente de auto-corrección de errores
    """
    
    def __init__(self):
        self.fixes_applied = []
        self.fixes_failed = []
    
    def analyze_and_fix(self, error_log):
        """
        Analiza un error y trata de corregirlo automáticamente
        """
        error_type = error_log.error_type
        error_message = error_log.error_message
        
        # Mapeo de tipos de error a funciones de corrección
        error_handlers = {
            'DatabaseError': self.fix_database_error,
            'OperationalError': self.fix_database_error,
            'ConnectionError': self.fix_connection_error,
            'TimeoutError': self.fix_timeout_error,
            'MemoryError': self.fix_memory_error,
            'PermissionError': self.fix_permission_error,
            'FileNotFoundError': self.fix_file_not_found,
            'ImportError': self.fix_import_error,
            'ModuleNotFoundError': self.fix_import_error,
        }
        
        # Intentar corrección específica
        handler = error_handlers.get(error_type)
        if handler:
            try:
                success = handler(error_log)
                if success:
                    self.fixes_applied.append({
                        'error_id': error_log.id,
                        'error_type': error_type,
                        'fix_method': handler.__name__
                    })
                    logger.info(f"✅ Auto-corrección exitosa: {error_type} - {handler.__name__}")
                    return True
                else:
                    self.fixes_failed.append({
                        'error_id': error_log.id,
                        'error_type': error_type,
                        'reason': 'Handler returned False'
                    })
            except Exception as e:
                self.fixes_failed.append({
                    'error_id': error_log.id,
                    'error_type': error_type,
                    'reason': str(e)
                })
                logger.error(f"❌ Error al auto-corregir: {e}")
        
        return False
    
    # ===================== CORRECCIONES ESPECÍFICAS =====================
    
    def fix_database_error(self, error_log):
        """
        Corrige errores de base de datos
        """
        message = error_log.error_message.lower()
        
        # Error: Too many connections
        if 'too many connections' in message:
            logger.info("🔧 Detectado: Too many connections - Cerrando conexiones idle")
            try:
                connection.close()
                return True
            except:
                pass
        
        # Error: Table doesn't exist
        if "doesn't exist" in message or "no such table" in message:
            logger.info("🔧 Detectado: Tabla faltante - Ejecutando migraciones")
            try:
                call_command('migrate', '--noinput')
                return True
            except:
                pass
        
        # Error: Lock timeout
        if 'lock' in message or 'deadlock' in message:
            logger.info("🔧 Detectado: Deadlock - Limpiando transacciones")
            try:
                connection.close()
                return True
            except:
                pass
        
        return False
    
    def fix_connection_error(self, error_log):
        """
        Corrige errores de conexión
        """
        message = error_log.error_message.lower()
        
        # Error de conexión a servicios externos
        if 'connection refused' in message or 'connection timeout' in message:
            logger.info("🔧 Detectado: Error de conexión - Esperando reconexión")
            # Limpiar caché de conexiones
            cache.clear()
            return True
        
        return False
    
    def fix_timeout_error(self, error_log):
        """
        Corrige errores de timeout
        """
        logger.info("🔧 Detectado: Timeout - Limpiando caché")
        try:
            cache.clear()
            return True
        except:
            pass
        
        return False
    
    def fix_memory_error(self, error_log):
        """
        Corrige errores de memoria
        """
        logger.info("🔧 Detectado: Memory Error - Limpiando caché y garbage collection")
        try:
            import gc
            cache.clear()
            gc.collect()
            return True
        except:
            pass
        
        return False
    
    def fix_permission_error(self, error_log):
        """
        Corrige errores de permisos de archivos
        """
        message = error_log.error_message
        stack_trace = error_log.stack_trace or ""
        
        # Extraer ruta del archivo del error
        import re
        file_pattern = r"['\"]([^'\"]+)['\"]"
        matches = re.findall(file_pattern, message + stack_trace)
        
        for file_path in matches:
            if os.path.exists(file_path):
                try:
                    logger.info(f"🔧 Detectado: Permission Error - Ajustando permisos: {file_path}")
                    os.chmod(file_path, 0o644)  # rw-r--r--
                    return True
                except:
                    pass
        
        return False
    
    def fix_file_not_found(self, error_log):
        """
        Corrige errores de archivo no encontrado
        """
        message = error_log.error_message
        
        # Intentar crear directorios faltantes
        import re
        path_pattern = r"['\"]([^'\"]+)['\"]"
        matches = re.findall(path_pattern, message)
        
        for path in matches:
            dir_path = os.path.dirname(path)
            if dir_path and not os.path.exists(dir_path):
                try:
                    logger.info(f"🔧 Detectado: Directorio faltante - Creando: {dir_path}")
                    os.makedirs(dir_path, exist_ok=True)
                    return True
                except:
                    pass
        
        return False
    
    def fix_import_error(self, error_log):
        """
        Corrige errores de importación
        """
        message = error_log.error_message
        
        # Extraer nombre del módulo
        import re
        module_pattern = r"No module named ['\"]([^'\"]+)['\"]"
        match = re.search(module_pattern, message)
        
        if match:
            module_name = match.group(1)
            logger.info(f"🔧 Detectado: Módulo faltante - Intentando instalar: {module_name}")
            
            # Mapeo de módulos comunes
            pip_packages = {
                'PIL': 'Pillow',
                'cv2': 'opencv-python',
                'yaml': 'PyYAML',
                'bs4': 'beautifulsoup4',
            }
            
            package = pip_packages.get(module_name, module_name)
            
            try:
                # Intentar instalación (solo en desarrollo)
                from django.conf import settings
                if settings.DEBUG:
                    subprocess.run(['pip', 'install', package], check=True)
                    return True
            except:
                pass
        
        return False
    
    # ===================== ACCIONES PROACTIVAS =====================
    
    def restart_service_if_needed(self, error_log):
        """
        Reinicia servicios si hay demasiados errores críticos
        """
        # Contar errores críticos recientes (últimas 5 minutos)
        from django.utils import timezone
        from datetime import timedelta
        
        five_minutes_ago = timezone.now() - timedelta(minutes=5)
        critical_count = ErrorLog.objects.filter(
            severity='CRITICAL',
            created_at__gte=five_minutes_ago,
            is_resolved=False
        ).count()
        
        if critical_count >= 5:
            logger.warning(f"⚠️ Detectados {critical_count} errores críticos - Reinicio recomendado")
            # En producción, esto podría enviar una alerta o reiniciar automáticamente
            return True
        
        return False
    
    def clean_old_cache(self):
        """
        Limpia caché antiguo proactivamente
        """
        try:
            cache.clear()
            logger.info("🧹 Caché limpiado proactivamente")
            return True
        except:
            return False
    
    def optimize_database(self):
        """
        Optimiza la base de datos (VACUUM, ANALYZE)
        """
        try:
            with connection.cursor() as cursor:
                cursor.execute("VACUUM ANALYZE")
            logger.info("🔧 Base de datos optimizada")
            return True
        except:
            return False
    
    # ===================== REPORTES =====================
    
    def get_fixes_report(self):
        """
        Genera reporte de correcciones aplicadas
        """
        return {
            'fixes_applied': len(self.fixes_applied),
            'fixes_failed': len(self.fixes_failed),
            'details': {
                'applied': self.fixes_applied,
                'failed': self.fixes_failed
            }
        }


# ===================== COMANDO DE GESTIÓN =====================

def auto_fix_errors():
    """
    Función ejecutable por cron para auto-corrección de errores
    """
    logger.info("🤖 Iniciando auto-corrección de errores...")
    
    fixer = ErrorAutoFix()
    
    # Obtener errores sin resolver de las últimas 24 horas
    from django.utils import timezone
    from datetime import timedelta
    
    yesterday = timezone.now() - timedelta(days=1)
    errors = ErrorLog.objects.filter(
        is_resolved=False,
        timestamp__gte=yesterday
    ).order_by('-timestamp')[:50]  # Últimos 50 errores
    
    for error in errors:
        fixer.analyze_and_fix(error)
    
    # Acciones proactivas
    fixer.clean_old_cache()
    
    # Reporte
    report = fixer.get_fixes_report()
    logger.info(f"✅ Auto-corrección completada: {report['fixes_applied']} correcciones aplicadas")
    
    return report
