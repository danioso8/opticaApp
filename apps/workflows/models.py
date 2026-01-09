"""
Modelos para el sistema de workflows
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


class WorkflowDefinition(TenantModel):
    """
    Definición de un workflow
    Template reutilizable que define estados, transiciones y reglas
    """
    
    name = models.CharField('Nombre', max_length=255)
    slug = models.SlugField('Slug', max_length=255)
    description = models.TextField('Descripción', blank=True)
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name='Organización',
        related_name='workflow_definitions'
    )
    
    # Define a qué tipo de objeto se aplica este workflow
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name='Tipo de Contenido',
        help_text='Tipo de objeto al que se aplica este workflow'
    )
    
    initial_state = models.CharField(
        'Estado Inicial',
        max_length=100,
        help_text='Estado inicial cuando se crea una instancia'
    )
    
    states = JSONFieldCompatible(
        'Estados',
        default=list,
        help_text='Lista de estados posibles: [{"key": "draft", "name": "Borrador", "color": "#ccc"}]'
    )
    
    final_states = JSONFieldCompatible(
        'Estados Finales',
        default=list,
        help_text='Lista de estados finales (completados/cancelados)'
    )
    
    is_active = models.BooleanField('Activo', default=True)
    
    auto_start = models.BooleanField(
        'Inicio Automático',
        default=False,
        help_text='Iniciar workflow automáticamente al crear el objeto'
    )
    
    require_approval = models.BooleanField(
        'Requiere Aprobación',
        default=False,
        help_text='Workflow requiere aprobaciones en transiciones'
    )
    
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Creado por',
        related_name='created_workflows'
    )
    
    created_at = models.DateTimeField('Fecha Creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Definición de Workflow'
        verbose_name_plural = 'Definiciones de Workflows'
        ordering = ['name']
        unique_together = [['organization', 'slug']]
        indexes = [
            models.Index(fields=['organization', 'is_active']),
            models.Index(fields=['content_type', 'is_active']),
        ]
    
    def __str__(self):
        return self.name
    
    def get_state_info(self, state_key):
        """Obtiene información de un estado específico"""
        for state in self.states:
            if state.get('key') == state_key:
                return state
        return None
    
    def is_final_state(self, state_key):
        """Verifica si un estado es final"""
        return state_key in self.final_states


class WorkflowTransition(TenantModel):
    """
    Transición entre estados en un workflow
    Define las reglas para moverse de un estado a otro
    """
    
    workflow = models.ForeignKey(
        WorkflowDefinition,
        on_delete=models.CASCADE,
        verbose_name='Workflow',
        related_name='transitions'
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name='Organización',
        related_name='workflow_transitions'
    )
    
    name = models.CharField('Nombre', max_length=255)
    
    from_state = models.CharField(
        'Estado Origen',
        max_length=100,
        help_text='Estado desde el cual se puede hacer la transición'
    )
    
    to_state = models.CharField(
        'Estado Destino',
        max_length=100,
        help_text='Estado al que se transiciona'
    )
    
    conditions = JSONFieldCompatible(
        'Condiciones',
        default=dict,
        blank=True,
        help_text='Condiciones que deben cumplirse para la transición'
    )
    
    required_permission = models.CharField(
        'Permiso Requerido',
        max_length=255,
        blank=True,
        help_text='Permiso necesario para ejecutar esta transición'
    )
    
    require_approval = models.BooleanField(
        'Requiere Aprobación',
        default=False,
        help_text='Esta transición requiere aprobación'
    )
    
    approval_roles = JSONFieldCompatible(
        'Roles Aprobadores',
        default=list,
        blank=True,
        help_text='Roles que pueden aprobar esta transición'
    )
    
    order = models.IntegerField(
        'Orden',
        default=0,
        help_text='Orden de presentación'
    )
    
    is_active = models.BooleanField('Activa', default=True)
    
    created_at = models.DateTimeField('Fecha Creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Transición de Workflow'
        verbose_name_plural = 'Transiciones de Workflows'
        ordering = ['workflow', 'order', 'name']
        indexes = [
            models.Index(fields=['workflow', 'from_state']),
            models.Index(fields=['organization', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.workflow.name}: {self.from_state} → {self.to_state}"


class WorkflowAction(TenantModel):
    """
    Acciones automáticas que se ejecutan en transiciones
    """
    
    ACTION_TYPE_CHOICES = [
        ('send_notification', 'Enviar Notificación'),
        ('send_email', 'Enviar Email'),
        ('create_task', 'Crear Tarea'),
        ('update_field', 'Actualizar Campo'),
        ('call_webhook', 'Llamar Webhook'),
        ('execute_script', 'Ejecutar Script'),
        ('assign_user', 'Asignar Usuario'),
    ]
    
    TRIGGER_CHOICES = [
        ('on_enter', 'Al Entrar al Estado'),
        ('on_exit', 'Al Salir del Estado'),
        ('on_transition', 'En la Transición'),
    ]
    
    workflow = models.ForeignKey(
        WorkflowDefinition,
        on_delete=models.CASCADE,
        verbose_name='Workflow',
        related_name='actions'
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name='Organización',
        related_name='workflow_actions'
    )
    
    name = models.CharField('Nombre', max_length=255)
    
    transition = models.ForeignKey(
        WorkflowTransition,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Transición',
        related_name='actions',
        help_text='Transición que dispara esta acción (opcional)'
    )
    
    state = models.CharField(
        'Estado',
        max_length=100,
        blank=True,
        help_text='Estado que dispara esta acción (alternativa a transición)'
    )
    
    action_type = models.CharField(
        'Tipo de Acción',
        max_length=50,
        choices=ACTION_TYPE_CHOICES
    )
    
    trigger = models.CharField(
        'Disparador',
        max_length=20,
        choices=TRIGGER_CHOICES,
        default='on_transition'
    )
    
    parameters = JSONFieldCompatible(
        'Parámetros',
        default=dict,
        help_text='Parámetros específicos de la acción'
    )
    
    order = models.IntegerField('Orden de Ejecución', default=0)
    
    is_active = models.BooleanField('Activa', default=True)
    
    created_at = models.DateTimeField('Fecha Creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Acción de Workflow'
        verbose_name_plural = 'Acciones de Workflows'
        ordering = ['workflow', 'order']
        indexes = [
            models.Index(fields=['workflow', 'is_active']),
            models.Index(fields=['transition', 'trigger']),
        ]
    
    def __str__(self):
        return f"{self.workflow.name}: {self.name}"


class WorkflowInstance(TenantModel):
    """
    Instancia activa de un workflow
    Representa la ejecución de un workflow sobre un objeto específico
    """
    
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
        ('suspended', 'Suspendido'),
        ('error', 'Error'),
    ]
    
    workflow = models.ForeignKey(
        WorkflowDefinition,
        on_delete=models.CASCADE,
        verbose_name='Workflow',
        related_name='instances'
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name='Organización',
        related_name='workflow_instances'
    )
    
    # Objeto al que se aplica el workflow
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.CASCADE,
        verbose_name='Tipo de Contenido'
    )
    object_id = models.PositiveIntegerField('ID Objeto')
    content_object = GenericForeignKey('content_type', 'object_id')
    
    current_state = models.CharField(
        'Estado Actual',
        max_length=100,
        db_index=True
    )
    
    status = models.CharField(
        'Estado',
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True
    )
    
    data = JSONFieldCompatible(
        'Datos',
        default=dict,
        blank=True,
        help_text='Datos adicionales del workflow'
    )
    
    started_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Iniciado por',
        related_name='started_workflows'
    )
    
    started_at = models.DateTimeField('Iniciado en', auto_now_add=True)
    completed_at = models.DateTimeField('Completado en', null=True, blank=True)
    
    error_message = models.TextField('Mensaje de Error', blank=True)
    
    class Meta:
        verbose_name = 'Instancia de Workflow'
        verbose_name_plural = 'Instancias de Workflows'
        ordering = ['-started_at']
        indexes = [
            models.Index(fields=['workflow', 'status']),
            models.Index(fields=['organization', 'current_state']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['started_by', 'status']),
        ]
    
    def __str__(self):
        return f"{self.workflow.name} - {self.current_state}"
    
    def is_active(self):
        """Verifica si la instancia está activa"""
        return self.status == 'active'
    
    def is_in_final_state(self):
        """Verifica si está en un estado final"""
        return self.workflow.is_final_state(self.current_state)
    
    def complete(self):
        """Marca la instancia como completada"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()
    
    def cancel(self):
        """Cancela la instancia"""
        self.status = 'cancelled'
        self.completed_at = timezone.now()
        self.save()
    
    def suspend(self):
        """Suspende la instancia"""
        self.status = 'suspended'
        self.save()
    
    def resume(self):
        """Reanuda la instancia"""
        if self.status == 'suspended':
            self.status = 'active'
            self.save()


