from django.db import models
from django.core.validators import RegexValidator


class Patient(models.Model):
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
        unique=True,
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

    # Metadatos
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Fecha de registro")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Última actualización")
    is_active = models.BooleanField(default=True, verbose_name="Activo")

    class Meta:
        verbose_name = "Paciente"
        verbose_name_plural = "Pacientes"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['phone_number']),
            models.Index(fields=['identification']),
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
