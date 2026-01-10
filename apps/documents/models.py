"""
Modelos para el sistema de gestión de documentos.
Permite almacenar, organizar y compartir archivos.
"""
from django.db import models
from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.utils import timezone
from django.core.exceptions import ValidationError
import os
import json

User = get_user_model()


class JSONFieldCompatible(models.TextField):
    """Campo compatible con SQLite que almacena JSON como texto."""
    def __init__(self, *args, **kwargs):
        kwargs.setdefault('default', dict)
        super().__init__(*args, **kwargs)

    def from_db_value(self, value, expression, connection):
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return {}

    def to_python(self, value):
        if value is None:
            return {}
        if isinstance(value, dict):
            return value
        try:
            return json.loads(value)
        except (json.JSONDecodeError, TypeError):
            return {}

    def get_prep_value(self, value):
        if value is None:
            return '{}'
        if isinstance(value, str):
            return value
        return json.dumps(value, ensure_ascii=False)

    def value_to_string(self, obj):
        value = self.value_from_object(obj)
        return self.get_prep_value(value)


class Folder(models.Model):
    """
    Carpeta para organizar documentos.
    Estructura jerárquica (carpetas dentro de carpetas).
    """
    
    # Nombre de la carpeta
    name = models.CharField(
        'Nombre',
        max_length=200
    )
    
    # Descripción
    description = models.TextField(
        'Descripción',
        blank=True
    )
    
    # Organización (multi-tenant)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='folders',
        verbose_name='Organización'
    )
    
    # Carpeta padre (para jerarquía)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='subfolders',
        verbose_name='Carpeta padre'
    )
    
    # Creador
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='created_folders',
        verbose_name='Creado por'
    )
    
    # Color para UI
    color = models.CharField(
        'Color',
        max_length=7,
        default='#3B82F6',
        help_text='Color en formato hex (#RRGGBB)'
    )
    
    # Icono
    icon = models.CharField(
        'Ícono',
        max_length=50,
        default='folder',
        help_text='Nombre del ícono'
    )
    
    # Si es carpeta del sistema
    is_system = models.BooleanField(
        'Es del sistema',
        default=False
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        'Fecha de creación',
        default=timezone.now
    )
    
    updated_at = models.DateTimeField(
        'Fecha de actualización',
        auto_now=True
    )
    
    class Meta:
        verbose_name = 'Carpeta'
        verbose_name_plural = 'Carpetas'
        ordering = ['name']
        unique_together = [['organization', 'parent', 'name']]
        indexes = [
            models.Index(fields=['organization', 'parent']),
        ]
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name}/{self.name}"
        return self.name
    
    def get_full_path(self):
        """Retorna la ruta completa de la carpeta."""
        path = [self.name]
        parent = self.parent
        while parent:
            path.insert(0, parent.name)
            parent = parent.parent
        return '/'.join(path)
    
    def get_total_size(self):
        """Calcula el tamaño total de documentos en la carpeta."""
        total = self.documents.aggregate(
            total=models.Sum('file_size')
        )['total'] or 0
        
        # Incluir subcarpetas
        for subfolder in self.subfolders.all():
            total += subfolder.get_total_size()
        
        return total