class WorkflowHistory(TenantModel):
    """
    Historial de transiciones de workflow
    Registra todos los cambios de estado
    """
    
    instance = models.ForeignKey(
        WorkflowInstance,
        on_delete=models.CASCADE,
        verbose_name='Instancia',
        related_name='history'
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name='Organización',
        related_name='workflow_history'
    )
    
    transition = models.ForeignKey(
        WorkflowTransition,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Transición'
    )
    
    from_state = models.CharField('Estado Anterior', max_length=100)
    to_state = models.CharField('Estado Nuevo', max_length=100)
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Usuario',
        related_name='workflow_transitions_made'
    )
    
    comment = models.TextField('Comentario', blank=True)
    
    metadata = JSONFieldCompatible(
        'Metadata',
        default=dict,
        blank=True,
        help_text='Datos adicionales de la transición'
    )
    
    ip_address = models.GenericIPAddressField('IP Address', null=True, blank=True)
    
    created_at = models.DateTimeField('Fecha', auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = 'Historial de Workflow'
        verbose_name_plural = 'Historiales de Workflows'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['instance', 'created_at']),
            models.Index(fields=['organization', 'created_at']),
            models.Index(fields=['user', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.instance.workflow.name}: {self.from_state} → {self.to_state}"


class WorkflowApproval(TenantModel):
    """
    Aprobaciones requeridas en transiciones de workflow
    """
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('approved', 'Aprobada'),
        ('rejected', 'Rechazada'),
    ]
    
    instance = models.ForeignKey(
        WorkflowInstance,
        on_delete=models.CASCADE,
        verbose_name='Instancia',
        related_name='approvals'
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name='Organización',
        related_name='workflow_approvals'
    )
    
    transition = models.ForeignKey(
        WorkflowTransition,
        on_delete=models.CASCADE,
        verbose_name='Transición'
    )
    
    requested_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Solicitado por',
        related_name='workflow_approval_requests'
    )
    
    approver = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Aprobador',
        related_name='workflow_approvals_assigned'
    )
    
    status = models.CharField(
        'Estado',
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        db_index=True
    )
    
    comment = models.TextField('Comentario', blank=True)
    
    requested_at = models.DateTimeField('Solicitado en', auto_now_add=True)
    responded_at = models.DateTimeField('Respondido en', null=True, blank=True)
    
    class Meta:
        verbose_name = 'Aprobación de Workflow'
        verbose_name_plural = 'Aprobaciones de Workflows'
        ordering = ['-requested_at']
        indexes = [
            models.Index(fields=['instance', 'status']),
            models.Index(fields=['approver', 'status']),
            models.Index(fields=['organization', 'requested_at']),
        ]
    
    def __str__(self):
        return f"Aprobación: {self.transition} - {self.status}"
    
    def approve(self, user, comment=''):
        """Aprueba la transición"""
        self.status = 'approved'
        self.approver = user
        self.comment = comment
        self.responded_at = timezone.now()
        self.save()
    
    def reject(self, user, comment=''):
        """Rechaza la transición"""
        self.status = 'rejected'
        self.approver = user
        self.comment = comment
        self.responded_at = timezone.now()
        self.save()
