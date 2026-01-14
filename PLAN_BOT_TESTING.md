# 🤖 PLAN DE TRABAJO - BOT DE TESTING AUTOMATIZADO

**Fecha:** 14 de Enero de 2026  
**Objetivo:** Bot autónomo que prueba todos los módulos 24/7 y reporta errores automáticamente

---

## 🎯 VISIÓN GENERAL

Bot de testing que:
1. ✅ Simula usuarios reales interactuando con TODOS los módulos
2. ✅ Ejecuta escenarios de uso completos (happy path + edge cases)
3. ✅ Captura errores automáticamente (ya implementado en sistema)
4. ✅ Genera reportes y notificaciones de fallos
5. ✅ Se ejecuta continuamente en background
6. ✅ Prueba integraciones de pagos (Stripe/Wompi en sandbox)

---

## 📋 FASE 1: INFRAESTRUCTURA BASE (Día 1-2)

### 1.1 Estructura del Bot

```
apps/testing_bot/
├── __init__.py
├── apps.py
├── bot_runner.py              # Orquestador principal
├── config.py                  # Configuración del bot
├── models.py                  # Modelos para tracking
├── admin.py                   # Admin para ver resultados
├── scenarios/
│   ├── __init__.py
│   ├── base_scenario.py       # Clase base
│   ├── auth_scenarios.py      # Login/logout/registro
│   ├── appointments_scenarios.py
│   ├── patients_scenarios.py
│   ├── clinical_scenarios.py
│   ├── inventory_scenarios.py
│   ├── payments_scenarios.py  # NUEVO
│   ├── modules_scenarios.py   # NUEVO
│   └── ...
├── utils/
│   ├── __init__.py
│   ├── api_client.py          # Cliente HTTP para testing
│   ├── data_generators.py     # Generar datos de prueba
│   ├── error_reporter.py      # Integración con sistema de errores
│   └── notifications.py       # Enviar alertas
└── management/
    └── commands/
        ├── run_bot.py         # python manage.py run_bot
        ├── run_scenario.py    # python manage.py run_scenario appointments
        └── bot_report.py      # python manage.py bot_report
```

### 1.2 Modelos de Tracking

```python
# apps/testing_bot/models.py
from django.db import models
import uuid

class BotRun(models.Model):
    """Registro de cada ejecución del bot"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=20, choices=[
        ('running', 'En Ejecución'),
        ('completed', 'Completado'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado'),
    ])
    total_scenarios = models.IntegerField(default=0)
    passed_scenarios = models.IntegerField(default=0)
    failed_scenarios = models.IntegerField(default=0)
    errors_found = models.IntegerField(default=0)
    execution_time = models.FloatField(null=True)  # segundos

class ScenarioResult(models.Model):
    """Resultado de cada escenario ejecutado"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    bot_run = models.ForeignKey(BotRun, on_delete=models.CASCADE, related_name='results')
    scenario_name = models.CharField(max_length=200)
    module = models.CharField(max_length=100)  # appointments, patients, etc.
    status = models.CharField(max_length=20, choices=[
        ('pass', 'Exitoso'),
        ('fail', 'Fallido'),
        ('error', 'Error'),
        ('skip', 'Omitido'),
    ])
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True)
    execution_time = models.FloatField(null=True)
    
    # Detalles
    steps_executed = models.IntegerField(default=0)
    steps_passed = models.IntegerField(default=0)
    error_message = models.TextField(null=True, blank=True)
    stack_trace = models.TextField(null=True, blank=True)
    screenshot_path = models.CharField(max_length=500, null=True)
    
    # Métricas
    response_time = models.FloatField(null=True)  # ms
    memory_usage = models.FloatField(null=True)   # MB
    
class BotError(models.Model):
    """Errores encontrados por el bot"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4)
    scenario_result = models.ForeignKey(ScenarioResult, on_delete=models.CASCADE)
    error_type = models.CharField(max_length=100)
    error_message = models.TextField()
    url = models.URLField(max_length=500)
    http_status = models.IntegerField(null=True)
    stack_trace = models.TextField()
    
    # Integración con sistema de errores existente
    sentry_id = models.CharField(max_length=200, null=True)
    js_error_id = models.BigIntegerField(null=True)
    
    is_resolved = models.BooleanField(default=False)
    resolved_at = models.DateTimeField(null=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
```

### 1.3 Configuración Base

