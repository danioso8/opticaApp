from django.db import models
from django.core.validators import RegexValidator
from apps.organizations.base_models import TenantModel

# Importar modelos de historia clínica
from .models_clinical import ClinicalHistory, ClinicalHistoryAttachment

# Importar modelo de doctores
from .models_doctors import Doctor


class Patient(TenantModel):
    """Modelo de Paciente/Cliente"""
    GENDER_CHOICES = [
        ('M', 'Masculino'),
        ('F', 'Femenino'),
        ('O', 'Otro'),
    ]

    # Información personal
    full_name = models.CharField(max_length=200, verbose_name="Nombre completo")
    identification = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        verbose_name="Identificación"
    )
    date_of_birth = models.DateField(null=True, blank=True, verbose_name="Fecha de nacimiento")
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, verbose_name="Género")

    # Información de contacto
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Formato válido: '+999999999'. Hasta 15 dígitos."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        verbose_name="Teléfono"
    )
    email = models.EmailField(blank=True, verbose_name="Correo electrónico")
    address = models.TextField(blank=True, verbose_name="Dirección")

    # Información médica básica
    allergies = models.TextField(blank=True, verbose_name="Alergias")
    medical_conditions = models.TextField(blank=True, verbose_name="Condiciones médicas")
    current_medications = models.TextField(blank=True, verbose_name="Medicamentos actuales")

    # Datos adicionales de óptica
    occupation = models.CharField(max_length=200, blank=True, verbose_name="Ocupación")
    residence_area = models.CharField(max_length=200, blank=True, verbose_name="Zona de residencia")
    business_name = models.CharField(max_length=200, blank=True, verbose_name="Nombre de empresa")
    business_address = models.TextField(blank=True, verbose_name="Dirección de empresa")
    business_phone = models.CharField(max_length=17, blank=True, verbose_name="Teléfono de empresa")
    business_type = models.CharField(max_length=200, blank=True, verbose_name="Tipo encadenado")
    civil_status = models.CharField(max_length=50, blank=True, verbose_name="Estado civil")
    
    # Información bancaria
    bank_entity = models.CharField(max_length=200, blank=True, verbose_name="Entidad bancaria")
    account_number = models.CharField(max_length=50, blank=True, verbose_name="# Cuenta bancaria")

    # Información de acompañante
    has_companion = models.BooleanField(default=False, verbose_name="Viene con acompañante")
    companion_name = models.CharField(max_length=200, blank=True, verbose_name="Nombre del acompañante")
    companion_relationship = models.CharField(max_length=100, blank=True, verbose_name="Relación con el paciente")
    companion_phone = models.CharField(max_length=17, blank=True, verbose_name="Teléfono del acompañante")

    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'phone_number']),
            models.Index(fields=['organization', 'identification']),
        ]
        unique_together = [
            ['organization', 'identification'],
        ]

    def __str__(self):
        return self.full_name

    @property
    def age(self):
        """Calcula la edad del paciente"""
        if self.date_of_birth:
            from datetime import date
            today = date.today()
            return today.year - self.date_of_birth.year - (
                (today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day)
            )
        return None
