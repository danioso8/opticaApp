"""
Tests para API
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient

from apps.api.models import APIKey, APILog, RateLimitRecord, APIWebhook
from apps.api.services import APIService, RateLimitService, WebhookService

User = get_user_model()


class APIKeyTestCase(TestCase):
    """Tests para modelo APIKey"""
    
    def setUp(self):
        """Setup test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        # Crear organización mock
        from apps.organizations.models import Organization
        self.org = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
    
    def test_create_api_key(self):
        """Test crear API key"""
        api_key = APIKey.objects.create(
            name='Test Key',
            user=self.user,
            organization=self.org,
            scope='read'
        )
        
        self.assertIsNotNone(api_key.key)
        self.assertEqual(len(api_key.key_prefix), 8)
        self.assertIsNotNone(api_key.key_hash)
        self.assertEqual(api_key.status, 'active')
    
    def test_api_key_validation(self):
        """Test validación de API key"""
        api_key = APIKey.objects.create(
            name='Test Key',
            user=self.user,
            organization=self.org,
            scope='read'
        )
        
        self.assertTrue(api_key.is_valid())
        
        # Revocar
        api_key.status = 'revoked'
        api_key.save()
        
        self.assertFalse(api_key.is_valid())
    
    def test_api_key_expiration(self):
        """Test expiración de API key"""
        api_key = APIKey.objects.create(
            name='Test Key',
            user=self.user,
            organization=self.org,
            scope='read',
            expires_at=timezone.now() - timedelta(days=1)
        )
        
        self.assertFalse(api_key.is_valid())
        self.assertEqual(api_key.status, 'expired')
    
    def test_endpoint_restrictions(self):
        """Test restricciones de endpoint"""
        api_key = APIKey.objects.create(
            name='Test Key',
            user=self.user,
            organization=self.org,
            scope='read',
            allowed_endpoints=['/api/v1/patients/', '/api/v1/appointments/']
        )
        
        self.assertTrue(api_key.can_access_endpoint('/api/v1/patients/'))
        self.assertFalse(api_key.can_access_endpoint('/api/v1/invoices/'))
    
    def test_ip_restrictions(self):
        """Test restricciones de IP"""
        api_key = APIKey.objects.create(
            name='Test Key',
            user=self.user,
            organization=self.org,
            scope='read',
            allowed_ips=['192.168.1.1', '10.0.0.1']
        )
        
        self.assertTrue(api_key.can_access_from_ip('192.168.1.1'))
        self.assertFalse(api_key.can_access_from_ip('192.168.1.2'))


class APIServiceTestCase(TestCase):
    """Tests para APIService"""
    
    def setUp(self):
        """Setup test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        from apps.organizations.models import Organization
        self.org = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
        
        self.api_key = APIKey.objects.create(
            name='Test Key',
            user=self.user,
            organization=self.org,
            scope='read'
        )
    
    def test_validate_api_key(self):
        """Test validación de API key"""
        is_valid, api_key_obj, error = APIService.validate_api_key(
            self.api_key.key
        )
        
        self.assertTrue(is_valid)
        self.assertEqual(api_key_obj.id, self.api_key.id)
        self.assertIsNone(error)
    
    def test_validate_invalid_key(self):
        """Test validación de key inválida"""
        is_valid, api_key_obj, error = APIService.validate_api_key(
            'invalid_key'
        )
        
        self.assertFalse(is_valid)
        self.assertIsNone(api_key_obj)
        self.assertIsNotNone(error)
    
    def test_create_api_key(self):
        """Test crear API key via service"""
        new_key = APIService.create_api_key(
            user=self.user,
            organization=self.org,
            name='New Key',
            scope='write'
        )
        
        self.assertIsNotNone(new_key)
        self.assertEqual(new_key.scope, 'write')
    
    def test_log_request(self):
        """Test logging de request"""
        log = APIService.log_request(
            api_key=self.api_key,
            user=self.user,
            organization=self.org,
            method='GET',
            endpoint='/api/v1/test/',
            full_path='/api/v1/test/?page=1',
            response_status=200,
            response_time=45.5,
            ip_address='127.0.0.1'
        )
        
        self.assertIsNotNone(log)
        self.assertEqual(log.method, 'GET')
        self.assertEqual(log.response_status, 200)


class RateLimitServiceTestCase(TestCase):
    """Tests para RateLimitService"""
    
    def setUp(self):
        """Setup test data"""
        from apps.organizations.models import Organization
        self.org = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
    
    def test_rate_limit_check(self):
        """Test verificación de rate limit"""
        can_proceed, remaining, retry_after = RateLimitService.check_rate_limit(
            identifier='test_identifier',
            limit_type='api_key',
            endpoint='/api/v1/test/',
            limit=10,
            window_minutes=60
        )
        
        self.assertTrue(can_proceed)
        self.assertEqual(remaining, 9)  # 10 - 1
    
    def test_rate_limit_exceeded(self):
        """Test rate limit excedido"""
        identifier = 'test_identifier_2'
        
        # Hacer 10 requests (límite)
        for i in range(10):
            can_proceed, remaining, retry_after = RateLimitService.check_rate_limit(
                identifier=identifier,
                limit_type='api_key',
                endpoint='/api/v1/test/',
                limit=10,
                window_minutes=60
            )
        
        # El 11vo debería fallar
        can_proceed, remaining, retry_after = RateLimitService.check_rate_limit(
            identifier=identifier,
            limit_type='api_key',
            endpoint='/api/v1/test/',
            limit=10,
            window_minutes=60
        )
        
        self.assertFalse(can_proceed)
        self.assertEqual(remaining, 0)
        self.assertGreater(retry_after, 0)


class APIWebhookTestCase(TestCase):
    """Tests para webhooks"""
    
    def setUp(self):
        """Setup test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        from apps.organizations.models import Organization
        self.org = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
        
        self.api_key = APIKey.objects.create(
            name='Test Key',
            user=self.user,
            organization=self.org,
            scope='admin'
        )
        
        self.webhook = APIWebhook.objects.create(
            name='Test Webhook',
            url='https://example.com/webhook',
            api_key=self.api_key,
            organization=self.org,
            events=['patient.created', 'appointment.created']
        )
    
    def test_webhook_creation(self):
        """Test creación de webhook"""
        self.assertIsNotNone(self.webhook.secret)
        self.assertTrue(self.webhook.is_active)
        self.assertEqual(self.webhook.status, 'active')
    
    def test_webhook_event_subscription(self):
        """Test suscripción a eventos"""
        self.assertTrue(self.webhook.is_subscribed_to('patient.created'))
        self.assertTrue(self.webhook.is_subscribed_to('appointment.created'))
        self.assertFalse(self.webhook.is_subscribed_to('invoice.created'))
    
    def test_webhook_wildcard_subscription(self):
        """Test suscripción a todos los eventos"""
        webhook = APIWebhook.objects.create(
            name='Wildcard Webhook',
            url='https://example.com/webhook',
            api_key=self.api_key,
            organization=self.org,
            events=['*']
        )
        
        self.assertTrue(webhook.is_subscribed_to('patient.created'))
        self.assertTrue(webhook.is_subscribed_to('any.event'))