```python
# apps/testing_bot/config.py
from dataclasses import dataclass
from typing import List

@dataclass
class BotConfig:
    """Configuración del bot"""
    
    # Ambiente
    BASE_URL: str = 'https://www.optikaapp.com'
    TEST_MODE: bool = True
    
    # Credenciales de testing
    TEST_USERS = [
        {
            'email': 'bot.tester.1@opticaapp.com',
            'password': 'BotTest2026!',
            'organization': 'Organización Bot Testing 1',
            'role': 'owner'
        },
        {
            'email': 'bot.doctor.1@opticaapp.com',
            'password': 'BotDoctor2026!',
            'organization': 'Organización Bot Testing 1',
            'role': 'doctor'
        },
        {
            'email': 'bot.receptionist.1@opticaapp.com',
            'password': 'BotReceptionist2026!',
            'organization': 'Organización Bot Testing 1',
            'role': 'receptionist'
        },
    ]
    
    # Módulos a probar (todos los 23)
    MODULES_TO_TEST: List[str] = [
        'appointments',
        'patients',
        'clinical_history',
        'prescriptions',
        'exams',
        'treatments',
        'inventory',
        'sales',
        'suppliers',
        'reports',
        'analytics',
        'payments',  # NUEVO
        'modules_marketplace',  # NUEVO
        'whatsapp',
        'email',
        'sms',
        'forms',
        'surveys',
        'telemedicine',
        'billing',
        'insurance',
        'lab_integration',
        'calendar_sync',
    ]
    
    # Timing
    RUN_INTERVAL: int = 3600  # Cada hora
    TIMEOUT_PER_SCENARIO: int = 300  # 5 minutos máximo
    DELAY_BETWEEN_SCENARIOS: int = 5  # 5 segundos
    
    # Notificaciones
    NOTIFY_ON_ERROR: bool = True
    NOTIFY_CHANNELS: List[str] = ['slack', 'email']
    CRITICAL_ERROR_THRESHOLD: int = 5  # Alertar si hay 5+ errores en una run
    
    # Reportes
    GENERATE_HTML_REPORT: bool = True
    KEEP_HISTORY_DAYS: int = 30
    
    # Stripe/Wompi Sandbox
    STRIPE_TEST_CARDS = [
        '4242424242424242',  # Visa exitosa
        '4000000000000002',  # Tarjeta declinada
    ]
    WOMPI_TEST_CARDS = [
        '4242424242424242',  # Exitosa
    ]
```

---

## 📋 FASE 2: ESCENARIOS DE PRUEBA (Día 3-5)

### 2.1 Estructura Base de Escenario

```python
# apps/testing_bot/scenarios/base_scenario.py
from abc import ABC, abstractmethod
import time
import traceback
from typing import Dict, Any, List
import requests

class BaseScenario(ABC):
    """Clase base para todos los escenarios"""
    
    def __init__(self, config, client):
        self.config = config
        self.client = client  # requests.Session con cookies
        self.steps = []
        self.current_step = 0
        self.data = {}  # Datos generados durante la prueba
        
    @abstractmethod
    def setup(self):
        """Preparar datos para el escenario"""
        pass
    
    @abstractmethod
    def execute(self) -> Dict[str, Any]:
        """Ejecutar el escenario completo"""
        pass
    
    @abstractmethod
    def teardown(self):
        """Limpiar datos después del test"""
        pass
    
    def run(self) -> Dict[str, Any]:
        """Ejecutar el escenario completo con manejo de errores"""
        result = {
            'scenario': self.__class__.__name__,
            'status': 'pass',
            'steps_executed': 0,
            'steps_passed': 0,
            'error': None,
            'execution_time': 0,
        }
        
        start_time = time.time()
        
        try:
            self.setup()
            result.update(self.execute())
            self.teardown()
        except Exception as e:
            result['status'] = 'error'
            result['error'] = str(e)
            result['stack_trace'] = traceback.format_exc()
        finally:
            result['execution_time'] = time.time() - start_time
        
        return result
    
    def step(self, name: str, fn, *args, **kwargs):
        """Ejecutar un paso del escenario"""
        self.current_step += 1
        print(f"  Step {self.current_step}: {name}")
        
        try:
            result = fn(*args, **kwargs)
            self.steps.append({
                'name': name,
                'status': 'pass',
                'result': result
            })
            return result
        except Exception as e:
            self.steps.append({
                'name': name,
                'status': 'fail',
                'error': str(e)
            })
            raise
    
    def login(self, email: str, password: str):
        """Login helper"""
        response = self.client.post(
            f"{self.config.BASE_URL}/login/",
            data={'email': email, 'password': password}
        )
        assert response.status_code in [200, 302], f"Login failed: {response.status_code}"
        return response
    
    def get(self, url: str, **kwargs):
        """GET request helper"""
        response = self.client.get(f"{self.config.BASE_URL}{url}", **kwargs)
        return response
    
    def post(self, url: str, data: Dict, **kwargs):
        """POST request helper"""
        response = self.client.post(f"{self.config.BASE_URL}{url}", data=data, **kwargs)
        return response
```

### 2.2 Escenarios Críticos por Módulo

