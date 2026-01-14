"""
Modelos para el sistema de API REST
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from apps.organizations.base_models import TenantModel
import secrets
import hashlib
import json

User = get_user_model()


class JSONFieldCompatible(models.TextField):
    """
    Campo compatible con SQLite y PostgreSQL para almacenar JSON
    Usa JSONField en PostgreSQL y TextField con serialización en SQLite
    """
    
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


class APIKey(TenantModel):
    """
    API Keys para autenticación de aplicaciones externas
    Permite a terceros acceder al API de forma segura
    """
    
    STATUS_CHOICES = [
        ('active', 'Activa'),
        ('inactive', 'Inactiva'),
        ('revoked', 'Revocada'),
        ('expired', 'Expirada'),
    ]
    
    SCOPE_CHOICES = [
        ('read', 'Solo Lectura'),
        ('write', 'Lectura y Escritura'),
        ('admin', 'Administrador'),
    ]
    
    name = models.CharField('Nombre', max_length=255, help_text='Nombre descriptivo de la API Key')
    key = models.CharField('Key', max_length=64, unique=True, db_index=True)
    key_prefix = models.CharField('Prefijo', max_length=8, db_index=True)
    key_hash = models.CharField('Hash', max_length=64, db_index=True)
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Usuario',
        related_name='api_keys',
        help_text='Usuario propietario de esta API Key'
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name='Organización',
        related_name='api_keys'
    )
    
    scope = models.CharField(
        'Alcance',
        max_length=20,
        choices=SCOPE_CHOICES,
        default='read',
        help_text='Nivel de permisos de la API Key'
    )
    
    status = models.CharField(
        'Estado',
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True
    )
    
    allowed_ips = JSONFieldCompatible(
        'IPs Permitidas',
        default=list,
        blank=True,
        help_text='Lista de IPs permitidas (vacío = todas)'
    )
    
    allowed_endpoints = JSONFieldCompatible(
        'Endpoints Permitidos',
        default=list,
        blank=True,
        help_text='Lista de endpoints permitidos (vacío = todos)'
    )
    
    rate_limit = models.IntegerField(
        'Límite de Tasa',
        default=1000,
        help_text='Requests por hora permitidos'
    )
    
    expires_at = models.DateTimeField(
        'Expira en',
        null=True,
        blank=True,
        help_text='Fecha de expiración (null = sin expiración)'
    )
    
    last_used_at = models.DateTimeField('Último Uso', null=True, blank=True)
    last_used_ip = models.GenericIPAddressField('Última IP', null=True, blank=True)
    
    total_requests = models.IntegerField('Total Requests', default=0)
    
    notes = models.TextField('Notas', blank=True)
    
    created_at = models.DateTimeField('Fecha Creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'API Key'
        verbose_name_plural = 'API Keys'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['key_prefix', 'key_hash']),
            models.Index(fields=['expires_at']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.key_prefix}...)"
    
    @classmethod
    def generate_key(cls):
        """Genera una nueva API key única"""
        key = secrets.token_urlsafe(48)  # 64 caracteres
        return key
    
    @classmethod
    def hash_key(cls, key):
        """Genera hash SHA256 de la key"""
        return hashlib.sha256(key.encode()).hexdigest()
    
    def save(self, *args, **kwargs):
        """Override save to generate key and hash"""
        if not self.key:
            self.key = self.generate_key()
            self.key_prefix = self.key[:8]
            self.key_hash = self.hash_key(self.key)
        
        # Check expiration
        if self.expires_at and self.expires_at < timezone.now():
            self.status = 'expired'
        
        super().save(*args, **kwargs)
    
    def is_valid(self):
        """Verifica si la API Key es válida"""
        if self.status != 'active':
            return False
        
        if self.expires_at and self.expires_at < timezone.now():
            self.status = 'expired'
            self.save()
            return False
        
        return True
    
    def can_access_endpoint(self, endpoint):
        """Verifica si puede acceder a un endpoint específico"""
        if not self.allowed_endpoints:
            return True
        return endpoint in self.allowed_endpoints
    
    def can_access_from_ip(self, ip_address):
        """Verifica si puede acceder desde una IP específica"""
        if not self.allowed_ips:
            return True
        return ip_address in self.allowed_ips
    
    def record_usage(self, ip_address=None):
        """Registra el uso de la API Key"""
        self.last_used_at = timezone.now()
        if ip_address:
            self.last_used_ip = ip_address
        self.total_requests += 1
        self.save(update_fields=['last_used_at', 'last_used_ip', 'total_requests'])


class APILog(TenantModel):
    """
    Log de todas las peticiones API
    Permite auditoría y análisis de uso
    """
    
    METHOD_CHOICES = [
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('PATCH', 'PATCH'),
        ('DELETE', 'DELETE'),
        ('OPTIONS', 'OPTIONS'),
        ('HEAD', 'HEAD'),
    ]
    
    api_key = models.ForeignKey(
        APIKey,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='API Key',
        related_name='logs'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Usuario',
        related_name='api_logs'
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name='Organización',
        related_name='api_logs'
    )
    
    method = models.CharField('Método HTTP', max_length=10, choices=METHOD_CHOICES, db_index=True)
    endpoint = models.CharField('Endpoint', max_length=500, db_index=True)
    full_path = models.TextField('Path Completo')
    
    request_headers = JSONFieldCompatible('Headers Request', default=dict, blank=True)
    request_body = JSONFieldCompatible('Body Request', default=dict, blank=True)
    request_params = JSONFieldCompatible('Query Params', default=dict, blank=True)
    
    response_status = models.IntegerField('Status Code', db_index=True)
    response_body = JSONFieldCompatible('Body Response', default=dict, blank=True)
    response_time = models.FloatField('Tiempo Respuesta (ms)', help_text='Tiempo en milisegundos')
    
    ip_address = models.GenericIPAddressField('IP Address', db_index=True)
    user_agent = models.TextField('User Agent', blank=True)
    
    error_message = models.TextField('Mensaje Error', blank=True)
    stack_trace = models.TextField('Stack Trace', blank=True)
    
    created_at = models.DateTimeField('Fecha', auto_now_add=True, db_index=True)
    
    class Meta:
        verbose_name = 'Log API'
        verbose_name_plural = 'Logs API'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'created_at']),
            models.Index(fields=['api_key', 'created_at']),
            models.Index(fields=['user', 'created_at']),
            models.Index(fields=['endpoint', 'method']),
            models.Index(fields=['response_status', 'created_at']),
            models.Index(fields=['ip_address', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.method} {self.endpoint} - {self.response_status}"
    
    def is_error(self):
        """Verifica si la petición resultó en error"""
        return self.response_status >= 400
    
    def is_success(self):
        """Verifica si la petición fue exitosa"""
        return 200 <= self.response_status < 300


class RateLimitRecord(TenantModel):
    """
    Registro de rate limiting por API Key o IP
    Permite control de abuso y throttling
    """
    
    TYPE_CHOICES = [
        ('api_key', 'API Key'),
        ('ip_address', 'IP Address'),
        ('user', 'Usuario'),
    ]
    
    limit_type = models.CharField('Tipo', max_length=20, choices=TYPE_CHOICES, db_index=True)
    identifier = models.CharField('Identificador', max_length=255, db_index=True)
    
    api_key = models.ForeignKey(
        APIKey,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='API Key',
        related_name='rate_limits'
    )
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='Usuario',
        related_name='rate_limits'
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        null=True,  # Permitir NULL para rate limits públicos (sin organización)
        blank=True,
        verbose_name='Organización',
        related_name='rate_limits'
    )
    
    endpoint = models.CharField('Endpoint', max_length=500, db_index=True)
    
    request_count = models.IntegerField('Contador Requests', default=0)
    window_start = models.DateTimeField('Inicio Ventana', db_index=True)
    window_end = models.DateTimeField('Fin Ventana', db_index=True)
    
    limit = models.IntegerField('Límite', help_text='Número máximo de requests en la ventana')
    
    is_blocked = models.BooleanField('Bloqueado', default=False, db_index=True)
    blocked_until = models.DateTimeField('Bloqueado Hasta', null=True, blank=True)
    
    created_at = models.DateTimeField('Fecha Creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Registro Rate Limit'
        verbose_name_plural = 'Registros Rate Limit'
        ordering = ['-created_at']
        unique_together = [['limit_type', 'identifier', 'endpoint', 'window_start']]
        indexes = [
            models.Index(fields=['organization', 'window_end']),
            models.Index(fields=['identifier', 'endpoint', 'window_end']),
            models.Index(fields=['is_blocked', 'blocked_until']),
        ]
    
    def __str__(self):
        return f"{self.limit_type}: {self.identifier} - {self.request_count}/{self.limit}"
    
    def increment(self):
        """Incrementa el contador de requests"""
        self.request_count += 1
        
        if self.request_count > self.limit:
            self.is_blocked = True
            self.blocked_until = self.window_end
        
        self.save()
    
    def is_limit_exceeded(self):
        """Verifica si se excedió el límite"""
        return self.request_count >= self.limit
    
    def can_make_request(self):
        """Verifica si puede hacer una petición"""
        now = timezone.now()
        
        # Si la ventana expiró, reiniciar
        if now > self.window_end:
            return True
        
        # Si está bloqueado y el bloqueo no expiró
        if self.is_blocked and self.blocked_until and now < self.blocked_until:
            return False
        
        return not self.is_limit_exceeded()


class APIWebhook(TenantModel):
    """
    Webhooks para notificaciones de eventos
    Permite integración con sistemas externos
    """
    
    STATUS_CHOICES = [
        ('active', 'Activo'),
        ('inactive', 'Inactivo'),
        ('failed', 'Fallido'),
    ]
    
    EVENT_CHOICES = [
        ('patient.created', 'Paciente Creado'),
        ('patient.updated', 'Paciente Actualizado'),
        ('patient.deleted', 'Paciente Eliminado'),
        ('appointment.created', 'Cita Creada'),
        ('appointment.updated', 'Cita Actualizada'),
        ('appointment.cancelled', 'Cita Cancelada'),
        ('invoice.created', 'Factura Creada'),
        ('invoice.paid', 'Factura Pagada'),
        ('order.created', 'Orden Creada'),
        ('order.completed', 'Orden Completada'),
        ('document.uploaded', 'Documento Subido'),
        ('report.generated', 'Reporte Generado'),
        ('*', 'Todos los Eventos'),
    ]
    
    name = models.CharField('Nombre', max_length=255)
    url = models.URLField('URL', max_length=500, help_text='URL donde se enviarán los webhooks')
    
    api_key = models.ForeignKey(
        APIKey,
        on_delete=models.CASCADE,
        verbose_name='API Key',
        related_name='webhooks',
        help_text='API Key asociada a este webhook'
    )
    
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        verbose_name='Organización',
        related_name='webhooks'
    )
    
    events = JSONFieldCompatible(
        'Eventos',
        default=list,
        help_text='Lista de eventos a los que está suscrito'
    )
    
    status = models.CharField(
        'Estado',
        max_length=20,
        choices=STATUS_CHOICES,
        default='active',
        db_index=True
    )
    
    headers = JSONFieldCompatible(
        'Headers Personalizados',
        default=dict,
        blank=True,
        help_text='Headers HTTP personalizados a incluir'
    )
    
    secret = models.CharField(
        'Secret',
        max_length=64,
        blank=True,
        help_text='Secret para firmar payloads (HMAC)'
    )
    
    retry_on_failure = models.BooleanField('Reintentar en Fallo', default=True)
    max_retries = models.IntegerField('Máximo Reintentos', default=3)
    
    last_triggered_at = models.DateTimeField('Último Trigger', null=True, blank=True)
    last_success_at = models.DateTimeField('Último Éxito', null=True, blank=True)
    last_failure_at = models.DateTimeField('Último Fallo', null=True, blank=True)
    
    total_triggers = models.IntegerField('Total Triggers', default=0)
    total_successes = models.IntegerField('Total Éxitos', default=0)
    total_failures = models.IntegerField('Total Fallos', default=0)
    
    is_active = models.BooleanField('Activo', default=True)
    
    created_at = models.DateTimeField('Fecha Creación', auto_now_add=True)
    updated_at = models.DateTimeField('Fecha Actualización', auto_now=True)
    
    class Meta:
        verbose_name = 'Webhook API'
        verbose_name_plural = 'Webhooks API'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'status']),
            models.Index(fields=['api_key', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.name} - {self.url}"
    
    def save(self, *args, **kwargs):
        """Generate secret if not provided"""
        if not self.secret:
            self.secret = secrets.token_urlsafe(32)
        super().save(*args, **kwargs)
    
    def is_subscribed_to(self, event):
        """Verifica si está suscrito a un evento específico"""
        if not self.events:
            return False
        return '*' in self.events or event in self.events
    
    def record_trigger(self, success=True):
        """Registra un trigger del webhook"""
        self.last_triggered_at = timezone.now()
        self.total_triggers += 1
        
        if success:
            self.last_success_at = timezone.now()
            self.total_successes += 1
            if self.status == 'failed':
                self.status = 'active'
        else:
            self.last_failure_at = timezone.now()
            self.total_failures += 1
            
            # Si falla muchas veces, marcar como failed
            if self.total_failures > self.max_retries * 3:
                self.status = 'failed'
        
        self.save()
