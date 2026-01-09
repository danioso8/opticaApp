"""
Tests para workflows
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType

from apps.workflows.models import (
    WorkflowDefinition, WorkflowTransition, WorkflowAction,
    WorkflowInstance, WorkflowHistory, WorkflowApproval
)
from apps.workflows.services import (
    WorkflowService, WorkflowActionService,
    WorkflowHistoryService, WorkflowApprovalService
)

User = get_user_model()


class WorkflowDefinitionTestCase(TestCase):
    """Tests para definiciones de workflow"""
    
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
        
        # Crear un content type de prueba
        self.content_type = ContentType.objects.get_for_model(Organization)
    
    def test_create_workflow(self):
        """Test crear workflow"""
        workflow = WorkflowService.create_workflow(
            organization=self.org,
            name='Test Workflow',
            slug='test-workflow',
            content_type=self.content_type,
            initial_state='draft',
            created_by=self.user,
            states=[
                {'key': 'draft', 'name': 'Borrador', 'color': '#ccc'},
                {'key': 'review', 'name': 'En Revisión', 'color': '#ff0'},
                {'key': 'approved', 'name': 'Aprobado', 'color': '#0f0'},
            ],
            final_states=['approved']
        )
        
        self.assertEqual(workflow.name, 'Test Workflow')
        self.assertEqual(workflow.initial_state, 'draft')
        self.assertEqual(len(workflow.states), 3)
        self.assertTrue(workflow.is_final_state('approved'))
        self.assertFalse(workflow.is_final_state('draft'))


class WorkflowInstanceTestCase(TestCase):
    """Tests para instancias de workflow"""
    
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
        
        self.content_type = ContentType.objects.get_for_model(Organization)
        
        # Crear workflow
        self.workflow = WorkflowDefinition.objects.create(
            organization=self.org,
            name='Test Workflow',
            slug='test-workflow',
            content_type=self.content_type,
            initial_state='draft',
            created_by=self.user,
            states=[
                {'key': 'draft', 'name': 'Borrador'},
                {'key': 'approved', 'name': 'Aprobado'},
            ],
            final_states=['approved']
        )
    
    def test_start_workflow(self):
        """Test iniciar workflow"""
        instance = WorkflowService.start_workflow(
            workflow=self.workflow,
            content_object=self.org,
            started_by=self.user
        )
        
        self.assertEqual(instance.workflow, self.workflow)
        self.assertEqual(instance.current_state, 'draft')
        self.assertEqual(instance.status, 'active')
        self.assertTrue(instance.is_active())
        
        # Verificar que se creó historial
        history = instance.history.first()
        self.assertIsNotNone(history)
        self.assertEqual(history.to_state, 'draft')
    
    def test_workflow_transition(self):
        """Test ejecutar transición"""
        # Crear instancia
        instance = WorkflowService.start_workflow(
            workflow=self.workflow,
            content_object=self.org,
            started_by=self.user
        )
        
        # Crear transición
        transition = WorkflowTransition.objects.create(
            workflow=self.workflow,
            organization=self.org,
            name='Aprobar',
            from_state='draft',
            to_state='approved'
        )
        
        # Ejecutar transición
        success, message = WorkflowService.execute_transition(
            instance=instance,
            transition=transition,
            user=self.user,
            comment='Test transition'
        )
        
        self.assertTrue(success)
        instance.refresh_from_db()
        self.assertEqual(instance.current_state, 'approved')
        self.assertEqual(instance.status, 'completed')  # Estado final
    
    def test_get_available_transitions(self):
        """Test obtener transiciones disponibles"""
        instance = WorkflowService.start_workflow(
            workflow=self.workflow,
            content_object=self.org,
            started_by=self.user
        )
        
        # Crear transiciones
        transition1 = WorkflowTransition.objects.create(
            workflow=self.workflow,
            organization=self.org,
            name='Aprobar',
            from_state='draft',
            to_state='approved',
            order=1
        )
        
        transition2 = WorkflowTransition.objects.create(
            workflow=self.workflow,
            organization=self.org,
            name='Rechazar',
            from_state='draft',
            to_state='rejected',
            order=2
        )
        
        # Obtener disponibles
        available = WorkflowService.get_available_transitions(instance)
        
        self.assertEqual(available.count(), 2)
        self.assertEqual(available[0].order, 1)


class WorkflowApprovalTestCase(TestCase):
    """Tests para aprobaciones de workflow"""
    
    def setUp(self):
        """Setup test data"""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='testpass123'
        )
        
        self.approver = User.objects.create_user(
            username='approver',
            email='approver@test.com',
            password='testpass123'
        )
        
        from apps.organizations.models import Organization
        self.org = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
        
        self.content_type = ContentType.objects.get_for_model(Organization)
        
        # Crear workflow
        self.workflow = WorkflowDefinition.objects.create(
            organization=self.org,
            name='Test Workflow',
            slug='test-workflow',
            content_type=self.content_type,
            initial_state='draft',
            created_by=self.user,
            require_approval=True
        )
        
        # Crear transición que requiere aprobación
        self.transition = WorkflowTransition.objects.create(
            workflow=self.workflow,
            organization=self.org,
            name='Aprobar',
            from_state='draft',
            to_state='approved',
            require_approval=True
        )
        
        # Crear instancia
        self.instance = WorkflowService.start_workflow(
            workflow=self.workflow,
            content_object=self.org,
            started_by=self.user
        )
    
    def test_request_approval(self):
        """Test solicitar aprobación"""
        approval = WorkflowApprovalService.request_approval(
            instance=self.instance,
            transition=self.transition,
            requested_by=self.user,
            approver=self.approver
        )
        
        self.assertEqual(approval.status, 'pending')
        self.assertEqual(approval.requested_by, self.user)
        self.assertEqual(approval.approver, self.approver)
    
    def test_approve_transition(self):
        """Test aprobar transición"""
        # Solicitar aprobación
        approval = WorkflowApprovalService.request_approval(
            instance=self.instance,
            transition=self.transition,
            requested_by=self.user,
            approver=self.approver
        )
        
        # Aprobar
        success, message = WorkflowApprovalService.approve_transition(
            approval=approval,
            user=self.approver,
            comment='Aprobado por testing'
        )
        
        self.assertTrue(success)
        approval.refresh_from_db()
        self.assertEqual(approval.status, 'approved')
        
        # Verificar que la transición se ejecutó
        self.instance.refresh_from_db()
        self.assertEqual(self.instance.current_state, 'approved')
    
    def test_reject_transition(self):
        """Test rechazar transición"""
        # Solicitar aprobación
        approval = WorkflowApprovalService.request_approval(
            instance=self.instance,
            transition=self.transition,
            requested_by=self.user,
            approver=self.approver
        )
        
        # Rechazar
        success = WorkflowApprovalService.reject_transition(
            approval=approval,
            user=self.approver,
            comment='Rechazado por testing'
        )
        
        self.assertTrue(success)
        approval.refresh_from_db()
        self.assertEqual(approval.status, 'rejected')
        
        # Verificar que NO se ejecutó la transición
        self.instance.refresh_from_db()
        self.assertEqual(self.instance.current_state, 'draft')


class WorkflowHistoryTestCase(TestCase):
    """Tests para historial de workflows"""
    
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
        
        self.content_type = ContentType.objects.get_for_model(Organization)
        
        self.workflow = WorkflowDefinition.objects.create(
            organization=self.org,
            name='Test Workflow',
            slug='test-workflow',
            content_type=self.content_type,
            initial_state='draft',
            created_by=self.user
        )
        
        self.instance = WorkflowService.start_workflow(
            workflow=self.workflow,
            content_object=self.org,
            started_by=self.user
        )
    
    def test_log_transition(self):
        """Test registrar transición en historial"""
        history = WorkflowHistoryService.log_transition(
            instance=self.instance,
            from_state='draft',
            to_state='approved',
            user=self.user,
            comment='Test comment'
        )
        
        self.assertEqual(history.from_state, 'draft')
        self.assertEqual(history.to_state, 'approved')
        self.assertEqual(history.user, self.user)
    
    def test_get_instance_history(self):
        """Test obtener historial de instancia"""
        # La instancia ya tiene un registro (de start_workflow)
        history = WorkflowHistoryService.get_instance_history(self.instance)
        
        self.assertGreater(history.count(), 0)
