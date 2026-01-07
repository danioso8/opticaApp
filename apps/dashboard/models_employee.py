from django.db import models
from django.contrib.auth.models import User
from apps.organizations.models import Organization


class Employee(models.Model):
    """Modelo para gestionar empleados de la organización"""
    
    DOCUMENT_TYPE_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('PA', 'Pasaporte'),
        ('TI', 'Tarjeta de Identidad'),
    ]
    
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]
    
    POSITION_CHOICES = [
        ('RECEPCIONISTA', 'Recepcionista'),
        ('VENDEDOR', 'Vendedor'),
        ('TECNICO_OPTICO', 'Técnico Óptico'),
        ('ASISTENTE', 'Asistente'),
        ('GERENTE', 'Gerente'),
        ('ADMINISTRATIVO', 'Administrativo'),
        ('CONTADOR', 'Contador'),
        ('OTRO', 'Otro'),
    ]
    
    # Relación con organización
    organization = models.ForeignKey(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='employees',
        verbose_name='Organización'
    )
    
    # Vinculación con usuario (opcional - para dar acceso al sistema)
    user = models.OneToOneField(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='employee_profile',
        verbose_name='Usuario del Sistema'
    )
    
    # Información personal
    first_name = models.CharField('Nombres', max_length=100)
    last_name = models.CharField('Apellidos', max_length=100)
    document_type = models.CharField('Tipo de Documento', max_length=2, choices=DOCUMENT_TYPE_CHOICES, default='CC')
    identification = models.CharField('Número de Identificación', max_length=20)
    birth_date = models.DateField('Fecha de Nacimiento', null=True, blank=True)
    gender = models.CharField('Género', max_length=1, choices=GENDER_CHOICES, null=True, blank=True)
    
    # Información de contacto
    email = models.EmailField('Correo Electrónico', blank=True)
    phone = models.CharField('Teléfono', max_length=20, blank=True)
    address = models.TextField('Dirección', blank=True)
    
    # Información laboral
    position = models.CharField('Cargo', max_length=50, choices=POSITION_CHOICES)
    department = models.CharField('Departamento', max_length=100, blank=True)
    hire_date = models.DateField('Fecha de Contratación')
    salary = models.DecimalField('Salario', max_digits=12, decimal_places=2, null=True, blank=True)
    is_active = models.BooleanField('Activo', default=True)
    
    # Nómina
    incluir_en_nomina = models.BooleanField('Incluir en Nómina', default=False, 
                                            help_text='Si está activado, este empleado aparecerá en el módulo de nómina electrónica')
    ciudad = models.CharField('Ciudad', max_length=100, blank=True, default='Bogotá')
    departamento_ubicacion = models.CharField('Departamento/Estado', max_length=100, blank=True, default='Cundinamarca')
    
    # Metadata
    created_at = models.DateTimeField('Fecha de Creación', auto_now_add=True)
    updated_at = models.DateTimeField('Última Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Empleado'
        verbose_name_plural = 'Empleados'
        ordering = ['-created_at']
        constraints = [
            models.UniqueConstraint(
                fields=['organization', 'identification'],
                name='unique_employee_per_organization'
            )
        ]
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} - {self.get_position_display()}"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
