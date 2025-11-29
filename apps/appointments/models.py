from django.db import models
from django.utils import timezone
from django.core.validators import RegexValidator
from django.conf import settings


class AppointmentConfiguration(models.Model):
    """Configuración global del sistema de citas"""
    is_open = models.BooleanField(
        default=True,
        verbose_name="Sistema abierto",
        help_text="Activa/desactiva el sistema de agendamiento"
    )
    slot_duration = models.IntegerField(
        default=30,
        verbose_name="Duración de cita (minutos)"
    )
    max_daily_appointments = models.IntegerField(
        default=20,
        verbose_name="Máximo de citas diarias"
    )
    advance_booking_days = models.IntegerField(
        default=30,
        verbose_name="Días de anticipación para agendar"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Configuración de Citas"
        verbose_name_plural = "Configuración de Citas"

    def __str__(self):
        return f"Configuración - {'Abierto' if self.is_open else 'Cerrado'}"

    @classmethod
    def get_config(cls):
        """Obtiene o crea la configuración"""
        config, created = cls.objects.get_or_create(pk=1)
        return config


class WorkingHours(models.Model):
    """Horarios de atención por día de la semana"""
    DAYS_OF_WEEK = [
        (0, 'Lunes'),
        (1, 'Martes'),
        (2, 'Miércoles'),
        (3, 'Jueves'),
        (4, 'Viernes'),
        (5, 'Sábado'),
        (6, 'Domingo')
    ]

    day_of_week = models.IntegerField(
        choices=DAYS_OF_WEEK,
        verbose_name="Día de la semana"
    )
    start_time = models.TimeField(verbose_name="Hora inicio")
    end_time = models.TimeField(verbose_name="Hora fin")
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Horario de Atención"
        verbose_name_plural = "Horarios de Atención"
        ordering = ['day_of_week', 'start_time']
        unique_together = ['day_of_week', 'start_time']

    def __str__(self):
        return f"{self.get_day_of_week_display()} - {self.start_time} a {self.end_time}"


class SpecificDateSchedule(models.Model):
    """Horarios para fechas específicas (sobrescribe WorkingHours)"""
    date = models.DateField(
        verbose_name="Fecha específica"
    )
    start_time = models.TimeField(verbose_name="Hora inicio")
    end_time = models.TimeField(verbose_name="Hora fin")
    is_active = models.BooleanField(
        default=True,
        verbose_name="Activo"
    )
    notes = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Notas"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='specific_schedules'
    )

    class Meta:
        verbose_name = "Horario Específico"
        verbose_name_plural = "Horarios Específicos"
        ordering = ['date', 'start_time']
        unique_together = ['date', 'start_time']

    def __str__(self):
        return f"{self.date} - {self.start_time} a {self.end_time}"


class BlockedDate(models.Model):
    """Fechas bloqueadas (festivos, vacaciones, etc.)"""
    date = models.DateField(
        unique=True,
        verbose_name="Fecha bloqueada"
    )
    reason = models.CharField(
        max_length=200,
        verbose_name="Motivo"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='blocked_dates'
    )

    class Meta:
        verbose_name = "Fecha Bloqueada"
        verbose_name_plural = "Fechas Bloqueadas"
        ordering = ['-date']

    def __str__(self):
        return f"{self.date} - {self.reason}"


class Appointment(models.Model):
    """Cita agendada"""
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('confirmed', 'Confirmada'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
        ('no_show', 'No asistió'),
    ]

    # Datos básicos del usuario (mínimos requeridos)
    full_name = models.CharField(
        max_length=200,
        verbose_name="Nombre completo"
    )

    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Formato válido: '+999999999'. Hasta 15 dígitos."
    )
    phone_number = models.CharField(
        validators=[phone_regex],
        max_length=17,
        verbose_name="Número de celular"
    )

    # Fecha y hora
    appointment_date = models.DateField(verbose_name="Fecha de cita")
    appointment_time = models.TimeField(verbose_name="Hora de cita")

    # Estado y seguimiento
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="Estado"
    )

    notes = models.TextField(
        blank=True,
        verbose_name="Notas",
        help_text="Notas adicionales del administrador"
    )

    # Metadatos
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Fecha de creación"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="Última actualización"
    )

    # Relación con paciente (opcional, se crea después si no existe)
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='appointments',
        verbose_name="Paciente"
    )

    # Usuario que atendió (optometrista)
    attended_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='attended_appointments',
        verbose_name="Atendido por"
    )

    class Meta:
        verbose_name = "Cita"
        verbose_name_plural = "Citas"
        ordering = ['-appointment_date', '-appointment_time']
        unique_together = ['appointment_date', 'appointment_time']
        indexes = [
            models.Index(fields=['appointment_date', 'status']),
            models.Index(fields=['phone_number']),
        ]

    def __str__(self):
        return f"{self.full_name} - {self.appointment_date} {self.appointment_time}"

    @property
    def datetime(self):
        """Combina fecha y hora en un datetime"""
        from datetime import datetime
        dt = datetime.combine(self.appointment_date, self.appointment_time)
        # Hacer el datetime aware (con zona horaria)
        return timezone.make_aware(dt) if timezone.is_naive(dt) else dt

    @property
    def is_past(self):
        """Verifica si la cita ya pasó"""
        return self.datetime < timezone.now()

    @property
    def is_today(self):
        """Verifica si la cita es hoy"""
        return self.appointment_date == timezone.now().date()

    def can_be_cancelled(self):
        """Verifica si la cita puede ser cancelada"""
        return self.status in ['pending', 'confirmed'] and not self.is_past


class TimeSlot(models.Model):
    """Slots de tiempo disponibles (generados dinámicamente)"""
    date = models.DateField(verbose_name="Fecha")
    time = models.TimeField(verbose_name="Hora")
    is_available = models.BooleanField(
        default=True,
        verbose_name="Disponible"
    )
    manually_blocked = models.BooleanField(
        default=False,
        verbose_name="Bloqueado manualmente"
    )
    blocked_reason = models.CharField(
        max_length=200,
        blank=True,
        verbose_name="Razón de bloqueo"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "Slot de Tiempo"
        verbose_name_plural = "Slots de Tiempo"
        unique_together = ['date', 'time']
        ordering = ['date', 'time']
        indexes = [
            models.Index(fields=['date', 'is_available']),
        ]

    def __str__(self):
        status = "Disponible" if self.is_available else "Ocupado"
        return f"{self.date} {self.time} - {status}"
