from django.test import TestCase
from django.contrib.auth.models import User
from apps.organizations.models import Organization, ModulePermission
from apps.permissions.models import Role, Permission, UserRole, RolePermission
from apps.permissions.services import PermissionService, RoleService


class PermissionServiceTestCase(TestCase):
    """Tests para PermissionService"""
    
    def setUp(self):
        """Configuración inicial para tests"""
        # Crear organización de prueba
        self.org = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
        
        # Crear usuario de prueba
        self.user = User.objects.create_user(
            username='testuser',
            email='test@test.com',
            password='password123'
        )
        
        # Crear módulo de prueba
        self.module = ModulePermission.objects.create(
            organization=self.org,
            code='patients',
            name='Pacientes',
            description='Gestión de pacientes'
        )
        
        # Crear permiso de prueba
        self.permission = Permission.objects.create(
            organization=self.org,
            codename='patients.view',
            name='Ver Pacientes',
            module=self.module,
            actions={'view': True, 'add': False, 'change': False, 'delete': False}
        )
        
        # Crear rol de prueba
        self.role = Role.objects.create(
            organization=self.org,
            name='Recepcionista',
            description='Rol de prueba'
        )
        
        # Asignar permiso al rol
        RolePermission.objects.create(
            organization=self.org,
            role=self.role,
            permission=self.permission
        )
    
    def test_user_has_permission_after_role_assignment(self):
        """Test: Usuario tiene permisos después de asignar rol"""
        # Asignar rol al usuario
        service = PermissionService(self.user, self.org)
        service.assign_role(self.role)
        
        # Verificar que tiene el permiso
        self.assertTrue(service.has_permission('patients', 'view'))
    
    def test_user_loses_permission_after_role_removal(self):
        """Test: Usuario pierde permisos después de remover rol"""
        # Asignar y luego remover rol
        service = PermissionService(self.user, self.org)
        service.assign_role(self.role)
        service.remove_role(self.role)
        
        # Verificar que NO tiene el permiso
        self.assertFalse(service.has_permission('patients', 'view'))
    
    def test_permission_cache_invalidation(self):
        """Test: Caché se invalida correctamente"""
        service = PermissionService(self.user, self.org)
        
        # Asignar rol (crea caché)
        service.assign_role(self.role)
        initial_perms = service.get_all_permissions()
        
        # Remover rol (debe invalidar caché)
        service.remove_role(self.role)
        updated_perms = service.get_all_permissions()
        
        # Verificar que los permisos cambiaron
        self.assertNotEqual(initial_perms, updated_perms)


class RoleServiceTestCase(TestCase):
    """Tests para RoleService"""
    
    def setUp(self):
        self.org = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
        self.service = RoleService(self.org)
    
    def test_create_role(self):
        """Test: Crear un nuevo rol"""
        role = self.service.create_role(
            name='Doctor',
            description='Rol de doctor'
        )
        
        self.assertEqual(role.name, 'Doctor')
        self.assertEqual(role.organization, self.org)
    
    def test_clone_role(self):
        """Test: Clonar un rol con sus permisos"""
        # Crear rol original con permiso
        original_role = self.service.create_role(name='Original')
        
        # El test completo requiere módulos y permisos configurados
        # Este es un test básico
        cloned_role = self.service.clone_role(original_role, 'Clonado')
        
        self.assertEqual(cloned_role.name, 'Clonado')
        self.assertNotEqual(cloned_role.id, original_role.id)