#### APPOINTMENTS (Alta Prioridad)
```python
# apps/testing_bot/scenarios/appointments_scenarios.py

class CreateAppointmentScenario(BaseScenario):
    """Crear una cita completa"""
    
    def setup(self):
        self.patient_data = generate_patient()
        self.doctor = get_random_doctor()
    
    def execute(self):
        # 1. Login como recepcionista
        self.step("Login", self.login, 
                 'bot.receptionist.1@opticaapp.com', 'BotReceptionist2026!')
        
        # 2. Buscar paciente o crear nuevo
        resp = self.step("Search patient", self.get, '/patients/api/search/', 
                        params={'q': self.patient_data['identification']})
        
        if resp.json()['results']:
            patient_id = resp.json()['results'][0]['id']
        else:
            resp = self.step("Create patient", self.post, '/patients/create/',
                           self.patient_data)
            patient_id = resp.json()['patient_id']
        
        # 3. Ver disponibilidad
        resp = self.step("Check availability", self.get,
                        f'/appointments/availability/{self.doctor}/',
                        params={'date': '2026-01-20'})
        
        slots = resp.json()['slots']
        assert len(slots) > 0, "No hay slots disponibles"
        
        # 4. Crear cita
        appointment_data = {
            'patient': patient_id,
            'doctor': self.doctor,
            'date': '2026-01-20',
            'time': slots[0]['time'],
            'reason': 'Control general',
            'notes': 'Testing bot appointment'
        }
        
        resp = self.step("Create appointment", self.post,
                        '/appointments/create/', appointment_data)
        
        assert resp.status_code == 201, f"Failed to create: {resp.status_code}"
        
        self.data['appointment_id'] = resp.json()['appointment_id']
        
        return {
            'status': 'pass',
            'steps_executed': self.current_step,
            'steps_passed': len([s for s in self.steps if s['status'] == 'pass']),
            'data': self.data
        }
    
    def teardown(self):
        # Cancelar la cita de prueba
        if 'appointment_id' in self.data:
            self.post(f'/appointments/{self.data["appointment_id"]}/cancel/',
                     {'reason': 'Testing cleanup'})


class RescheduleAppointmentScenario(BaseScenario):
    """Reprogramar una cita existente"""
    # Similar estructura...

class CancelAppointmentScenario(BaseScenario):
    """Cancelar una cita"""
    # Similar estructura...

class AppointmentReminderScenario(BaseScenario):
    """Verificar envío de recordatorios"""
    # Similar estructura...
```

#### PAYMENTS & MODULES (Alta Prioridad - NUEVO)
```python
# apps/testing_bot/scenarios/payments_scenarios.py

class PurchaseModuleWithStripeScenario(BaseScenario):
    """Comprar módulos con Stripe"""
    
    def execute(self):
        # 1. Login como owner
        self.step("Login", self.login,
                 'bot.tester.1@opticaapp.com', 'BotTest2026!')
        
        # 2. Ver marketplace
        resp = self.step("View marketplace", self.get,
                        '/dashboard/modules/marketplace/')
        assert resp.status_code == 200
        
        # 3. Seleccionar 3 módulos (debe aplicar 10% descuento)
        modules = [1, 2, 3]  # IDs de módulos
        
        # 4. Calcular precio
        resp = self.step("Calculate price", self.post,
                        '/dashboard/modules/api/calculate-price/',
                        {'module_ids': modules})
        
        price_data = resp.json()
        assert price_data['discount_percentage'] == 10
        assert price_data['total'] < price_data['subtotal']
        
        # 5. Ir a checkout
        resp = self.step("Go to checkout", self.post,
                        '/dashboard/modules/checkout/',
                        {'module_ids': modules, 'gateway': 'stripe'})
        
        # 6. Usar tarjeta de prueba
        resp = self.step("Create payment intent", self.post,
                        '/payments/create-payment-intent/',
                        {
                            'amount': price_data['total'],
                            'module_ids': modules,
                            'payment_method': 'card',
                            'card_number': '4242424242424242',
                            'exp_month': '12',
                            'exp_year': '2027',
                            'cvc': '123'
                        })
        
        assert resp.status_code == 200
        payment_intent = resp.json()['payment_intent_id']
        
        # 7. Confirmar pago (webhook simulado)
        # En testing, simular el webhook
        resp = self.step("Simulate webhook", self.post,
                        '/payments/webhooks/stripe/',
                        {
                            'type': 'payment_intent.succeeded',
                            'data': {
                                'object': {
                                    'id': payment_intent,
                                    'status': 'succeeded',
                                    'amount': int(price_data['total'] * 100)
                                }
                            }
                        },
                        headers={'Stripe-Signature': 'test_signature'})
        
        # 8. Verificar que módulos se activaron
        time.sleep(2)  # Esperar procesamiento
        resp = self.step("Check modules activated", self.get,
                        '/dashboard/modules/my-plan/')
        
        html = resp.text
        for module_id in modules:
            assert f'module-{module_id}' in html or 'Activo' in html
        
        return {
            'status': 'pass',
            'steps_executed': self.current_step,
            'steps_passed': len([s for s in self.steps if s['status'] == 'pass']),
            'data': {'payment_intent': payment_intent, 'modules': modules}
        }

class VolumeDiscountScenario(BaseScenario):
    """Verificar descuentos por volumen"""
    
    def execute(self):
        # Probar 3 módulos (10%), 5 módulos (10%), 8 módulos (20%)
        test_cases = [
            {'count': 3, 'expected_discount': 0},
            {'count': 5, 'expected_discount': 10},
            {'count': 8, 'expected_discount': 20},
        ]
        
        self.step("Login", self.login,
                 'bot.tester.1@opticaapp.com', 'BotTest2026!')
        
        for case in test_cases:
            modules = list(range(1, case['count'] + 1))
            resp = self.step(f"Calculate {case['count']} modules", self.post,
                           '/dashboard/modules/api/calculate-price/',
                           {'module_ids': modules})
            
            data = resp.json()
            assert data['discount_percentage'] == case['expected_discount'], \
                   f"Expected {case['expected_discount']}% but got {data['discount_percentage']}%"
        
        return {'status': 'pass', 'steps_executed': self.current_step}

class TrialToPaymentScenario(BaseScenario):
    """Simular conversión de trial a pago"""
    # Verificar timeline de 30 días, emails, modo lectura, etc.
```

