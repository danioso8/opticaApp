from django.db import models
from apps.organizations.base_models import TenantModel


class Doctor(TenantModel):
    """Modelo de Doctor/Optómetra"""
    
    SPECIALTY_CHOICES = [
        ('optometrist', 'Optómetra'),
        ('ophthalmologist', 'Oftalmólogo'),
        ('general', 'Médico General'),
        ('other', 'Otro'),
    ]
    
    ID_TYPE_CHOICES = [
        ('CC', 'Cédula de Ciudadanía'),
        ('CE', 'Cédula de Extranjería'),
        ('TI', 'Tarjeta de Identidad'),
        ('PA', 'Pasaporte'),
        ('RC', 'Registro Civil'),
        ('NIT', 'NIT'),
        ('OTRO', 'Otro'),
    ]
    
    # Información Personal
    full_name = models.CharField(max_length=200, verbose_name='Nombre Completo')
    identification_type = models.CharField(
        max_length=10,
        choices=ID_TYPE_CHOICES,
        blank=True,
        default='CC',
        verbose_name='Tipo de identificación'
    )
    identification = models.CharField(max_length=50, verbose_name='Cédula/ID')
    specialty = models.CharField(max_length=50, choices=SPECIALTY_CHOICES, default='optometrist', verbose_name='Especialidad')
    
    # Información Profesional
    professional_card = models.CharField(max_length=50, verbose_name='Tarjeta Profesional', blank=True)
    rethus = models.CharField(max_length=50, verbose_name='Registro RETHUS', blank=True, help_text='Registro Único Nacional del Talento Humano en Salud')
    graduation_date = models.DateField(verbose_name='Fecha de Graduación', null=True, blank=True)
    university = models.CharField(max_length=200, verbose_name='Universidad', blank=True)
    
    # Información de Contacto
    email = models.EmailField(verbose_name='Correo Electrónico', blank=True)
    phone = models.CharField(max_length=20, verbose_name='Teléfono')
    mobile = models.CharField(max_length=20, verbose_name='Celular', blank=True)
    address = models.TextField(verbose_name='Dirección', blank=True)
    
    # Horarios de Atención
    monday_schedule = models.CharField(max_length=100, verbose_name='Lunes', blank=True, help_text='Ej: 8:00-12:00, 14:00-18:00')
    tuesday_schedule = models.CharField(max_length=100, verbose_name='Martes', blank=True)
    wednesday_schedule = models.CharField(max_length=100, verbose_name='Miércoles', blank=True)
    thursday_schedule = models.CharField(max_length=100, verbose_name='Jueves', blank=True)
    friday_schedule = models.CharField(max_length=100, verbose_name='Viernes', blank=True)
    saturday_schedule = models.CharField(max_length=100, verbose_name='Sábado', blank=True)
    sunday_schedule = models.CharField(max_length=100, verbose_name='Domingo', blank=True)
    
    # Información Adicional
    signature = models.ImageField(upload_to='doctors/signatures/', verbose_name='Firma Digital', blank=True, null=True)
    photo = models.ImageField(upload_to='doctors/photos/', verbose_name='Foto', blank=True, null=True)
    bio = models.TextField(verbose_name='Biografía', blank=True, help_text='Breve descripción profesional')
    notes = models.TextField(verbose_name='Notas', blank=True)
    
    # Estado
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Registro')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Doctor/Optómetra'
        verbose_name_plural = 'Doctores/Optómetras'
        ordering = ['full_name']
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['professional_card']),
            models.Index(fields=['organization', 'identification']),
        ]
        unique_together = [
            ['organization', 'identification'],
        ]
    
    def __str__(self):
        return f"{self.full_name} - {self.get_specialty_display()}"
    
    @property
    def active_schedule_days(self):
        """Retorna los días con horario configurado"""
        days = []
        schedule_map = {
            'Lunes': self.monday_schedule,
            'Martes': self.tuesday_schedule,
            'Miércoles': self.wednesday_schedule,
            'Jueves': self.thursday_schedule,
            'Viernes': self.friday_schedule,
            'Sábado': self.saturday_schedule,
            'Domingo': self.sunday_schedule,
        }
        return [day for day, schedule in schedule_map.items() if schedule]
