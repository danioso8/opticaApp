from django.test import TestCase, RequestFactory
from django.contrib.auth.models import User
from apps.organizations.models import (
    Organization, 
    OrganizationMember, 
    SubscriptionPlan, 
    Subscription
)
from apps.organizations.middleware import TenantMiddleware
from datetime import timedelta
from django.utils import timezone


class OrganizationModelTest(TestCase):
    """Tests para el modelo Organization"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.organization = Organization.objects.create(
            name='Test Optica',
            slug='test-optica',
            email='contact@testoptica.com',
            owner=self.user
        )
    
    def test_organization_creation(self):
        """Test de creación de organización"""
        self.assertEqual(self.organization.name, 'Test Optica')
        self.assertEqual(self.organization.slug, 'test-optica')
        self.assertTrue(self.organization.is_active)
    
    def test_owner_membership_auto_created(self):
        """Test que el owner se agrega automáticamente como miembro"""
        membership = OrganizationMember.objects.get(
            organization=self.organization,
            user=self.user
        )
        self.assertEqual(membership.role, 'owner')
        self.assertTrue(membership.is_active)


class SubscriptionPlanModelTest(TestCase):
    """Tests para el modelo SubscriptionPlan"""
    
    def setUp(self):
        self.free_plan = SubscriptionPlan.objects.create(
            name='Free Plan',
            slug='free',
            plan_type='free',
            price_monthly=0,
            price_yearly=0,
            max_users=1,
            max_appointments_month=50,
            max_patients=100
        )
        
        self.premium_plan = SubscriptionPlan.objects.create(
            name='Premium Plan',
            slug='premium',
            plan_type='professional',
            price_monthly=79.99,
            price_yearly=799.99,
            max_users=10,
            max_appointments_month=1000,
            max_patients=2000,
            whatsapp_integration=True,
            custom_branding=True
        )
    
    def test_plan_creation(self):
        """Test de creación de planes"""
        self.assertEqual(self.free_plan.name, 'Free Plan')
        self.assertEqual(self.premium_plan.price_monthly, 79.99)
        self.assertTrue(self.premium_plan.whatsapp_integration)


class SubscriptionModelTest(TestCase):
    """Tests para el modelo Subscription"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.organization = Organization.objects.create(
            name='Test Optica',
            slug='test-optica',
            email='contact@testoptica.com',
            owner=self.user
        )
        
        self.plan = SubscriptionPlan.objects.create(
            name='Test Plan',
            slug='test',
            plan_type='basic',
            price_monthly=29.99,
            price_yearly=299.99,
            max_users=3
        )
    
    def test_subscription_creation(self):
        """Test de creación de suscripción"""
        subscription = Subscription.objects.create(
            organization=self.organization,
            plan=self.plan,
            billing_cycle='monthly'
        )
        
        self.assertTrue(subscription.is_active)
        self.assertEqual(subscription.amount_paid, 29.99)
        self.assertIsNotNone(subscription.end_date)
    
    def test_subscription_expiration(self):
        """Test de expiración de suscripción"""
        # Crear suscripción expirada
        subscription = Subscription.objects.create(
            organization=self.organization,
            plan=self.plan,
            billing_cycle='monthly',
            start_date=timezone.now() - timedelta(days=60),
            end_date=timezone.now() - timedelta(days=30)
        )
        
        self.assertTrue(subscription.is_expired)
        self.assertEqual(subscription.days_remaining, 0)
    
    def test_organization_current_subscription(self):
        """Test de obtención de suscripción actual"""
        subscription = Subscription.objects.create(
            organization=self.organization,
            plan=self.plan,
            billing_cycle='monthly'
        )
        
        current = self.organization.current_subscription
        self.assertEqual(current.id, subscription.id)
        self.assertTrue(self.organization.is_subscription_active)


class TenantMiddlewareTest(TestCase):
    """Tests para el TenantMiddleware"""
    
    def setUp(self):
        self.factory = RequestFactory()
        self.middleware = TenantMiddleware(get_response=lambda r: None)
        
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.organization = Organization.objects.create(
            name='Test Optica',
            slug='test-optica',
            email='contact@testoptica.com',
            owner=self.user
        )
    
    def test_unauthenticated_user_no_tenant(self):
        """Test que usuarios no autenticados no tienen tenant"""
        request = self.factory.get('/')
        request.user = User()  # Usuario anónimo
        request.session = {}
        
        self.middleware.process_request(request)
        
        self.assertIsNone(request.organization)
    
    def test_authenticated_user_with_membership(self):
        """Test que usuarios con membresía obtienen tenant"""
        request = self.factory.get('/')
        request.user = self.user
        request.session = {}
        
        self.middleware.process_request(request)
        
        self.assertIsNotNone(request.organization)
        self.assertEqual(request.organization.id, self.organization.id)


class OrganizationViewsTest(TestCase):
    """Tests para las vistas de Organization"""
    
    def setUp(self):
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        self.client.login(username='testuser', password='testpass123')
    
    def test_organization_list_view(self):
        """Test de vista de lista de organizaciones"""
        response = self.client.get('/organizations/')
        self.assertEqual(response.status_code, 200)
    
    def test_organization_create_view_get(self):
        """Test de vista de creación GET"""
        response = self.client.get('/organizations/create/')
        self.assertEqual(response.status_code, 200)
    
    def test_organization_create_view_post(self):
        """Test de creación de organización vía POST"""
        # Crear plan gratuito primero
        SubscriptionPlan.objects.create(
            name='Free Plan',
            slug='free',
            plan_type='free',
            price_monthly=0,
            price_yearly=0
        )
        
        response = self.client.post('/organizations/create/', {
            'name': 'New Optica',
            'email': 'new@optica.com',
            'phone': '1234567890'
        })
        
        # Debe redirigir después de crear
        self.assertEqual(response.status_code, 302)
        
        # Verificar que se creó
        self.assertTrue(
            Organization.objects.filter(name='New Optica').exists()
        )
