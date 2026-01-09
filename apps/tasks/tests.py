"""
Tests para tareas
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta

from apps.tasks.models import (
    TaskCategory, Task, TaskComment, TaskActivity,
    TaskChecklist, TaskReminder
)
from apps.tasks.services import (
    TaskService, TaskCommentService, TaskChecklistService,
    TaskReminderService, create_default_categories
)

User = get_user_model()


class TaskCategoryTestCase(TestCase):
    """Tests para categorías de tareas"""
    
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
    
    def test_create_category(self):
        """Test crear categoría"""
        category = TaskCategory.objects.create(
            name='Test Category',
            slug='test-category',
            organization=self.org,
            created_by=self.user,
            color='#3498db'
        )
        
        self.assertEqual(category.name, 'Test Category')
        self.assertTrue(category.is_active)
    
    def test_create_default_categories(self):
        """Test crear categorías predeterminadas"""
        categories = create_default_categories(self.org, self.user)
        
        self.assertEqual(len(categories), 5)
        self.assertTrue(TaskCategory.objects.filter(slug='general').exists())
        self.assertTrue(TaskCategory.objects.filter(slug='ventas').exists())


class TaskTestCase(TestCase):
    """Tests para tareas"""
    
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
        
        self.category = TaskCategory.objects.create(
            name='Test Category',
            slug='test-category',
            organization=self.org,
            created_by=self.user
        )
    
    def test_create_task(self):
        """Test crear tarea"""
        task = TaskService.create_task(
            organization=self.org,
            created_by=self.user,
            title='Test Task',
            description='Test description',
            category=self.category,
            priority='high'
        )
        
        self.assertEqual(task.title, 'Test Task')
        self.assertEqual(task.status, 'pending')
        self.assertEqual(task.priority, 'high')
        
        # Verificar que se creó actividad
        self.assertTrue(task.activities.filter(action='created').exists())
    
    def test_assign_task(self):
        """Test asignar tarea"""
        task = Task.objects.create(
            organization=self.org,
            created_by=self.user,
            title='Test Task'
        )
        
        TaskService.assign_task(task, self.user, self.user)
        
        task.refresh_from_db()
        self.assertEqual(task.assigned_to, self.user)
        self.assertEqual(task.status, 'in_progress')
    
    def test_complete_task(self):
        """Test completar tarea"""
        task = Task.objects.create(
            organization=self.org,
            created_by=self.user,
            title='Test Task'
        )
        
        task.complete()
        
        self.assertEqual(task.status, 'completed')
        self.assertIsNotNone(task.completed_at)
        self.assertEqual(task.progress, 100)
    
    def test_is_overdue(self):
        """Test verificar si está vencida"""
        task = Task.objects.create(
            organization=self.org,
            created_by=self.user,
            title='Test Task',
            due_date=timezone.now() - timedelta(days=1)
        )
        
        self.assertTrue(task.is_overdue())
        
        # Completada no está vencida
        task.status = 'completed'
        task.save()
        self.assertFalse(task.is_overdue())
    
    def test_is_due_soon(self):
        """Test verificar si vence pronto"""
        task = Task.objects.create(
            organization=self.org,
            created_by=self.user,
            title='Test Task',
            due_date=timezone.now() + timedelta(hours=12)
        )
        
        self.assertTrue(task.is_due_soon(hours=24))
        self.assertFalse(task.is_due_soon(hours=6))


class TaskCommentTestCase(TestCase):
    """Tests para comentarios de tareas"""
    
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
        
        self.task = Task.objects.create(
            organization=self.org,
            created_by=self.user,
            title='Test Task'
        )
    
    def test_add_comment(self):
        """Test agregar comentario"""
        comment = TaskCommentService.add_comment(
            task=self.task,
            user=self.user,
            comment='Test comment'
        )
        
        self.assertEqual(comment.comment, 'Test comment')
        self.assertEqual(comment.task, self.task)
        
        # Verificar actividad
        self.assertTrue(self.task.activities.filter(action='commented').exists())
    
    def test_reply_to_comment(self):
        """Test responder a comentario"""
        parent = TaskComment.objects.create(
            task=self.task,
            organization=self.org,
            user=self.user,
            comment='Parent comment'
        )
        
        reply = TaskCommentService.add_comment(
            task=self.task,
            user=self.user,
            comment='Reply',
            parent_comment=parent
        )
        
        self.assertEqual(reply.parent_comment, parent)


class TaskChecklistTestCase(TestCase):
    """Tests para checklists"""
    
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
        
        self.task = Task.objects.create(
            organization=self.org,
            created_by=self.user,
            title='Test Task'
        )
    
    def test_create_checklist(self):
        """Test crear checklist"""
        checklist = TaskChecklistService.create_checklist(
            task=self.task,
            created_by=self.user,
            title='Test Checklist',
            items=['Item 1', 'Item 2', 'Item 3']
        )
        
        self.assertEqual(checklist.title, 'Test Checklist')
        self.assertEqual(len(checklist.items), 3)
        self.assertEqual(checklist.get_completion_percentage(), 0)
    
    def test_toggle_item(self):
        """Test cambiar estado de item"""
        checklist = TaskChecklistService.create_checklist(
            task=self.task,
            created_by=self.user,
            title='Test Checklist',
            items=['Item 1', 'Item 2']
        )
        
        # Completar primer item
        TaskChecklistService.toggle_item(checklist, 0)
        checklist.refresh_from_db()
        
        self.assertTrue(checklist.items[0]['completed'])
        self.assertEqual(checklist.get_completion_percentage(), 50)
        
        # Completar segundo item
        TaskChecklistService.toggle_item(checklist, 1)
        checklist.refresh_from_db()
        
        self.assertTrue(checklist.is_complete())
        self.assertEqual(checklist.get_completion_percentage(), 100)


class TaskServiceTestCase(TestCase):
    """Tests para servicios de tareas"""
    
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
    
    def test_get_user_tasks(self):
        """Test obtener tareas de usuario"""
        # Crear tareas
        Task.objects.create(
            organization=self.org,
            created_by=self.user,
            assigned_to=self.user,
            title='Task 1',
            status='pending'
        )
        
        Task.objects.create(
            organization=self.org,
            created_by=self.user,
            assigned_to=self.user,
            title='Task 2',
            status='completed'
        )
        
        # Obtener todas las tareas
        tasks = TaskService.get_user_tasks(self.user)
        self.assertEqual(tasks.count(), 2)
        
        # Filtrar por estado
        pending = TaskService.get_user_tasks(self.user, status='pending')
        self.assertEqual(pending.count(), 1)
    
    def test_get_overdue_tasks(self):
        """Test obtener tareas vencidas"""
        # Tarea vencida
        Task.objects.create(
            organization=self.org,
            created_by=self.user,
            title='Overdue Task',
            due_date=timezone.now() - timedelta(days=1)
        )
        
        # Tarea no vencida
        Task.objects.create(
            organization=self.org,
            created_by=self.user,
            title='Future Task',
            due_date=timezone.now() + timedelta(days=1)
        )
        
        overdue = TaskService.get_overdue_tasks(self.org)
        self.assertEqual(overdue.count(), 1)
