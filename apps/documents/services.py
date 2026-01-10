"""
Servicios para el sistema de documentos.
Gestiona subida, descarga y organización de archivos.
"""
from django.db.models import Q, Sum
from django.core.files.uploadedfile import UploadedFile
from django.utils import timezone
from datetime import timedelta
import os

from .models import Folder, Document, DocumentShare, DocumentComment, DocumentActivity


class DocumentService:
    """Servicio para gestionar documentos."""
    
    @staticmethod
    def upload_document(file, organization, user, title=None, folder=None,
                       description='', tags=None, content_object=None,
                       is_public=False):
        """
        Sube un documento.
        
        Args:
            file: Archivo subido (UploadedFile)
            organization: Organization
            user: User que sube
            title: Título del documento
            folder: Carpeta destino
            description: Descripción
            tags: Lista de etiquetas
            content_object: Objeto relacionado
            is_public: Si es público
        
        Returns:
            Document creado
        """
        # Título por defecto = nombre del archivo
        if not title:
            title = os.path.splitext(file.name)[0]
        
        # Crear documento
        document = Document.objects.create(
            title=title,
            description=description,
            organization=organization,
            folder=folder,
            file=file,
            uploaded_by=user,
            tags=tags or [],
            content_object=content_object,
            is_public=is_public
        )
        
        # Registrar actividad
        DocumentService.log_activity(
            document=document,
            user=user,
            action='upload',
            details=f"Subido: {document.file_name}"
        )
        
        return document
    
    @staticmethod
    def get_folder_contents(folder, organization, user=None):
        """
        Obtiene el contenido de una carpeta.
        
        Args:
            folder: Folder (None para raíz)
            organization: Organization
            user: User (para permisos)
        
        Returns:
            Dict con subcarpetas y documentos
        """
        # Subcarpetas
        subfolders = Folder.objects.filter(
            organization=organization,
            parent=folder
        ).order_by('name')
        
        # Documentos
        documents = Document.objects.filter(
            organization=organization,
            folder=folder
        )
        
        # Filtrar por permisos si no es público
        if user:
            documents = documents.filter(
                Q(is_public=True) | Q(uploaded_by=user)
            )
        else:
            documents = documents.filter(is_public=True)
        
        return {
            'subfolders': subfolders,
            'documents': documents.order_by('-created_at')
        }
    
    @staticmethod
    def search_documents(organization, query, user=None, document_type=None,
                        folder=None, tags=None):
        """
        Busca documentos.
        
        Args:
            organization: Organization
            query: Texto de búsqueda
            user: User (para permisos)
            document_type: Tipo de documento
            folder: Carpeta
            tags: Lista de tags
        
        Returns:
            QuerySet de Document
        """
        documents = Document.objects.filter(organization=organization)
        
        # Búsqueda por texto
        if query:
            documents = documents.filter(
                Q(title__icontains=query) |
                Q(description__icontains=query) |
                Q(file_name__icontains=query)
            )
        
        # Filtrar por tipo
        if document_type:
            documents = documents.filter(document_type=document_type)
        
        # Filtrar por carpeta
        if folder:
            documents = documents.filter(folder=folder)
        
        # Filtrar por tags
        if tags:
            # TODO: Implementar búsqueda en JSONField
            pass
        
        # Permisos
        if user:
            documents = documents.filter(
                Q(is_public=True) | Q(uploaded_by=user)
            )
        else:
            documents = documents.filter(is_public=True)
        
        return documents.order_by('-created_at')
    
    @staticmethod
    def share_document(document, user, recipient_user=None, recipient_email=None,
                      can_download=True, can_edit=False, message='',
                      expires_in_days=7, password=None):
        """
        Comparte un documento.
        
        Args:
            document: Document a compartir
            user: User que comparte
            recipient_user: User destinatario
            recipient_email: Email destinatario
            can_download: Si puede descargar
            can_edit: Si puede editar
            message: Mensaje
            expires_in_days: Días hasta expiración
            password: Contraseña de protección
        
        Returns:
            DocumentShare creado
        """
        share = DocumentShare.objects.create(
            document=document,
            shared_by=user,
            shared_with=recipient_user,
            shared_with_email=recipient_email or (recipient_user.email if recipient_user else ''),
            can_download=can_download,
            can_edit=can_edit,
            message=message,
            expires_at=timezone.now() + timedelta(days=expires_in_days)
        )
        
        # Protección con contraseña
        if password:
            from django.contrib.auth.hashers import make_password
            share.password = make_password(password)
            share.save()
        
        # Registrar actividad
        DocumentService.log_activity(
            document=document,
            user=user,
            action='share',
            details=f"Compartido con {recipient_email or recipient_user.email if recipient_user else 'enlace público'}"
        )
        
        # TODO: Enviar notificación
        
        return share
    
    @staticmethod
    def create_public_link(document, user, can_download=True, expires_in_days=7,
                          password=None):
        """
        Crea un enlace público para compartir.
        
        Args:
            document: Document
            user: User que crea el enlace
            can_download: Si permite descarga
            expires_in_days: Días hasta expiración
            password: Contraseña opcional
        
        Returns:
            DocumentShare con enlace público
        """
        share = DocumentShare.objects.create(
            document=document,
            shared_by=user,
            can_download=can_download,
            expires_at=timezone.now() + timedelta(days=expires_in_days)
        )
        
        # Generar enlace
        share.generate_public_link()
        
        # Contraseña
        if password:
            from django.contrib.auth.hashers import make_password
            share.password = make_password(password)
            share.save()
        
        return share
    
    @staticmethod
    def log_activity(document, user, action, details='', ip_address=None):
        """
        Registra actividad en un documento.
        
        Args:
            document: Document
            user: User
            action: Tipo de acción
            details: Detalles
            ip_address: IP del usuario
        
        Returns:
            DocumentActivity creado
        """
        activity = DocumentActivity.objects.create(
            document=document,
            user=user,
            action=action,
            details=details,
            ip_address=ip_address
        )
        
        # Actualizar contadores
        if action == 'view':
            document.view_count += 1
            document.save(update_fields=['view_count'])
        elif action == 'download':
            document.download_count += 1
            document.save(update_fields=['download_count'])
        
        return activity
    
    @staticmethod
    def add_comment(document, user, comment, parent=None):
        """
        Agrega un comentario a un documento.
        
        Args:
            document: Document
            user: User
            comment: Texto del comentario
            parent: Comentario padre (para respuestas)
        
        Returns:
            DocumentComment creado
        """
        comment_obj = DocumentComment.objects.create(
            document=document,
            user=user,
            comment=comment,
            parent=parent
        )
        
        # Registrar actividad
        DocumentService.log_activity(
            document=document,
            user=user,
            action='comment',
            details=comment[:100]
        )
        
        # TODO: Notificar al dueño del documento
        
        return comment_obj
    
    @staticmethod
    def get_storage_stats(organization):
        """
        Obtiene estadísticas de almacenamiento.
        
        Args:
            organization: Organization
        
        Returns:
            Dict con estadísticas
        """
        documents = Document.objects.filter(organization=organization)
        
        total_size = documents.aggregate(Sum('file_size'))['file_size__sum'] or 0
        total_count = documents.count()
        
        # Por tipo
        by_type = {}
        for doc_type, _ in Document.DOCUMENT_TYPE_CHOICES:
            count = documents.filter(document_type=doc_type).count()
            size = documents.filter(document_type=doc_type).aggregate(
                Sum('file_size')
            )['file_size__sum'] or 0
            
            if count > 0:
                by_type[doc_type] = {
                    'count': count,
                    'size': size
                }
        
        return {
            'total_size': total_size,
            'total_count': total_count,
            'by_type': by_type,
            'folders_count': Folder.objects.filter(organization=organization).count()
        }
    
    @staticmethod
    def cleanup_expired_shares():
        """Elimina shares expirados."""
        expired = DocumentShare.objects.filter(
            expires_at__lte=timezone.now()
        )
        
        count = expired.count()
        expired.delete()
        
        return count


