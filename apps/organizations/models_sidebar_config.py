"""
Modelos para configuración personalizada del sidebar
"""
import json
from django.db import models
from django.contrib.auth.models import User
from apps.organizations.models import Organization


class SidebarConfiguration(models.Model):
    """
    Configuración personalizada del sidebar para cada usuario/organización
    """
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sidebar_configs')
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='sidebar_configs', null=True, blank=True)
    config_data = models.TextField(
        default='{}',
        help_text="JSON con la configuración del sidebar: orden, visibilidad, submenús, etc."
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'organization']
        ordering = ['-updated_at']
        verbose_name = 'Configuración de Sidebar'
        verbose_name_plural = 'Configuraciones de Sidebar'

    def __str__(self):
        if self.organization:
            return f"Sidebar config for {self.user.username} - {self.organization.name}"
        return f"Sidebar config for {self.user.username}"

    def get_config(self):
        """Obtiene config_data como diccionario"""
        try:
            return json.loads(self.config_data) if self.config_data else {}
        except json.JSONDecodeError:
            return {}
    
    def set_config(self, data):
        """Establece config_data desde un diccionario"""
        self.config_data = json.dumps(data)

    @classmethod
    def get_or_create_config(cls, user, organization=None):
        """
        Obtiene o crea la configuración del sidebar para un usuario/organización
        """
        config, created = cls.objects.get_or_create(
            user=user,
            organization=organization,
            defaults={'config_data': json.dumps(cls.get_default_config())}
        )
        return config

    @staticmethod
    def get_default_config():
        """
        Retorna la configuración por defecto del sidebar
        """
        return {
            'items': [
                {'id': 'my-companies', 'order': 0, 'visible': True, 'parent': None},
                {'id': 'my-modules', 'order': 1, 'visible': True, 'parent': None},
                {'id': 'divider-1', 'order': 2, 'visible': True, 'parent': None},
                {'id': 'dashboard', 'order': 3, 'visible': True, 'parent': None},
                {'id': 'sales-dashboard', 'order': 4, 'visible': True, 'parent': None},
                {'id': 'billing-menu', 'order': 5, 'visible': True, 'parent': None},
                {'id': 'billing-basic', 'order': 0, 'visible': True, 'parent': 'billing-menu'},
                {'id': 'billing-electronic', 'order': 1, 'visible': True, 'parent': 'billing-menu'},
                {'id': 'cash-register-menu', 'order': 2, 'visible': True, 'parent': 'billing-menu'},
                {'id': 'cash-dashboard', 'order': 0, 'visible': True, 'parent': 'cash-register-menu'},
                {'id': 'cash-registers', 'order': 1, 'visible': True, 'parent': 'cash-register-menu'},
                {'id': 'cash-movements', 'order': 2, 'visible': True, 'parent': 'cash-register-menu'},
                {'id': 'cash-closures', 'order': 3, 'visible': True, 'parent': 'cash-register-menu'},
                {'id': 'cash-reports', 'order': 4, 'visible': True, 'parent': 'cash-register-menu'},
                {'id': 'doctors', 'order': 6, 'visible': True, 'parent': None},
                {'id': 'payroll-menu', 'order': 7, 'visible': True, 'parent': None},
                {'id': 'employees', 'order': 0, 'visible': True, 'parent': 'payroll-menu'},
                {'id': 'payroll-electronic', 'order': 1, 'visible': True, 'parent': 'payroll-menu'},
                {'id': 'payroll-employees', 'order': 2, 'visible': True, 'parent': 'payroll-menu'},
                {'id': 'payroll-workflow', 'order': 3, 'visible': True, 'parent': 'payroll-menu'},
                {'id': 'divider-2', 'order': 4, 'visible': True, 'parent': 'payroll-menu'},
                {'id': 'contracts', 'order': 5, 'visible': True, 'parent': 'payroll-menu'},
                {'id': 'vacations', 'order': 6, 'visible': True, 'parent': 'payroll-menu'},
                # Agregar más items aquí según el sidebar completo
            ],
            'mini_sidebar': False,
            'custom_css': {}
        }

    def update_item_order(self, item_id, new_order, parent=None):
        """
        Actualiza el orden de un item del sidebar
        """
        config = self.get_config()
        items = config.get('items', [])
        
        # Buscar el item
        for item in items:
            if item['id'] == item_id:
                item['order'] = new_order
                if parent is not None:
                    item['parent'] = parent
                break
        
        config['items'] = items
        self.set_config(config)
        self.save()
        return self

    def toggle_item_visibility(self, item_id):
        """
        Cambia la visibilidad de un item
        """
        config = self.get_config()
        items = config.get('items', [])
        
        for item in items:
            if item['id'] == item_id:
                item['visible'] = not item.get('visible', True)
                break
        
        config['items'] = items
        self.set_config(config)
        self.save()
        return self

    def move_item_to_submenu(self, item_id, parent_id):
        """
        Mueve un item a un submenú
        """
        config = self.get_config()
        items = config.get('items', [])
        
        # Buscar el item y actualizarlo
        for item in items:
            if item['id'] == item_id:
                item['parent'] = parent_id
                # Resetear el orden dentro del nuevo padre
                item['order'] = self.get_next_order_in_parent(parent_id)
                break
        
        config['items'] = items
        self.set_config(config)
        self.save()
        return self

    def remove_item_from_submenu(self, item_id):
        """
        Saca un item de un submenú y lo pone en el nivel principal
        """
        config = self.get_config()
        items = config.get('items', [])
        
        for item in items:
            if item['id'] == item_id:
                item['parent'] = None
                # Resetear el orden en el nivel principal
                item['order'] = self.get_next_order_in_parent(None)
                break
        
        config['items'] = items
        self.set_config(config)
        self.save()
        return self

    def get_next_order_in_parent(self, parent_id):
        """
        Obtiene el siguiente número de orden disponible para un padre específico
        """
        config = self.get_config()
        items = config.get('items', [])
        max_order = -1
        
        for item in items:
            if item.get('parent') == parent_id:
                if item['order'] > max_order:
                    max_order = item['order']
        
        return max_order + 1

    def get_ordered_items(self, parent=None):
        """
        Obtiene los items ordenados para un nivel específico (root o submenú)
        """
        config = self.get_config()
        items = config.get('items', [])
        filtered = [item for item in items if item.get('parent') == parent and item.get('visible', True)]
        return sorted(filtered, key=lambda x: x['order'])