#### CLINICAL HISTORY (Alta Prioridad)
```python
# apps/testing_bot/scenarios/clinical_scenarios.py

class CompleteConsultationScenario(BaseScenario):
    """Consulta completa: historia clínica + examen + receta"""
    
    def execute(self):
        # 1. Login como doctor
        # 2. Atender cita
        # 3. Actualizar historia clínica
        # 4. Crear examen de refracción
        # 5. Generar receta
        # 6. Finalizar consulta
        pass

class RefractometryExamScenario(BaseScenario):
    """Crear examen de refractometría"""
    pass

class PrescriptionGenerationScenario(BaseScenario):
    """Generar receta médica con fórmula"""
    pass
```

### 2.3 Escenarios de Integración

```python
# apps/testing_bot/scenarios/integration_scenarios.py

class EndToEndPatientJourneyScenario(BaseScenario):
    """Flujo completo de un paciente"""
    
    def execute(self):
        # 1. Registro de paciente
        # 2. Agendar cita
        # 3. Recordatorio WhatsApp/Email
        # 4. Atención médica (historia + examen + receta)
        # 5. Venta de lentes (inventario)
        # 6. Facturación
        # 7. Seguimiento
        pass

class SubscriptionLifecycleScenario(BaseScenario):
    """Ciclo de vida completo de suscripción"""
    
    def execute(self):
        # 1. Trial de 30 días
        # 2. Notificaciones día 20, 25, 28
        # 3. Expiración → modo lectura
        # 4. Compra de módulos
        # 5. Facturación mensual
        # 6. Renovación automática
        pass
```

---

## 📋 FASE 3: ORQUESTADOR Y RUNNER (Día 6-7)

### 3.1 Bot Runner Principal

```python
# apps/testing_bot/bot_runner.py
import time
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
from .models import BotRun, ScenarioResult, BotError
from .scenarios import ALL_SCENARIOS
from .utils.error_reporter import ErrorReporter
from .utils.notifications import NotificationService

class BotRunner:
    """Orquestador principal del bot"""
    
    def __init__(self, config):
        self.config = config
        self.error_reporter = ErrorReporter()
        self.notifier = NotificationService()
        
    def run_all_scenarios(self, parallel=False):
        """Ejecutar todos los escenarios"""
        
        bot_run = BotRun.objects.create(
            status='running',
            total_scenarios=len(ALL_SCENARIOS)
        )
        
        print(f"🤖 Bot Run #{bot_run.id} iniciado")
        print(f"📋 {len(ALL_SCENARIOS)} escenarios a ejecutar")
        
        results = []
        
        if parallel:
            # Ejecutar en paralelo (cuidado con rate limits)
            with ThreadPoolExecutor(max_workers=3) as executor:
                futures = {
                    executor.submit(self.run_scenario, scenario): scenario
                    for scenario in ALL_SCENARIOS
                }
                
                for future in as_completed(futures):
                    result = future.result()
                    results.append(result)
                    self.save_result(bot_run, result)
        else:
            # Ejecutar secuencialmente
            for scenario in ALL_SCENARIOS:
                result = self.run_scenario(scenario)
                results.append(result)
                self.save_result(bot_run, result)
                
                # Delay entre escenarios
                time.sleep(self.config.DELAY_BETWEEN_SCENARIOS)
        
        # Finalizar run
        bot_run.completed_at = datetime.now()
        bot_run.status = 'completed'
        bot_run.passed_scenarios = len([r for r in results if r['status'] == 'pass'])
        bot_run.failed_scenarios = len([r for r in results if r['status'] != 'pass'])
        bot_run.save()
        
        # Generar reporte
        self.generate_report(bot_run, results)
        
        # Notificar si hay errores críticos
        if bot_run.failed_scenarios >= self.config.CRITICAL_ERROR_THRESHOLD:
            self.notifier.send_critical_alert(bot_run)
        
        return bot_run
    
    def run_scenario(self, scenario_class):
        """Ejecutar un escenario individual"""
        import requests
        
        client = requests.Session()
        scenario = scenario_class(self.config, client)
        
        print(f"\n▶️  Ejecutando: {scenario_class.__name__}")
        
        result = scenario.run()
        
        status_emoji = "✅" if result['status'] == 'pass' else "❌"
        print(f"{status_emoji} {scenario_class.__name__}: {result['status']}")
        
        return result
    
    def save_result(self, bot_run, result):
        """Guardar resultado en BD"""
        scenario_result = ScenarioResult.objects.create(
            bot_run=bot_run,
            scenario_name=result['scenario'],
            module=result.get('module', 'unknown'),
            status=result['status'],
            steps_executed=result.get('steps_executed', 0),
            steps_passed=result.get('steps_passed', 0),
            execution_time=result.get('execution_time', 0),
            error_message=result.get('error'),
            stack_trace=result.get('stack_trace')
        )
        
        # Si hay error, crear BotError y reportar
        if result['status'] in ['fail', 'error']:
            bot_error = BotError.objects.create(
                scenario_result=scenario_result,
                error_type=result.get('error_type', 'UnknownError'),
                error_message=result.get('error', ''),
                url=result.get('url', ''),
                stack_trace=result.get('stack_trace', '')
            )
            
            # Reportar a sistema de errores
            self.error_reporter.report(bot_error)
    
    def generate_report(self, bot_run, results):
        """Generar reporte HTML"""
        # Implementar generación de reporte bonito
        pass
```