class Document(models.Model):
    """
    Documento o archivo almacenado.
    """
    
    DOCUMENT_TYPE_CHOICES = [
        ('image', 'Imagen'),
        ('pdf', 'PDF'),
        ('word', 'Word'),
        ('excel', 'Excel'),
        ('video', 'Video'),
        ('audio', 'Audio'),
        ('other', 'Otro'),
    ]
    
    # Título del documento
    title = models.CharField(
        'Título',
        max_length=200
    )
    
    # Descripción
    description = models.TextField(
        'Descripción',
        blank=True
    )
    
    # Organización (multi-tenant)
    organization = models.ForeignKey(
        'organizations.Organization',
        on_delete=models.CASCADE,
        related_name='documents',
        verbose_name='Organización'
    )
    
    # Carpeta
    folder = models.ForeignKey(
        Folder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='documents',
        verbose_name='Carpeta'
    )
    
    # Archivo
    file = models.FileField(
        'Archivo',
        upload_to='documents/%Y/%m/'
    )
    
    # Tipo de documento
    document_type = models.CharField(
        'Tipo',
        max_length=20,
        choices=DOCUMENT_TYPE_CHOICES,
        db_index=True
    )
    
    # Información del archivo
    file_name = models.CharField(
        'Nombre del archivo',
        max_length=255
    )
    
    file_size = models.BigIntegerField(
        'Tamaño (bytes)',
        default=0
    )
    
    mime_type = models.CharField(
        'Tipo MIME',
        max_length=100,
        blank=True
    )
    
    # Hash del archivo (para evitar duplicados)
    file_hash = models.CharField(
        'Hash MD5',
        max_length=32,
        blank=True,
        db_index=True
    )
    
    # Relación con otros objetos (GenericForeignKey)
    content_type = models.ForeignKey(
        ContentType,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Tipo de objeto'
    )
    object_id = models.CharField(
        'ID del objeto',
        max_length=255,
        null=True,
        blank=True
    )
    content_object = GenericForeignKey('content_type', 'object_id')
    
    # Usuario que subió el documento
    uploaded_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='uploaded_documents',
        verbose_name='Subido por'
    )
    
    # Tags
    tags = JSONFieldCompatible(
        'Etiquetas',
        help_text='Lista de etiquetas para búsqueda'
    )
    
    # Metadatos adicionales
    metadata = JSONFieldCompatible(
        'Metadatos',
        help_text='Información adicional del archivo'
    )
    
    # Permisos
    is_public = models.BooleanField(
        'Es público',
        default=False,
        help_text='Visible para todos los usuarios de la org'
    )
    
    is_protected = models.BooleanField(
        'Protegido',
        default=False,
        help_text='No se puede eliminar'
    )
    
    # Versión (para control de versiones)
    version = models.IntegerField(
        'Versión',
        default=1
    )
    
    parent_document = models.ForeignKey(
        'self',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='versions',
        verbose_name='Documento padre'
    )
    
    # Estadísticas
    download_count = models.IntegerField(
        'Descargas',
        default=0
    )
    
    view_count = models.IntegerField(
        'Visualizaciones',
        default=0
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        'Fecha de creación',
        default=timezone.now,
        db_index=True
    )
    
    updated_at = models.DateTimeField(
        'Fecha de actualización',
        auto_now=True
    )
    
    # Expiración
    expires_at = models.DateTimeField(
        'Expira el',
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Documento'
        verbose_name_plural = 'Documentos'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['organization', 'folder', '-created_at']),
            models.Index(fields=['document_type', '-created_at']),
            models.Index(fields=['content_type', 'object_id']),
            models.Index(fields=['file_hash']),
        ]
    
    def __str__(self):
        return self.title
    
    def save(self, *args, **kwargs):
        """Detecta tipo de documento y calcula hash."""
        if self.file:
            # Nombre del archivo
            self.file_name = os.path.basename(self.file.name)
            
            # Tamaño
            self.file_size = self.file.size
            
            # Detectar tipo
            ext = os.path.splitext(self.file_name)[1].lower()
            if ext in ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.svg']:
                self.document_type = 'image'
            elif ext == '.pdf':
                self.document_type = 'pdf'
            elif ext in ['.doc', '.docx']:
                self.document_type = 'word'
            elif ext in ['.xls', '.xlsx', '.csv']:
                self.document_type = 'excel'
            elif ext in ['.mp4', '.avi', '.mov', '.wmv']:
                self.document_type = 'video'
            elif ext in ['.mp3', '.wav', '.ogg']:
                self.document_type = 'audio'
            else:
                self.document_type = 'other'
            
            # TODO: Calcular hash MD5
            # import hashlib
            # self.file_hash = hashlib.md5(self.file.read()).hexdigest()
        
        super().save(*args, **kwargs)
    
    def get_file_size_display(self):
        """Retorna el tamaño del archivo en formato legible."""
        size = self.file_size
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"
    
    def is_expired(self):
        """Verifica si el documento ha expirado."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False


class DocumentShare(models.Model):
    """
    Compartir documento con usuarios o enlaces públicos.
    """
    
    # Documento compartido
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='shares',
        verbose_name='Documento'
    )
    
    # Compartido por
    shared_by = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='documents_shared',
        verbose_name='Compartido por'
    )
    
    # Compartido con (usuario interno)
    shared_with = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='documents_received',
        verbose_name='Compartido con',
        null=True,
        blank=True
    )
    
    # O email externo
    shared_with_email = models.EmailField(
        'Email destinatario',
        blank=True
    )
    
    # O enlace público
    public_link = models.CharField(
        'Enlace público',
        max_length=100,
        unique=True,
        null=True,
        blank=True,
        help_text='Token único para acceso público'
    )
    
    # Permisos
    can_view = models.BooleanField(
        'Puede ver',
        default=True
    )
    
    can_download = models.BooleanField(
        'Puede descargar',
        default=True
    )
    
    can_edit = models.BooleanField(
        'Puede editar',
        default=False
    )
    
    # Mensaje
    message = models.TextField(
        'Mensaje',
        blank=True
    )
    
    # Expiración
    expires_at = models.DateTimeField(
        'Expira el',
        null=True,
        blank=True
    )
    
    # Protección con contraseña
    password = models.CharField(
        'Contraseña',
        max_length=128,
        blank=True,
        help_text='Contraseña para acceder (hash)'
    )
    
    # Estadísticas
    access_count = models.IntegerField(
        'Accesos',
        default=0
    )
    
    last_accessed_at = models.DateTimeField(
        'Último acceso',
        null=True,
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        'Fecha de creación',
        default=timezone.now
    )
    
    class Meta:
        verbose_name = 'Compartir documento'
        verbose_name_plural = 'Documentos compartidos'
        ordering = ['-created_at']
    
    def __str__(self):
        if self.shared_with:
            recipient = self.shared_with.email
        elif self.shared_with_email:
            recipient = self.shared_with_email
        else:
            recipient = 'Enlace público'
        return f"{self.document.title} → {recipient}"
    
    def is_expired(self):
        """Verifica si el compartido ha expirado."""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False
    
    def generate_public_link(self):
        """Genera un token único para enlace público."""
        import uuid
        self.public_link = uuid.uuid4().hex[:20]
        self.save()
        return self.public_link


class DocumentComment(models.Model):
    """
    Comentario en un documento.
    Permite colaboración y feedback.
    """
    
    # Documento
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='comments',
        verbose_name='Documento'
    )
    
    # Usuario que comenta
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='document_comments',
        verbose_name='Usuario'
    )
    
    # Comentario
    comment = models.TextField(
        'Comentario'
    )
    
    # Comentario padre (para respuestas)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies',
        verbose_name='Comentario padre'
    )
    
    # Timestamps
    created_at = models.DateTimeField(
        'Fecha de creación',
        default=timezone.now
    )
    
    updated_at = models.DateTimeField(
        'Fecha de actualización',
        auto_now=True
    )
    
    class Meta:
        verbose_name = 'Comentario'
        verbose_name_plural = 'Comentarios'
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.user.get_full_name()}: {self.comment[:50]}"


class DocumentActivity(models.Model):
    """
    Registro de actividad en documentos.
    Tracking de acciones (ver, descargar, compartir, etc.)
    """
    
    ACTION_CHOICES = [
        ('upload', 'Subido'),
        ('view', 'Visto'),
        ('download', 'Descargado'),
        ('edit', 'Editado'),
        ('delete', 'Eliminado'),
        ('share', 'Compartido'),
        ('comment', 'Comentado'),
    ]
    
    # Documento
    document = models.ForeignKey(
        Document,
        on_delete=models.CASCADE,
        related_name='activities',
        verbose_name='Documento'
    )
    
    # Usuario
    user = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='document_activities',
        verbose_name='Usuario'
    )
    
    # Acción
    action = models.CharField(
        'Acción',
        max_length=20,
        choices=ACTION_CHOICES
    )
    
    # Detalles
    details = models.TextField(
        'Detalles',
        blank=True
    )
    
    # IP
    ip_address = models.GenericIPAddressField(
        'Dirección IP',
        null=True,
        blank=True
    )
    
    # Timestamp
    created_at = models.DateTimeField(
        'Fecha',
        default=timezone.now,
        db_index=True
    )
    
    class Meta:
        verbose_name = 'Actividad de documento'
        verbose_name_plural = 'Actividades de documento'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['document', '-created_at']),
            models.Index(fields=['user', '-created_at']),
        ]
    
    def __str__(self):
        user_name = self.user.get_full_name() if self.user else 'Anónimo'
        return f"{user_name} - {self.get_action_display()} - {self.document.title}"
