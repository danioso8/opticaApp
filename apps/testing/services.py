"""
Servicio del Bot de Testing
Ejecuta pruebas automáticas y captura errores
"""
import requests
import time
import logging
from django.utils import timezone
from datetime import datetime, timedelta
from .models import TestBot, TestRun, TestResult
from apps.audit.models import ErrorLog

logger = logging.getLogger(__name__)


class TestBotService:
    """
    Servicio para ejecutar tests automáticos
    """
    
    def __init__(self, test_bot):
        self.test_bot = test_bot
        self.base_url = "https://www.optikaapp.com"
        self.session = requests.Session()
        
    def run_test(self):
        """
        Ejecuta el test configurado
        """
        # Crear registro de ejecución
        test_run = TestRun.objects.create(
            test_bot=self.test_bot,
            status='running'
        )
        
        log_lines = []
        errors_found = 0
        
        try:
            log_lines.append(f"🚀 Iniciando test: {self.test_bot.name}")
            log_lines.append(f"📅 Fecha: {timezone.now()}")
            log_lines.append(f"🔧 Tipo: {self.test_bot.get_test_type_display()}")
            log_lines.append("")
            
            # Obtener URLs a probar según el tipo
            urls_to_test = self.get_test_urls()
            
            log_lines.append(f"📋 URLs a probar: {len(urls_to_test)}")
            log_lines.append("")
            
            # Ejecutar cada prueba
            for i, url_config in enumerate(urls_to_test, 1):
                url = url_config.get('url')
                method = url_config.get('method', 'GET')
                data = url_config.get('data', None)
                
                log_lines.append(f"[{i}/{len(urls_to_test)}] Probando: {method} {url}")
                
                result = self.test_url(test_run, url, method, data)
                
                if result.success:
                    log_lines.append(f"  ✅ Exitoso - {result.status_code} - {result.response_time:.2f}ms")
                else:
                    log_lines.append(f"  ❌ Error - {result.error_type}: {result.error_message[:100]}")
                    errors_found += 1
                
                # Pequeña pausa entre requests
                time.sleep(0.5)
            
            # Actualizar estadísticas
            test_run.errors_found = errors_found
            test_run.status = 'completed'
            test_run.completed_at = timezone.now()
            test_run.execution_log = "\\n".join(log_lines)
            test_run.save()
            
            # Actualizar bot
            self.test_bot.last_run = timezone.now()
            self.test_bot.total_tests += len(urls_to_test)
            self.test_bot.passed_tests += (len(urls_to_test) - errors_found)
            self.test_bot.failed_tests += errors_found
            self.test_bot.status = 'completed'
            
            # Calcular próxima ejecución
            if self.test_bot.frequency != 'once':
                self.test_bot.next_run = self.calculate_next_run()
            
            self.test_bot.save()
            
            logger.info(f"Test completado: {self.test_bot.name} - {errors_found} errores")
            
            return test_run
            
        except Exception as e:
            logger.error(f"Error ejecutando test: {str(e)}", exc_info=True)
            test_run.status = 'failed'
            test_run.execution_log = "\\n".join(log_lines) + f"\\n\\n❌ ERROR FATAL: {str(e)}"
            test_run.completed_at = timezone.now()
            test_run.save()
            
            self.test_bot.status = 'failed'
            self.test_bot.save()
            
            return test_run
    
    def test_url(self, test_run, url, method='GET', data=None):
        """
        Prueba una URL específica
        """
        full_url = url if url.startswith('http') else f"{self.base_url}{url}"
        
        result = TestResult(
            test_run=test_run,
            url=full_url,
            method=method
        )
        
        try:
            start_time = time.time()
            
            if method == 'GET':
                response = self.session.get(full_url, timeout=30)
            elif method == 'POST':
                response = self.session.post(full_url, json=data, timeout=30)
            else:
                response = self.session.request(method, full_url, timeout=30)
            
            response_time = (time.time() - start_time) * 1000  # ms
            
            result.status_code = response.status_code
            result.response_time = response_time
            
            # Verificar si hay errores
            if response.status_code >= 400:
                result.success = False
                result.error_type = f"HTTP {response.status_code}"
                result.error_message = response.text[:1000]
            else:
                # Verificar si la respuesta contiene errores JS
                if 'text/html' in response.headers.get('Content-Type', ''):
                    # Buscar errores comunes en HTML
                    if 'SyntaxError' in response.text or 'TypeError' in response.text:
                        result.success = False
                        result.error_type = 'JavaScript Error'
                        result.error_message = self.extract_js_error(response.text)
                    else:
                        result.success = True
                else:
                    result.success = True
            
        except requests.Timeout:
            result.success = False
            result.error_type = 'Timeout'
            result.error_message = 'Request timeout after 30 seconds'
            
        except requests.ConnectionError as e:
            result.success = False
            result.error_type = 'Connection Error'
            result.error_message = str(e)
            
        except Exception as e:
            result.success = False
            result.error_type = type(e).__name__
            result.error_message = str(e)
            result.stack_trace = str(e.__traceback__)
        
        result.save()
        
        # Si hay error, registrar en el monitor
        if not result.success:
            self.log_error_to_monitor(result)
        
        return result
    
    def get_test_urls(self):
        """
        Obtiene las URLs a probar según el tipo de test
        """
        # Si hay URLs personalizadas, usarlas
        if self.test_bot.test_urls:
            return self.test_bot.test_urls
        
        # Sino, usar URLs predefinidas según el tipo
        org_id = self.test_bot.organization.id if self.test_bot.organization else 2
        
        url_sets = {
            'booking': [
                {'url': f'/api/available-dates/?organization_id={org_id}', 'method': 'GET'},
                {'url': f'/api/available-slots/?date=2026-01-20&organization_id={org_id}', 'method': 'GET'},
            ],
            'sales': [
                {'url': '/dashboard/sales/', 'method': 'GET'},
                {'url': '/dashboard/sales/api/products/', 'method': 'GET'},
            ],
            'inventory': [
                {'url': '/dashboard/inventory/', 'method': 'GET'},
            ],
            'billing': [
                {'url': '/dashboard/billing/', 'method': 'GET'},
            ],
            'payroll': [
                {'url': '/dashboard/payroll/', 'method': 'GET'},
            ],
            'full': []  # Combinar todos
        }
        
        if self.test_bot.test_type == 'full':
            all_urls = []
            for urls in url_sets.values():
                all_urls.extend(urls)
            return all_urls
        
        return url_sets.get(self.test_bot.test_type, [])
    
    def extract_js_error(self, html_content):
        """
        Extrae errores JavaScript del contenido HTML
        """
        # Buscar patrones de error comunes
        error_patterns = ['SyntaxError', 'TypeError', 'ReferenceError', 'Error:']
        
        for pattern in error_patterns:
            if pattern in html_content:
                # Extraer contexto alrededor del error
                start = html_content.find(pattern)
                return html_content[max(0, start-100):start+200]
        
        return "Error desconocido en respuesta HTML"
    
    def log_error_to_monitor(self, test_result):
        """
        Registra el error en el monitor del sistema
        """
        try:
            ErrorLog.objects.create(
                error_type=f"TestBot - {test_result.error_type}",
                message=test_result.error_message,
                url=test_result.url,
                stack_trace=test_result.stack_trace,
                user_agent=f"TestBot/{self.test_bot.name}",
                resolved=False
            )
        except Exception as e:
            logger.error(f"Error logging to monitor: {e}")
    
    def calculate_next_run(self):
        """
        Calcula la próxima ejecución según la frecuencia
        """
        now = timezone.now()
        
        if self.test_bot.frequency == 'hourly':
            return now + timedelta(hours=1)
        elif self.test_bot.frequency == 'daily':
            return now + timedelta(days=1)
        elif self.test_bot.frequency == 'weekly':
            return now + timedelta(weeks=1)
        
        return None


def run_scheduled_tests():
    """
    Ejecuta todos los tests programados que estén pendientes
    """
    now = timezone.now()
    
    # Buscar tests que deben ejecutarse
    pending_tests = TestBot.objects.filter(
        is_active=True,
        next_run__lte=now
    ) | TestBot.objects.filter(
        is_active=True,
        next_run__isnull=True,
        last_run__isnull=True
    )
    
    for test_bot in pending_tests:
        logger.info(f"Ejecutando test programado: {test_bot.name}")
        service = TestBotService(test_bot)
        service.run_test()