### 3.2 Management Command

```python
# apps/testing_bot/management/commands/run_bot.py
from django.core.management.base import BaseCommand
from apps.testing_bot.bot_runner import BotRunner
from apps.testing_bot.config import BotConfig

class Command(BaseCommand):
    help = 'Ejecutar el bot de testing'
    
    def add_arguments(self, parser):
        parser.add_argument(
            '--parallel',
            action='store_true',
            help='Ejecutar escenarios en paralelo'
        )
        parser.add_argument(
            '--module',
            type=str,
            help='Ejecutar solo escenarios de un módulo específico'
        )
        parser.add_argument(
            '--continuous',
            action='store_true',
            help='Ejecutar continuamente cada hora'
        )
    
    def handle(self, *args, **options):
        config = BotConfig()
        runner = BotRunner(config)
        
        if options['continuous']:
            import time
            while True:
                self.stdout.write(self.style.SUCCESS('🤖 Iniciando nueva run...'))
                runner.run_all_scenarios(parallel=options['parallel'])
                self.stdout.write(self.style.SUCCESS(f'⏰ Esperando {config.RUN_INTERVAL}s...'))
                time.sleep(config.RUN_INTERVAL)
        else:
            runner.run_all_scenarios(parallel=options['parallel'])
            self.stdout.write(self.style.SUCCESS('✅ Bot run completado'))
```

---

## 📋 FASE 4: INTEGRACIÓN CON ERRORES (Día 8)

### 4.1 Error Reporter

```python
# apps/testing_bot/utils/error_reporter.py
from apps.error_tracking.models import JSError
import requests

class ErrorReporter:
    """Reporta errores del bot al sistema existente"""
    
    def report(self, bot_error):
        """Reportar error encontrado por el bot"""
        
        # 1. Crear entrada en JSError (reutilizar sistema existente)
        js_error = JSError.objects.create(
            message=bot_error.error_message,
            source='BOT_TESTING',
            lineno=0,
            colno=0,
            error=bot_error.stack_trace,
            url=bot_error.url,
            user_agent='OpticaApp Testing Bot v1.0',
            page_url=bot_error.url,
            organization=None,  # Es del bot
            user=None
        )
        
        bot_error.js_error_id = js_error.id
        bot_error.save()
        
        # 2. Si hay Sentry configurado, enviar también
        if hasattr(settings, 'SENTRY_DSN'):
            self.report_to_sentry(bot_error)
        
        # 3. Log en archivo
        self.log_error(bot_error)
        
        return js_error
    
    def report_to_sentry(self, bot_error):
        """Enviar a Sentry"""
        import sentry_sdk
        with sentry_sdk.push_scope() as scope:
            scope.set_tag("source", "testing_bot")
            scope.set_context("scenario", {
                "name": bot_error.scenario_result.scenario_name,
                "module": bot_error.scenario_result.module
            })
            sentry_sdk.capture_exception(Exception(bot_error.error_message))
    
    def log_error(self, bot_error):
        """Log en archivo"""
        import logging
        logger = logging.getLogger('testing_bot')
        logger.error(
            f"[{bot_error.scenario_result.scenario_name}] "
            f"{bot_error.error_type}: {bot_error.error_message}"
        )
```

### 4.2 Notificaciones

