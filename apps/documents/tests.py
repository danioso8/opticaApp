"""
Tests para el sistema de documentos.
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile

from apps.organizations.models import Organization
from apps.documents.models import Folder, Document, DocumentShare, DocumentComment
from apps.documents.services import DocumentService, FolderService, create_default_folders

User = get_user_model()


class FolderTestCase(TestCase):
    """Tests para Folder."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.organization = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
    
    def test_create_folder(self):
        """Prueba crear una carpeta."""
        folder = FolderService.create_folder(
            name='Test Folder',
            organization=self.organization,
            user=self.user
        )
        
        self.assertIsNotNone(folder)
        self.assertEqual(folder.name, 'Test Folder')
    
    def test_subfolder(self):
        """Prueba crear subcarpeta."""
        parent = FolderService.create_folder(
            name='Parent',
            organization=self.organization,
            user=self.user
        )
        
        child = FolderService.create_folder(
            name='Child',
            organization=self.organization,
            user=self.user,
            parent=parent
        )
        
        self.assertEqual(child.parent, parent)
        self.assertEqual(child.get_full_path(), 'Parent/Child')
    
    def test_create_default_folders(self):
        """Prueba crear carpetas por defecto."""
        folders = create_default_folders(self.organization)
        self.assertGreater(len(folders), 0)


class DocumentTestCase(TestCase):
    """Tests para Document."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.organization = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
    
    def test_upload_document(self):
        """Prueba subir un documento."""
        file = SimpleUploadedFile(
            "test.pdf",
            b"file_content",
            content_type="application/pdf"
        )
        
        document = DocumentService.upload_document(
            file=file,
            organization=self.organization,
            user=self.user,
            title='Test Document'
        )
        
        self.assertIsNotNone(document)
        self.assertEqual(document.title, 'Test Document')
        self.assertEqual(document.document_type, 'pdf')
    
    def test_search_documents(self):
        """Prueba buscar documentos."""
        file = SimpleUploadedFile("test.pdf", b"content")
        
        DocumentService.upload_document(
            file=file,
            organization=self.organization,
            user=self.user,
            title='Test PDF'
        )
        
        results = DocumentService.search_documents(
            organization=self.organization,
            query='Test',
            user=self.user
        )
        
        self.assertEqual(results.count(), 1)


class DocumentShareTestCase(TestCase):
    """Tests para DocumentShare."""
    
    def setUp(self):
        """Configuración inicial."""
        self.user = User.objects.create_user(
            email='test@example.com',
            password='testpass123'
        )
        
        self.organization = Organization.objects.create(
            name='Test Org',
            slug='test-org'
        )
        
        file = SimpleUploadedFile("test.pdf", b"content")
        self.document = DocumentService.upload_document(
            file=file,
            organization=self.organization,
            user=self.user
        )
    
    def test_share_document(self):
        """Prueba compartir documento."""
        share = DocumentService.share_document(
            document=self.document,
            user=self.user,
            recipient_email='recipient@example.com'
        )
        
        self.assertIsNotNone(share)
        self.assertEqual(share.shared_with_email, 'recipient@example.com')
    
    def test_create_public_link(self):
        """Prueba crear enlace público."""
        share = DocumentService.create_public_link(
            document=self.document,
            user=self.user
        )
        
        self.assertIsNotNone(share)
        self.assertIsNotNone(share.public_link)
