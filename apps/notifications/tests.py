from django.test import TestCase
from django.contrib.auth.models import User
from apps.organizations.models import Organization
from apps.notifications.models import (
    Notification, NotificationChannel, NotificationPreference, NotificationTemplate
)
from apps.notifications.services import NotificationService


class NotificationServiceTestCase(TestCase):
    """Tests para NotificationService"""
    
    def setUp(self):
        """Configuración inicial"""
        self.org = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='password123'
        )
        
        self.service = NotificationService(self.org)
    
    def test_send_notification(self):
        """Test: Enviar notificación básica"""
        notification = self.service.send_notification(
            user=self.user,
            title='Test Notification',
            message='This is a test',
            notification_type='info'
        )
        
        self.assertIsNotNone(notification)
        self.assertEqual(notification.title, 'Test Notification')
        self.assertEqual(notification.user, self.user)
        self.assertFalse(notification.is_read)
    
    def test_unread_count(self):
        """Test: Contador de no leídas"""
        # Crear 3 notificaciones
        for i in range(3):
            self.service.send_notification(
                user=self.user,
                title=f'Notification {i}',
                message='Test'
            )
        
        count = self.service.get_unread_count(self.user)
        self.assertEqual(count, 3)
    
    def test_mark_all_as_read(self):
        """Test: Marcar todas como leídas"""
        # Crear notificaciones
        for i in range(2):
            self.service.send_notification(
                user=self.user,
                title=f'Notification {i}',
                message='Test'
            )
        
        # Marcar como leídas
        count = self.service.mark_all_as_read(self.user)
        
        self.assertEqual(count, 2)
        self.assertEqual(self.service.get_unread_count(self.user), 0)


class NotificationTemplateTestCase(TestCase):
    """Tests para NotificationTemplate"""
    
    def setUp(self):
        self.org = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
        
        self.template = NotificationTemplate.objects.create(
            organization=self.org,
            code='test_template',
            name='Test Template',
            title_template='Hello {name}',
            message_template='Welcome {name}, you have {count} items',
            default_type='info'
        )
    
    def test_render_template(self):
        """Test: Renderizar plantilla con variables"""
        rendered = self.template.render({
            'name': 'John',
            'count': 5
        })
        
        self.assertEqual(rendered['title'], 'Hello John')
        self.assertEqual(rendered['message'], 'Welcome John, you have 5 items')
        self.assertEqual(rendered['type'], 'info')