```python
# apps/testing_bot/utils/notifications.py
import requests
from django.core.mail import send_mail
from django.conf import settings

class NotificationService:
    """Enviar notificaciones de errores críticos"""
    
    def send_critical_alert(self, bot_run):
        """Enviar alerta de errores críticos"""
        
        # 1. Slack
        if 'slack' in settings.BOT_NOTIFY_CHANNELS:
            self.send_slack(bot_run)
        
        # 2. Email
        if 'email' in settings.BOT_NOTIFY_CHANNELS:
            self.send_email(bot_run)
        
        # 3. WhatsApp (opcional)
        if 'whatsapp' in settings.BOT_NOTIFY_CHANNELS:
            self.send_whatsapp(bot_run)
    
    def send_slack(self, bot_run):
        """Enviar mensaje a Slack"""
        webhook_url = settings.SLACK_WEBHOOK_URL
        
        message = {
            "text": f"🚨 *Bot Testing Alert*",
            "blocks": [
                {
                    "type": "header",
                    "text": {
                        "type": "plain_text",
                        "text": "🤖 Errores Críticos Detectados"
                    }
                },
                {
                    "type": "section",
                    "fields": [
                        {"type": "mrkdwn", "text": f"*Run ID:*\n{bot_run.id}"},
                        {"type": "mrkdwn", "text": f"*Errores:*\n{bot_run.failed_scenarios}"},
                        {"type": "mrkdwn", "text": f"*Total Escenarios:*\n{bot_run.total_scenarios}"},
                        {"type": "mrkdwn", "text": f"*Tiempo:*\n{bot_run.execution_time:.2f}s"},
                    ]
                },
                {
                    "type": "actions",
                    "elements": [
                        {
                            "type": "button",
                            "text": {"type": "plain_text", "text": "Ver Reporte"},
                            "url": f"https://www.optikaapp.com/admin/testing_bot/botrun/{bot_run.id}/"
                        }
                    ]
                }
            ]
        }
        
        requests.post(webhook_url, json=message)
    
    def send_email(self, bot_run):
        """Enviar email de alerta"""
        send_mail(
            subject=f'🚨 Bot Testing: {bot_run.failed_scenarios} errores detectados',
            message=f'''
            El bot de testing ha detectado {bot_run.failed_scenarios} errores en la última ejecución.
            
            Run ID: {bot_run.id}
            Total escenarios: {bot_run.total_scenarios}
            Exitosos: {bot_run.passed_scenarios}
            Fallidos: {bot_run.failed_scenarios}
            
            Ver reporte completo: https://www.optikaapp.com/admin/testing_bot/botrun/{bot_run.id}/
            ''',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=settings.BOT_ALERT_EMAILS,
        )
```

---

## 📋 FASE 5: DASHBOARDS Y REPORTES (Día 9-10)

### 5.1 Dashboard de Monitoreo

```python
# apps/testing_bot/views.py
from django.shortcuts import render
from django.contrib.admin.views.decorators import staff_member_required
from .models import BotRun, ScenarioResult, BotError
from django.db.models import Count, Avg, Q
from datetime import timedelta
from django.utils import timezone

@staff_member_required
def bot_dashboard(request):
    """Dashboard principal del bot"""
    
    # Últimas 24 horas
    last_24h = timezone.now() - timedelta(hours=24)
    
    # Métricas generales
    metrics = {
        'total_runs': BotRun.objects.count(),
        'runs_24h': BotRun.objects.filter(started_at__gte=last_24h).count(),
        'total_errors': BotError.objects.count(),
        'errors_24h': BotError.objects.filter(created_at__gte=last_24h).count(),
        'avg_execution_time': BotRun.objects.aggregate(Avg('execution_time'))['execution_time__avg'],
        'success_rate': calculate_success_rate(),
    }
    
    # Últimas runs
    recent_runs = BotRun.objects.order_by('-started_at')[:10]
    
    # Errores más frecuentes
    frequent_errors = BotError.objects.values('error_type').annotate(
        count=Count('id')
    ).order_by('-count')[:10]
    
    # Módulos con más errores
    problematic_modules = ScenarioResult.objects.filter(
        status__in=['fail', 'error']
    ).values('module').annotate(
        error_count=Count('id')
    ).order_by('-error_count')[:10]
    
    # Tendencia de errores (últimos 7 días)
    error_trend = get_error_trend(days=7)
    
    context = {
        'metrics': metrics,
        'recent_runs': recent_runs,
        'frequent_errors': frequent_errors,
        'problematic_modules': problematic_modules,
        'error_trend': error_trend,
    }
    
    return render(request, 'testing_bot/dashboard.html', context)

@staff_member_required
def bot_report(request, run_id):
    """Reporte detallado de una run"""
    
    bot_run = BotRun.objects.get(id=run_id)
    results = bot_run.results.all().order_by('module', 'scenario_name')
    
    # Agrupar por módulo
    by_module = {}
    for result in results:
        if result.module not in by_module:
            by_module[result.module] = []
        by_module[result.module].append(result)
    
    context = {
        'bot_run': bot_run,
        'results_by_module': by_module,
        'total_errors': BotError.objects.filter(
            scenario_result__bot_run=bot_run
        ).count(),
    }
    
    return render(request, 'testing_bot/report.html', context)
```

### 5.2 Template del Dashboard

