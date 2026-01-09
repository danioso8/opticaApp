"""
Tests para el sistema de reportes.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.organizations.models import Organization
from apps.reports.models import ReportTemplate, Report, ScheduledReport
from apps.reports.services import ReportService, create_default_templates

User = get_user_model()


class ReportTemplateTestCase(TestCase):
    """Tests para ReportTemplate."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.organization = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
    
    def test_create_template(self):
        """Prueba crear una plantilla."""
        template = ReportTemplate.objects.create(
            name='Test Report',
            report_type='sales',
            organization=self.organization,
            created_by=self.user,
            columns=['date', 'amount', 'status']
        )
        
        self.assertIsNotNone(template)
        self.assertEqual(template.name, 'Test Report')
        self.assertEqual(len(template.columns), 3)


class ReportServiceTestCase(TestCase):
    """Tests para ReportService."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.organization = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
        
        self.template = ReportTemplate.objects.create(
            name='Sales Report',
            report_type='sales',
            organization=self.organization,
            created_by=self.user,
            columns=['date', 'total']
        )
    
    def test_generate_report(self):
        """Prueba generar un reporte."""
        report = ReportService.generate_report(
            template=self.template,
            organization=self.organization,
            user=self.user,
            output_format='csv'
        )
        
        self.assertIsNotNone(report)
        self.assertEqual(report.status, 'completed')
        self.assertIsNotNone(report.completed_at)
    
    def test_create_default_templates(self):
        """Prueba crear plantillas por defecto."""
        count = create_default_templates()
        self.assertGreater(count, 0)
        
        templates = ReportTemplate.objects.filter(is_system=True)
        self.assertGreater(templates.count(), 0)


class ScheduledReportTestCase(TestCase):
    """Tests para ScheduledReport."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.organization = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
        
        self.template = ReportTemplate.objects.create(
            name='Daily Report',
            report_type='sales',
            organization=self.organization,
            created_by=self.user
        )
    
    def test_create_scheduled_report(self):
        """Prueba crear un reporte programado."""
        scheduled = ScheduledReport.objects.create(
            name='Daily Sales',
            template=self.template,
            organization=self.organization,
            frequency='daily',
            created_by=self.user,
            recipients=['test@example.com']
        )
        
        self.assertIsNotNone(scheduled)
        self.assertEqual(scheduled.frequency, 'daily')
    
    def test_calculate_next_run(self):
        """Prueba calcular próxima ejecución."""
        scheduled = ScheduledReport.objects.create(
            name='Weekly Report',
            template=self.template,
            organization=self.organization,
            frequency='weekly',
            created_by=self.user
        )
        
        next_run = scheduled.calculate_next_run()
        self.assertIsNotNone(next_run)
        self.assertGreater(next_run, timezone.now())
