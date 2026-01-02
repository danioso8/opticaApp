"""
Modelo de auditoría para rastrear acciones de los miembros del equipo
"""
from django.db import models
from django.contrib.auth.models import User
from apps.organizations.models import Organization


class AuditLog(models.Model):
    """Registro de auditoría de acciones de usuarios"""
    
    ACTION_CHOICES = [
        # Pacientes
        ('patient_create', 'Creó un paciente'),
        ('patient_edit', 'Editó un paciente'),
        ('patient_delete', 'Eliminó un paciente'),
        
        # Facturas
        ('invoice_create', 'Creó una factura'),
        ('invoice_edit', 'Editó una factura'),
        ('invoice_delete', 'Eliminó una factura'),
        ('invoice_void', 'Anuló una factura'),
        
        # Productos
        ('product_create', 'Creó un producto'),
        ('product_edit', 'Editó un producto'),
        ('product_delete', 'Eliminó un producto'),
        
        # Proveedores
        ('supplier_create', 'Creó un proveedor'),
        ('supplier_edit', 'Editó un proveedor'),
        ('supplier_delete', 'Eliminó un proveedor'),
        
        # Ventas
        ('sale_create', 'Registró una venta'),
        ('sale_edit', 'Editó una venta'),
        ('sale_delete', 'Eliminó una venta'),
        
        # Citas
        ('appointment_create', 'Creó una cita'),
        ('appointment_edit', 'Modificó una cita'),
        ('appointment_cancel', 'Canceló una cita'),
        ('appointment_complete', 'Completó una cita'),
        
        # Doctores
        ('doctor_create', 'Registró un doctor'),
        ('doctor_edit', 'Editó un doctor'),
        ('doctor_delete', 'Eliminó un doctor'),
        
        # Historia Clínica
        ('clinical_create', 'Creó historia clínica'),
        ('clinical_edit', 'Editó historia clínica'),
        
        # Exámenes
        ('exam_create', 'Registró un examen'),
        ('exam_edit', 'Editó un examen'),
        ('exam_delete', 'Eliminó un examen'),
        
        # Sesión
        ('login', 'Inició sesión'),
        ('logout', 'Cerró sesión'),
        
        # Equipo
        ('member_add', 'Agregó un miembro'),
        ('member_edit', 'Editó un miembro'),
        ('member_remove', 'Eliminó un miembro'),
        ('permissions_change', 'Cambió permisos'),
    ]
    
    # Usuario que realizó la acción
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='audit_logs')
    
    # Organización en la que se realizó la acción
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='audit_logs')
    
    # Tipo de acción
    action = models.CharField(max_length=50, choices=ACTION_CHOICES)
    
    # Descripción detallada
    description = models.TextField()
    
    # Modelo afectado (opcional)
    content_type = models.CharField(max_length=100, blank=True)
    object_id = models.PositiveIntegerField(null=True, blank=True)
    
    # Datos adicionales en JSON (opcional)
    metadata = models.JSONField(null=True, blank=True)
    
    # IP del usuario
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    
    # Timestamp
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Registro de Auditoría'
        verbose_name_plural = 'Registros de Auditoría'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['organization', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_action_display()} - {self.created_at.strftime('%d/%m/%Y %H:%M')}"
    
    def get_icon(self):
        """Retorna el ícono FontAwesome apropiado"""
        icon_map = {
            'patient_create': 'fa-user-plus',
            'patient_edit': 'fa-user-edit',
            'patient_delete': 'fa-user-minus',
            'invoice_create': 'fa-file-invoice',
            'invoice_edit': 'fa-file-invoice',
            'invoice_delete': 'fa-trash',
            'invoice_void': 'fa-ban',
            'product_create': 'fa-box',
            'product_edit': 'fa-edit',
            'product_delete': 'fa-trash',
            'supplier_create': 'fa-truck',
            'supplier_edit': 'fa-truck',
            'supplier_delete': 'fa-trash',
            'sale_create': 'fa-shopping-cart',
            'sale_edit': 'fa-edit',
            'sale_delete': 'fa-trash',
            'appointment_create': 'fa-calendar-plus',
            'appointment_edit': 'fa-calendar-edit',
            'appointment_cancel': 'fa-calendar-times',
            'appointment_complete': 'fa-calendar-check',
            'doctor_create': 'fa-user-md',
            'doctor_edit': 'fa-user-md',
            'doctor_delete': 'fa-user-minus',
            'clinical_create': 'fa-notes-medical',
            'clinical_edit': 'fa-notes-medical',
            'exam_create': 'fa-microscope',
            'exam_edit': 'fa-microscope',
            'exam_delete': 'fa-trash',
            'login': 'fa-sign-in-alt',
            'logout': 'fa-sign-out-alt',
            'member_add': 'fa-user-plus',
            'member_edit': 'fa-user-edit',
            'member_remove': 'fa-user-minus',
            'permissions_change': 'fa-key',
        }
        return icon_map.get(self.action, 'fa-circle')
    
    def get_color(self):
        """Retorna el color apropiado para el tipo de acción"""
        if 'create' in self.action or 'add' in self.action:
            return 'green'
        elif 'edit' in self.action or 'change' in self.action:
            return 'blue'
        elif 'delete' in self.action or 'remove' in self.action or 'void' in self.action or 'cancel' in self.action:
            return 'red'
        elif 'complete' in self.action:
            return 'purple'
        elif 'login' in self.action:
            return 'indigo'
        elif 'logout' in self.action:
            return 'gray'
        return 'gray'