```html
<!-- apps/testing_bot/templates/testing_bot/dashboard.html -->
{% extends 'admin_dashboard/base.html' %}

{% block title %}Bot de Testing - Dashboard{% endblock %}

{% block content %}
<div class="container-fluid">
    <h1 class="mb-4">🤖 Bot de Testing - Dashboard</h1>
    
    <!-- Métricas principales -->
    <div class="row mb-4">
        <div class="col-md-3">
            <div class="card">
                <div class="card-body text-center">
                    <h3>{{ metrics.total_runs }}</h3>
                    <p class="text-muted">Total Runs</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card">
                <div class="card-body text-center">
                    <h3>{{ metrics.runs_24h }}</h3>
                    <p class="text-muted">Runs (24h)</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card">
                <div class="card-body text-center">
                    <h3 class="text-danger">{{ metrics.errors_24h }}</h3>
                    <p class="text-muted">Errores (24h)</p>
                </div>
            </div>
        </div>
        <div class="col-md-3">
            <div class="card">
                <div class="card-body text-center">
                    <h3 class="text-success">{{ metrics.success_rate }}%</h3>
                    <p class="text-muted">Tasa de Éxito</p>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Gráfico de tendencias -->
    <div class="row mb-4">
        <div class="col-md-12">
            <div class="card">
                <div class="card-header">
                    <h5>Tendencia de Errores (7 días)</h5>
                </div>
                <div class="card-body">
                    <canvas id="errorTrendChart"></canvas>
                </div>
            </div>
        </div>
    </div>
    
    <!-- Últimas runs y errores frecuentes -->
    <div class="row">
        <div class="col-md-8">
            <div class="card">
                <div class="card-header">
                    <h5>Últimas Ejecuciones</h5>
                </div>
                <div class="card-body">
                    <table class="table">
                        <thead>
                            <tr>
                                <th>ID</th>
                                <th>Inicio</th>
                                <th>Estado</th>
                                <th>Escenarios</th>
                                <th>Errores</th>
                                <th>Tiempo</th>
                                <th></th>
                            </tr>
                        </thead>
                        <tbody>
                            {% for run in recent_runs %}
                            <tr>
                                <td>{{ run.id|truncatechars:8 }}</td>
                                <td>{{ run.started_at|date:"d/m H:i" }}</td>
                                <td>
                                    <span class="badge badge-{{ run.status|status_class }}">
                                        {{ run.get_status_display }}
                                    </span>
                                </td>
                                <td>{{ run.passed_scenarios }}/{{ run.total_scenarios }}</td>
                                <td class="text-danger">{{ run.failed_scenarios }}</td>
                                <td>{{ run.execution_time|floatformat:2 }}s</td>
                                <td>
                                    <a href="{% url 'bot_report' run.id %}" class="btn btn-sm btn-primary">
                                        Ver Reporte
                                    </a>
                                </td>
                            </tr>
                            {% endfor %}
                        </tbody>
                    </table>
                </div>
            </div>
        </div>
        
        <div class="col-md-4">
            <div class="card">
                <div class="card-header">
                    <h5>Errores Más Frecuentes</h5>
                </div>
                <div class="card-body">
                    <ul class="list-group">
                        {% for error in frequent_errors %}
                        <li class="list-group-item d-flex justify-content-between">
                            <span>{{ error.error_type }}</span>
                            <span class="badge badge-danger">{{ error.count }}</span>
                        </li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
            
            <div class="card mt-3">
                <div class="card-header">
                    <h5>Módulos Problemáticos</h5>
                </div>
                <div class="card-body">
                    <ul class="list-group">
                        {% for module in problematic_modules %}
                        <li class="list-group-item d-flex justify-content-between">
                            <span>{{ module.module }}</span>
                            <span class="badge badge-warning">{{ module.error_count }}</span>
                        </li>
                        {% endfor %}
                    </ul>
                </div>
            </div>
        </div>
    </div>
</div>

<script>
// Chart.js para gráfico de tendencias
const ctx = document.getElementById('errorTrendChart').getContext('2d');
new Chart(ctx, {
    type: 'line',
    data: {
        labels: {{ error_trend.labels|safe }},
        datasets: [{
            label: 'Errores',
            data: {{ error_trend.data|safe }},
            borderColor: 'rgb(255, 99, 132)',
            tension: 0.1
        }]
    }
});
</script>
{% endblock %}
```

---

## 📋 CRONOGRAMA DE IMPLEMENTACIÓN

### Semana 1 (Días 1-7)
- **Día 1:** Crear estructura de apps/testing_bot/
- **Día 2:** Implementar modelos y admin básico
- **Día 3:** Crear BaseScenario y primeros 3 escenarios (Appointments)
- **Día 4:** Implementar escenarios de Payments y Modules (NUEVO)
- **Día 5:** Crear escenarios de Clinical History
- **Día 6:** Implementar BotRunner y management commands
- **Día 7:** Testing manual del bot, ajustes

