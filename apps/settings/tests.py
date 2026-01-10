"""
Tests para el sistema de configuraciones.
"""
from django.test import TestCase
from django.core.exceptions import ValidationError

from apps.organizations.models import Organization
from apps.settings.models import AppSetting, IntegrationConfig, SettingCategory
from apps.settings.services import SettingsService, IntegrationService


class AppSettingTestCase(TestCase):
    """Tests para AppSetting."""
    
    def setUp(self):
        """Configuración inicial."""
        self.organization = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
    
    def test_create_setting(self):
        """Prueba crear una configuración."""
        setting = AppSetting.objects.create(
            key='test.setting',
            value='test_value',
            value_type='string',
            organization=self.organization
        )
        
        self.assertIsNotNone(setting)
        self.assertEqual(setting.key, 'test.setting')
        self.assertEqual(setting.get_value(), 'test_value')
    
    def test_int_value_type(self):
        """Prueba el tipo de valor entero."""
        setting = AppSetting.objects.create(
            key='test.int',
            value='42',
            value_type='int'
        )
        
        self.assertEqual(setting.get_value(), 42)
        self.assertIsInstance(setting.get_value(), int)
    
    def test_bool_value_type(self):
        """Prueba el tipo de valor booleano."""
        setting = AppSetting.objects.create(
            key='test.bool',
            value='true',
            value_type='bool'
        )
        
        self.assertTrue(setting.get_value())
    
    def test_json_value_type(self):
        """Prueba el tipo de valor JSON."""
        setting = AppSetting.objects.create(
            key='test.json',
            value='{"key": "value"}',
            value_type='json'
        )
        
        value = setting.get_value()
        self.assertIsInstance(value, dict)
        self.assertEqual(value['key'], 'value')
    
    def test_validation(self):
        """Prueba la validación de valores."""
        setting = AppSetting(
            key='test.invalid',
            value='invalid_int',
            value_type='int'
        )
        
        with self.assertRaises(ValidationError):
            setting.clean()


class SettingsServiceTestCase(TestCase):
    """Tests para SettingsService."""
    
    def setUp(self):
        """Configuración inicial."""
        self.organization = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
    
    def test_get_setting(self):
        """Prueba obtener una configuración."""
        SettingsService.set(
            'test.key',
            'test_value',
            organization=self.organization
        )
        
        value = SettingsService.get('test.key', organization=self.organization)
        self.assertEqual(value, 'test_value')
    
    def test_get_with_default(self):
        """Prueba obtener configuración con valor por defecto."""
        value = SettingsService.get(
            'non.existent',
            organization=self.organization,
            default='default_value'
        )
        
        self.assertEqual(value, 'default_value')
    
    def test_set_setting(self):
        """Prueba establecer una configuración."""
        setting = SettingsService.set(
            'new.setting',
            'new_value',
            organization=self.organization,
            module='test'
        )
        
        self.assertIsNotNone(setting)
        self.assertEqual(setting.value, 'new_value')
        self.assertEqual(setting.module, 'test')
    
    def test_get_module_settings(self):
        """Prueba obtener configuraciones de un módulo."""
        SettingsService.set('email.host', 'smtp.test.com', module='email')
        SettingsService.set('email.port', '587', module='email', value_type='int')
        
        settings = SettingsService.get_module_settings('email')
        
        self.assertIn('email.host', settings)
        self.assertIn('email.port', settings)
        self.assertEqual(settings['email.host'], 'smtp.test.com')
        self.assertEqual(settings['email.port'], 587)


class IntegrationServiceTestCase(TestCase):
    """Tests para IntegrationService."""
    
    def setUp(self):
        """Configuración inicial."""
        self.organization = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
    
    def test_create_integration(self):
        """Prueba crear una integración."""
        integration = IntegrationService.create_integration(
            'email',
            'SMTP',
            self.organization,
            config={'host': 'smtp.test.com', 'port': 587}
        )
        
        self.assertIsNotNone(integration)
        self.assertEqual(integration.integration_type, 'email')
        self.assertEqual(integration.name, 'SMTP')
    
    def test_get_integration(self):
        """Prueba obtener una integración."""
        IntegrationService.create_integration(
            'whatsapp',
            'Baileys',
            self.organization
        )
        
        integration = IntegrationService.get_integration(
            'whatsapp',
            self.organization
        )
        
        self.assertIsNotNone(integration)
        self.assertEqual(integration.name, 'Baileys')
