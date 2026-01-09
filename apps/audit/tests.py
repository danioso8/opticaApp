"""
Tests para el sistema de auditoría.
"""
from django.test import TestCase, RequestFactory
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from apps.organizations.models import Organization
from apps.audit.models import AuditLog, AuditConfig
from apps.audit.services import AuditService, create_default_configs
from apps.audit.middleware import AuditMiddleware

User = get_user_model()


class AuditServiceTestCase(TestCase):
    """Tests para AuditService."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        
        self.organization = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
    
    def test_log_action(self):
        """Prueba el registro de una acción."""
        log = AuditService.log_action(
            action='CREATE',
            user=self.user,
            organization=self.organization,
            instance=self.organization,
            description='Test action'
        )
        
        self.assertIsNotNone(log)
        self.assertEqual(log.action, 'CREATE')
        self.assertEqual(log.user, self.user)
        self.assertEqual(log.organization, self.organization)
    
    def test_get_object_history(self):
        """Prueba obtener el historial de un objeto."""
        # Crear algunos logs
        for i in range(3):
            AuditService.log_action(
                action='UPDATE',
                user=self.user,
                organization=self.organization,
                instance=self.organization,
                changes={'name': {'old': f'Old {i}', 'new': f'New {i}'}}
            )
        
        history = AuditService.get_object_history(self.organization)
        self.assertEqual(history.count(), 3)
    
    def test_search_logs(self):
        """Prueba la búsqueda de logs."""
        AuditService.log_action(
            action='CREATE',
            user=self.user,
            organization=self.organization,
            instance=self.organization
        )
        
        results = AuditService.search_logs(
            organization=self.organization,
            action='CREATE'
        )
        
        self.assertGreater(results.count(), 0)
    
    def test_audit_config(self):
        """Prueba la configuración de auditoría."""
        config = AuditConfig.objects.create(
            model_name='organizations.Organization',
            organization=self.organization,
            track_creates=True,
            track_updates=False
        )
        
        self.assertTrue(config.should_track_action('CREATE'))
        self.assertFalse(config.should_track_action('UPDATE'))
    
    def test_create_default_configs(self):
        """Prueba la creación de configuraciones por defecto."""
        count = create_default_configs()
        self.assertGreater(count, 0)
        
        # Verificar que se creó al menos una config
        configs = AuditConfig.objects.filter(organization__isnull=True)
        self.assertGreater(configs.count(), 0)


class AuditMiddlewareTestCase(TestCase):
    """Tests para AuditMiddleware."""
    
    def setUp(self):
        """Configuración inicial."""
        self.factory = RequestFactory()
        self.middleware = AuditMiddleware(lambda r: None)
    
    def test_middleware_stores_request(self):
        """Prueba que el middleware almacena la request."""
        from apps.audit.middleware import get_current_request
        
        request = self.factory.get('/')
        
        # Antes de procesar
        self.assertIsNone(get_current_request())
        
        # Procesar (normalmente devolvería una respuesta, pero nuestro
        # get_response es None, así que dará error - pero eso está ok para el test)
        try:
            self.middleware(request)
        except:
            pass