### Semana 2 (Días 8-14)
- **Día 8:** Integración con sistema de errores existente
- **Día 9:** Implementar NotificationService (Slack, Email)
- **Día 10:** Crear dashboards y reportes HTML
- **Día 11:** Implementar más escenarios (Inventory, Sales, etc.)
- **Día 12:** Crear escenarios de integración end-to-end
- **Día 13:** Configurar ejecución continua con Celery
- **Día 14:** Deploy a producción y monitoreo

---

## 🎯 PRIORIDADES DE ESCENARIOS

### P0 - Críticos (Implementar Primero)
1. ✅ Login/Logout/Auth
2. ✅ CreateAppointmentScenario
3. ✅ CreatePatientScenario
4. ✅ PurchaseModuleWithStripeScenario (NUEVO)
5. ✅ CompleteConsultationScenario
6. ✅ VolumeDiscountScenario (NUEVO)

### P1 - Alta Prioridad
7. ✅ RescheduleAppointmentScenario
8. ✅ RefractometryExamScenario
9. ✅ PrescriptionGenerationScenario
10. ✅ TrialToPaymentScenario (NUEVO)
11. ✅ WebhookStripeScenario (NUEVO)
12. ✅ WebhookWompiScenario (NUEVO)

### P2 - Media Prioridad
13. InventorySaleScenario
14. WhatsAppReminderScenario
15. EmailNotificationScenario
16. ReportGenerationScenario
17. AnalyticsDashboardScenario

### P3 - Baja Prioridad (Tiempo permitiendo)
18. TelemedicineScenario
19. InsuranceClaimScenario
20. LabIntegrationScenario
21. SurveyResponseScenario

---

## 🚀 COMANDOS PARA EJECUTAR

```bash
# Ejecutar bot una vez (todos los escenarios)
python manage.py run_bot

# Ejecutar solo escenarios de un módulo
python manage.py run_bot --module appointments

# Ejecutar en paralelo (más rápido pero cuidado con rate limits)
python manage.py run_bot --parallel

# Ejecutar continuamente (cada hora)
python manage.py run_bot --continuous

# Ver reporte de última run
python manage.py bot_report

# Ver estadísticas generales
python manage.py bot_stats

# Limpiar resultados antiguos (> 30 días)
python manage.py bot_cleanup
```

---

## 📊 MÉTRICAS A TRACKEAR

1. **Cobertura de Código:** % de endpoints probados
2. **Tasa de Éxito:** % de escenarios que pasan
3. **Tiempo de Respuesta:** Promedio por endpoint
4. **Errores por Módulo:** Top 10 módulos problemáticos
5. **Tendencia de Errores:** Gráfico de últimos 7/30 días
6. **Tiempo de Resolución:** Cuánto tardan en arreglar errores
7. **Disponibilidad:** Uptime del sistema (99.9% objetivo)

---

## 🔧 CONFIGURACIÓN DE CELERY BEAT

```python
# config/settings.py - CELERY_BEAT_SCHEDULE
{
    'run-testing-bot': {
        'task': 'apps.testing_bot.tasks.run_bot_task',
        'schedule': crontab(minute=0),  # Cada hora
    },
    'cleanup-old-bot-results': {
        'task': 'apps.testing_bot.tasks.cleanup_old_results',
        'schedule': crontab(hour=3, minute=0),  # Diario a las 3 AM
    },
}
```

```python
# apps/testing_bot/tasks.py
from celery import shared_task
from .bot_runner import BotRunner
from .config import BotConfig

@shared_task
def run_bot_task():
    """Task de Celery para ejecutar el bot"""
    config = BotConfig()
    runner = BotRunner(config)
    bot_run = runner.run_all_scenarios()
    return str(bot_run.id)

@shared_task
def cleanup_old_results():
    """Limpiar resultados antiguos"""
    from datetime import timedelta
    from django.utils import timezone
    from .models import BotRun
    
    threshold = timezone.now() - timedelta(days=30)
    deleted = BotRun.objects.filter(created_at__lt=threshold).delete()
    return f"Deleted {deleted[0]} old runs"
```

---

## ✅ CHECKLIST DE IMPLEMENTACIÓN

- [ ] Crear app testing_bot
- [ ] Implementar modelos (BotRun, ScenarioResult, BotError)
- [ ] Crear BaseScenario
- [ ] Implementar 10 escenarios P0/P1
- [ ] Crear BotRunner
- [ ] Management command run_bot
- [ ] Integración con ErrorReporter
- [ ] NotificationService (Slack/Email)
- [ ] Dashboard de monitoreo
- [ ] Template de reportes
- [ ] Configurar Celery Beat
- [ ] Deploy a producción
- [ ] Documentación de uso
- [ ] Training para equipo

---

## 🎯 OBJETIVO FINAL

**Bot autónomo que ejecuta 50+ escenarios cada hora, detecta automáticamente errores antes que los usuarios, y permite solucionar problemas proactivamente en lugar de reactivamente.**

**Tiempo estimado total: 10-14 días de trabajo**
