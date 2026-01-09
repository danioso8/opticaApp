"""
Modelos para el sistema de gestión de tareas
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.organizations.base_models import TenantModel
import json

User = get_user_model()


class JSONFieldCompatible(models.TextField):
    """Campo compatible con SQLite y PostgreSQL para almacenar JSON"""
    
    def __init__(self, *args, **kwargs):
        self.default_value = kwargs.pop('default', dict)
        kwargs['default'] = self._get_default
        super().__init__(*args, **kwargs)
    
    def _get_default(self):
        if callable(self.default_value):
            value = self.default_value()
        else:
            value = self.default_value
        return json.dumps(value) if value else '{}'
    
    def from_db_value(self, value, expression, connection):
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return value
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    def to_python(self, value):
        if value is None:
            return None
        if isinstance(value, (dict, list)):
            return value
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return value
    
    def get_prep_value(self, value):
        if value is None:
            return None
        if isinstance(value, str):
            return value
        return json.dumps(value)


class TaskCategory(TenantModel):
    """
    Categorías para organizar tareas
    Permite clasificar tareas por tipo o área
    """
    
    name = models.CharField('Nombre', max_length=100)
    slug = models.SlugField('Slug', max_length=100)
    description = models.TextField('Descripción', blank=True)
    
    color = models.CharField(
        'Color',
        max_length=7,
        default='#3498db',
        help_text='Color en formato hexadecimal (#RRGGBB)'
    )
    
    icon = models.CharField(
        'Icono',
        max_length=50,
        blank=True,
        help_text='Clase de icono (ej: fas fa-tasks)'
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name='Organización',
        related_name='task_categories'
    )
    
    is_active = models.BooleanField('Activa', default=True)
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Creado por',
        related_name='created_task_categories'
    )
    
    created_at = models.DateTimeField('Fecha Creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Categoría de Tarea'
        verbose_name_plural = 'Categorías de Tareas'
        ordering = ['name']
        unique_together = [['organization', 'slug']]
        indexes = [
            models.Index(fields=['organization', 'is_active']),
        ]
    
    def __str__(self):
        return self.name


class Task(TenantModel):
    """
    Tarea individual con asignación, prioridad y seguimiento
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('in_progress', 'En Progreso'),
        ('on_hold', 'En Espera'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
    ]
    
    PRIORITY_CHOICES = [
        ('low', 'Baja'),
        ('medium', 'Media'),
        ('high', 'Alta'),
        ('urgent', 'Urgente'),
    ]
    
    title = models.CharField('Título', max_length=255)
    description = models.TextField('Descripción', blank=True)
    
    category = models.ForeignKey(
        TaskCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Categoría',
        related_name='tasks'
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name='Organización',
        related_name='tasks'
    )
    
    status = models.CharField(
        'Estado',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    
    priority = models.CharField(
        'Prioridad',
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='medium',
        db_index=True
    )
    
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Asignado a',
        related_name='assigned_tasks'
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Creado por',
        related_name='created_tasks'
    )
    
    # Relación genérica con cualquier objeto
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Tipo de Contenido'
    )
    object_id = models.PositiveIntegerField('ID Objeto', null=True, blank=True)
    related_object = GenericForeignKey('content_type', 'object_id')
    
    due_date = models.DateTimeField(
        'Fecha Límite',
        null=True,
        blank=True,
        db_index=True
    )
    
    start_date = models.DateTimeField(
        'Fecha Inicio',
        null=True,
        blank=True
    )
    
    completed_at = models.DateTimeField(
        'Completada en',
        null=True,
        blank=True
    )
    
    estimated_hours = models.DecimalField(
        'Horas Estimadas',
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Tiempo estimado en horas'
    )
    
    actual_hours = models.DecimalField(
        'Horas Reales',
        max_digits=6,
        decimal_places=2,
        null=True,
        blank=True,
        help_text='Tiempo real invertido en horas'
    )
    
    progress = models.IntegerField(
        'Progreso',
        default=0,
        help_text='Porcentaje de completitud (0-100)'
    )
    
    tags = JSONFieldCompatible(
        'Etiquetas',
        default=list,
        blank=True,
        help_text='Lista de etiquetas para clasificación'
    )
    
    attachments = JSONFieldCompatible(
        'Adjuntos',
        default=list,
        blank=True,
        help_text='Referencias a documentos adjuntos'
    )
    
    metadata = JSONFieldCompatible(
        'Metadata',
        default=dict,
        blank=True,
        help_text='Datos adicionales personalizados'
    )
    
    is_recurring = models.BooleanField('Es Recurrente', default=False)
    recurrence_rule = models.CharField(
        'Regla de Recurrencia',
        max_length=255,
        blank=True,
        help_text='Regla RRULE para tareas recurrentes'
    )
    
    parent_task = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Tarea Padre',
        related_name='subtasks'
    )
    
    reminder_sent = models.BooleanField('Recordatorio Enviado', default=False)
    
    created_at = models.DateTimeField('Fecha Creación', auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField('Fecha Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Tarea'
        verbose_name_plural = 'Tareas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['due_date', 'status']),
            models.Index(fields=['priority', 'status']),
            models.Index(fields=['category', 'status']),
            models.Index(fields=['content_type', 'object_id']),
        ]
    
    def __str__(self):
        return self.title
    
    def is_overdue(self):
        """Verifica si la tarea está vencida"""
        if not self.due_date or self.status in ['completed', 'cancelled']:
            return False
        return timezone.now() > self.due_date
    
    def is_due_soon(self, hours=24):
        """Verifica si la tarea vence pronto"""
        if not self.due_date or self.status in ['completed', 'cancelled']:
            return False
        time_until_due = self.due_date - timezone.now()
        return timedelta(0) < time_until_due <= timedelta(hours=hours)
    
    def complete(self):
        """Marca la tarea como completada"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.progress = 100
        self.save()
    
    def cancel(self):
        """Cancela la tarea"""
        self.status = 'cancelled'
        self.save()
    
    def assign_to(self, user):
        """Asigna la tarea a un usuario"""
        self.assigned_to = user
        if self.status == 'pending':
            self.status = 'in_progress'
        self.save()
    
    def get_completion_percentage(self):
        """Retorna el porcentaje de completitud"""
        return self.progress
    
    def has_subtasks(self):
        """Verifica si tiene subtareas"""
        return self.subtasks.exists()
    
    def get_subtasks_count(self):
        """Retorna el número de subtareas"""
        return self.subtasks.count()
    
    def get_completed_subtasks_count(self):
        """Retorna el número de subtareas completadas"""
        return self.subtasks.filter(status='completed').count()
    
    def get_checklist_items_count(self):
        """Retorna el número total de items del checklist"""
        return self.checklist_items.count()
    
    def get_completed_checklist_items_count(self):
        """Retorna el número de items completados del checklist"""
        return self.checklist_items.filter(is_completed=True).count()
    
    def get_checklist_progress(self):
        """Retorna el porcentaje de progreso del checklist"""
        total = self.get_checklist_items_count()
        if total == 0:
            return 0
        completed = self.get_completed_checklist_items_count()
        return int((completed / total) * 100)


class TaskComment(TenantModel):
    """
    Comentarios en tareas
    Permite comunicación y seguimiento en las tareas
    """
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        verbose_name='Tarea',
        related_name='comments'
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name='Organización',
        related_name='task_comments'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Usuario',
        related_name='task_comments'
    )
    
    comment = models.TextField('Comentario')
    
    parent_comment = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Comentario Padre',
        related_name='replies'
    )
    
    attachments = JSONFieldCompatible(
        'Adjuntos',
        default=list,
        blank=True
    )
    
    is_internal = models.BooleanField(
        'Es Interno',
        default=False,
        help_text='Comentario solo visible para el equipo'
    )
    
    created_at = models.DateTimeField('Fecha Creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Comentario de Tarea'
        verbose_name_plural = 'Comentarios de Tareas'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['task', 'created_at']),
            models.Index(fields=['organization', 'created_at']),
        ]
    
    def __str__(self):
        return f"Comentario en {self.task.title} por {self.user}"


class TaskActivity(TenantModel):
    """
    Registro de actividades/cambios en tareas
    Tracking automático de cambios
    """
    
    ACTION_CHOICES = [
        ('created', 'Creada'),
        ('updated', 'Actualizada'),
        ('assigned', 'Asignada'),
        ('status_changed', 'Estado Cambiado'),
        ('priority_changed', 'Prioridad Cambiada'),
        ('completed', 'Completada'),
        ('cancelled', 'Cancelada'),
        ('commented', 'Comentada'),
        ('attachment_added', 'Adjunto Agregado'),
        ('due_date_changed', 'Fecha Límite Cambiada'),
    ]
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        verbose_name='Tarea',
        related_name='activities'
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name='Organización',
        related_name='task_activities'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Usuario',
        related_name='task_activities'
    )
    
    action = models.CharField(
        'Acción',
        max_length=50,
        choices=ACTION_CHOICES,
        db_index=True
    )
    
    description = models.TextField('Descripción', blank=True)
    
    old_value = JSONFieldCompatible('Valor Anterior', default=dict, blank=True)
    new_value = JSONFieldCompatible('Valor Nuevo', default=dict, blank=True)
    
    ip_address = models.GenericIPAddressField('IP Address', null=True, blank=True)
    
    created_at = models.DateTimeField('Fecha', auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = 'Actividad de Tarea'
        verbose_name_plural = 'Actividades de Tareas'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['task', 'created_at']),
            models.Index(fields=['organization', 'action']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.action} - {self.task.title}"


class TaskChecklist(TenantModel):
    """
    Checklist dentro de una tarea
    Lista de verificación con ítems completables
    """
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        verbose_name='Tarea',
        related_name='checklists'
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name='Organización',
        related_name='task_checklists'
    )
    
    title = models.CharField('Título', max_length=255)
    
    items = JSONFieldCompatible(
        'Items',
        default=list,
        help_text='Lista de items del checklist con estado'
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Creado por',
        related_name='created_checklists'
    )
    
    created_at = models.DateTimeField('Fecha Creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Checklist de Tarea'
        verbose_name_plural = 'Checklists de Tareas'
        ordering = ['created_at']
        indexes = [
            models.Index(fields=['task', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.task.title}"
    
    def get_completion_percentage(self):
        """Calcula el porcentaje de completitud del checklist"""
        if not self.items:
            return 0
        
        total = len(self.items)
        completed = sum(1 for item in self.items if item.get('completed', False))
        
        return int((completed / total) * 100) if total > 0 else 0
    
    def is_complete(self):
        """Verifica si todos los items están completados"""
        return self.get_completion_percentage() == 100


class TaskReminder(TenantModel):
    """
    Recordatorios para tareas
    Permite programar notificaciones antes de la fecha límite
    """
    
    TYPE_CHOICES = [
        ('email', 'Email'),
        ('push', 'Notificación Push'),
        ('sms', 'SMS'),
        ('whatsapp', 'WhatsApp'),
    ]
    
    task = models.ForeignKey(
        Task,
        on_delete=models.CASCADE,
        verbose_name='Tarea',
        related_name='reminders'
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name='Organización',
        related_name='task_reminders'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuario',
        related_name='task_reminders'
    )
    
    reminder_type = models.CharField(
        'Tipo',
        max_length=20,
        choices=TYPE_CHOICES,
        default='email'
    )
    
    remind_at = models.DateTimeField(
        'Recordar en',
        db_index=True,
        help_text='Fecha y hora del recordatorio'
    )
    
    message = models.TextField('Mensaje', blank=True)
    
    is_sent = models.BooleanField('Enviado', default=False, db_index=True)
    sent_at = models.DateTimeField('Enviado en', null=True, blank=True)
    
    created_at = models.DateTimeField('Fecha Creación', auto_now_add=True)
    
    class Meta:
        verbose_name = 'Recordatorio de Tarea'
        verbose_name_plural = 'Recordatorios de Tareas'
        ordering = ['remind_at']
        indexes = [
            models.Index(fields=['remind_at', 'is_sent']),
            models.Index(fields=['task', 'user']),
            models.Index(fields=['organization', 'remind_at']),
        ]
    
    def __str__(self):
        return f"Recordatorio: {self.task.title} - {self.remind_at}"
    
    def mark_as_sent(self):
        """Marca el recordatorio como enviado"""
        self.is_sent = True
        self.sent_at = timezone.now()
        self.save()