class FolderService:
    """Servicio para gestionar carpetas."""
    
    @staticmethod
    def create_folder(name, organization, user, parent=None, description='',
                     color='#3B82F6', icon='folder'):
        """
        Crea una carpeta.
        
        Args:
            name: Nombre
            organization: Organization
            user: User creador
            parent: Carpeta padre
            description: Descripción
            color: Color
            icon: Ícono
        
        Returns:
            Folder creado
        """
        folder = Folder.objects.create(
            name=name,
            description=description,
            organization=organization,
            parent=parent,
            created_by=user,
            color=color,
            icon=icon
        )
        
        return folder
    
    @staticmethod
    def move_folder(folder, new_parent):
        """
        Mueve una carpeta a otra ubicación.
        
        Args:
            folder: Folder a mover
            new_parent: Nueva carpeta padre
        
        Returns:
            Folder actualizado
        """
        # Verificar que no se mueva a sí misma o a sus hijas
        if new_parent:
            parent = new_parent
            while parent:
                if parent.id == folder.id:
                    raise ValueError("No se puede mover una carpeta a sí misma o a sus subcarpetas")
                parent = parent.parent
        
        folder.parent = new_parent
        folder.save()
        
        return folder
    
    @staticmethod
    def delete_folder(folder, delete_documents=False):
        """
        Elimina una carpeta.
        
        Args:
            folder: Folder a eliminar
            delete_documents: Si eliminar también los documentos
        
        Returns:
            Número de objetos eliminados
        """
        if not delete_documents:
            # Mover documentos a la carpeta padre
            Document.objects.filter(folder=folder).update(folder=folder.parent)
            
            # Mover subcarpetas a la carpeta padre
            Folder.objects.filter(parent=folder).update(parent=folder.parent)
        
        return folder.delete()


def create_default_folders(organization):
    """Crea carpetas por defecto para una organización."""
    default_folders = [
        {'name': 'Pacientes', 'icon': 'users', 'color': '#3B82F6'},
        {'name': 'Facturas', 'icon': 'file-invoice', 'color': '#10B981'},
        {'name': 'Contratos', 'icon': 'file-contract', 'color': '#F59E0B'},
        {'name': 'Imágenes', 'icon': 'images', 'color': '#EC4899'},
        {'name': 'Documentos', 'icon': 'file-alt', 'color': '#8B5CF6'},
    ]
    
    created = []
    for folder_data in default_folders:
        folder, _ = Folder.objects.get_or_create(
            name=folder_data['name'],
            organization=organization,
            parent=None,
            defaults={
                'icon': folder_data['icon'],
                'color': folder_data['color'],
                'is_system': True
            }
        )
        created.append(folder)
    
    return created
