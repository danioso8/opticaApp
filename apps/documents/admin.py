"""
Admin para el sistema de documentos.
"""
from django.contrib import admin
from django.utils.html import format_html
from django.db.models import Sum

from .models import Folder, Document, DocumentShare, DocumentComment, DocumentActivity


@admin.register(Folder)
class FolderAdmin(admin.ModelAdmin):
    """Admin para carpetas."""
    
    list_display = [
        'name', 'organization', 'parent', 'created_by',
        'documents_count', 'created_at'
    ]
    
    list_filter = [
        'organization',
        'is_system',
        'created_at'
    ]
    
    search_fields = [
        'name',
        'description'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('name', 'description', 'organization', 'parent')
        }),
        ('Apariencia', {
            'fields': ('color', 'icon')
        }),
        ('Permisos', {
            'fields': ('created_by', 'is_system')
        }),
    )
    
    readonly_fields = ['created_at', 'updated_at']
    
    def documents_count(self, obj):
        """Muestra el número de documentos."""
        return obj.documents.count()
    documents_count.short_description = 'Documentos'


@admin.register(Document)
class DocumentAdmin(admin.ModelAdmin):
    """Admin para documentos."""
    
    list_display = [
        'title', 'document_type_badge', 'organization', 'folder',
        'file_size_display', 'uploaded_by', 'is_public', 'created_at'
    ]
    
    list_filter = [
        'document_type',
        'is_public',
        'is_protected',
        'organization',
        'created_at'
    ]
    
    search_fields = [
        'title',
        'description',
        'file_name'
    ]
    
    fieldsets = (
        ('Información Básica', {
            'fields': ('title', 'description', 'organization', 'folder')
        }),
        ('Archivo', {
            'fields': ('file', 'document_type', 'file_name', 'file_size', 
                      'mime_type', 'file_hash')
        }),
        ('Relación', {
            'fields': ('content_type', 'object_id'),
            'classes': ('collapse',)
        }),
        ('Permisos', {
            'fields': ('uploaded_by', 'is_public', 'is_protected')
        }),
        ('Versiones', {
            'fields': ('version', 'parent_document'),
            'classes': ('collapse',)
        }),
        ('Metadatos', {
            'fields': ('tags', 'metadata', 'expires_at'),
            'classes': ('collapse',)
        }),
        ('Estadísticas', {
            'fields': ('view_count', 'download_count')
        }),
    )
    
    readonly_fields = [
        'document_type', 'file_name', 'file_size', 'mime_type',
        'file_hash', 'view_count', 'download_count', 'created_at',
        'updated_at'
    ]
    
    date_hierarchy = 'created_at'
    
    actions = ['make_public', 'make_private', 'protect_documents']
    
    def document_type_badge(self, obj):
        """Muestra badge de tipo."""
        colors = {
            'image': 'success',
            'pdf': 'danger',
            'word': 'primary',
            'excel': 'success',
            'video': 'warning',
            'audio': 'info',
            'other': 'secondary'
        }
        color = colors.get(obj.document_type, 'secondary')
        return format_html(
            '<span class="badge badge-{}">{}</span>',
            color,
            obj.get_document_type_display()
        )
    document_type_badge.short_description = 'Tipo'
    
    def file_size_display(self, obj):
        """Muestra el tamaño del archivo."""
        return obj.get_file_size_display()
    file_size_display.short_description = 'Tamaño'
    
    def make_public(self, request, queryset):
        count = queryset.update(is_public=True)
        self.message_user(request, f"{count} documentos marcados como públicos.")
    make_public.short_description = "Hacer públicos"
    
    def make_private(self, request, queryset):
        count = queryset.update(is_public=False)
        self.message_user(request, f"{count} documentos marcados como privados.")
    make_private.short_description = "Hacer privados"
    
    def protect_documents(self, request, queryset):
        count = queryset.update(is_protected=True)
        self.message_user(request, f"{count} documentos protegidos.")
    protect_documents.short_description = "Proteger documentos"


@admin.register(DocumentShare)
class DocumentShareAdmin(admin.ModelAdmin):
    """Admin para documentos compartidos."""
    
    list_display = [
        'document', 'shared_by', 'recipient_display',
        'can_download', 'access_count', 'expires_at', 'created_at'
    ]
    
    list_filter = [
        'can_download',
        'can_edit',
        'created_at',
        'expires_at'
    ]
    
    search_fields = [
        'document__title',
        'shared_by__email',
        'shared_with__email',
        'shared_with_email',
        'public_link'
    ]
    
    readonly_fields = [
        'document', 'shared_by', 'public_link', 'access_count',
        'last_accessed_at', 'created_at'
    ]
    
    def has_add_permission(self, request):
        return False
    
    def recipient_display(self, obj):
        """Muestra el destinatario."""
        if obj.shared_with:
            return obj.shared_with.email
        elif obj.shared_with_email:
            return obj.shared_with_email
        elif obj.public_link:
            return f"Enlace: {obj.public_link}"
        return '-'
    recipient_display.short_description = 'Compartido con'


@admin.register(DocumentComment)
class DocumentCommentAdmin(admin.ModelAdmin):
    """Admin para comentarios."""
    
    list_display = [
        'document', 'user', 'comment_preview', 'created_at'
    ]
    
    list_filter = [
        'created_at'
    ]
    
    search_fields = [
        'document__title',
        'user__email',
        'comment'
    ]
    
    readonly_fields = ['document', 'user', 'created_at', 'updated_at']
    
    def comment_preview(self, obj):
        """Muestra preview del comentario."""
        return obj.comment[:100]
    comment_preview.short_description = 'Comentario'


@admin.register(DocumentActivity)
class DocumentActivityAdmin(admin.ModelAdmin):
    """Admin para actividades."""
    
    list_display = [
        'created_at', 'user', 'action', 'document', 'ip_address'
    ]
    
    list_filter = [
        'action',
        'created_at'
    ]
    
    search_fields = [
        'document__title',
        'user__email',
        'details'
    ]
    
    readonly_fields = [
        'document', 'user', 'action', 'details',
        'ip_address', 'created_at'
    ]
    
    date_hierarchy = 'created_at'
    
    def has_add_permission(self, request):
        return False
    
    def has_change_permission(self, request, obj=None):
        return False
