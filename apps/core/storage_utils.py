"""
Utilidades para manejo de almacenamiento de archivos
Sistema multi-tenant: cada organización tiene su propia carpeta
"""
import os
from django.utils.deconstruct import deconstructible


@deconstructible
class OrganizationUploadPath:
    """
    Clase para generar paths de upload dinámicos por organización
    
    Uso:
        logo = models.ImageField(upload_to=OrganizationUploadPath('logos'))
    
    Resultado:
        org_1/logos/filename.jpg
        org_2/logos/filename.jpg
    """
    
    def __init__(self, subfolder=''):
        self.subfolder = subfolder
    
    def __call__(self, instance, filename):
        """
        Genera el path completo para el archivo
        
        Args:
            instance: Instancia del modelo
            filename: Nombre del archivo original
            
        Returns:
            str: Path relativo para guardar el archivo
        """
        # Obtener ID de organización
        org_id = self._get_organization_id(instance)
        
        # Limpiar nombre de archivo
        filename = self._clean_filename(filename)
        
        # Construir path: org_{id}/{subfolder}/{filename}
        if self.subfolder:
            return os.path.join(f'org_{org_id}', self.subfolder, filename)
        else:
            return os.path.join(f'org_{org_id}', filename)
    
    def _get_organization_id(self, instance):
        """Obtiene el ID de organización de la instancia"""
        # Intentar obtener directamente
        if hasattr(instance, 'organization') and instance.organization:
            return instance.organization.id
        
        # Si es una organización misma
        if hasattr(instance, 'id') and instance.__class__.__name__ == 'Organization':
            return instance.id
        
        # Si es un LandingPageConfig u otro modelo relacionado
        if hasattr(instance, 'organization_id') and instance.organization_id:
            return instance.organization_id
        
        # Default: carpeta compartida
        return 'shared'
    
    def _clean_filename(self, filename):
        """Limpia el nombre del archivo para evitar problemas"""
        import re
        from django.utils.text import get_valid_filename
        
        # Obtener nombre y extensión
        name, ext = os.path.splitext(filename)
        
        # Limpiar nombre
        name = get_valid_filename(name)
        name = re.sub(r'[^\w\s-]', '', name).strip()
        name = re.sub(r'[-\s]+', '-', name)
        
        # Limitar longitud
        if len(name) > 50:
            name = name[:50]
        
        return f"{name}{ext}".lower()


def get_organization_media_path(organization_id, subfolder=''):
    """
    Obtiene el path absoluto de media para una organización
    
    Args:
        organization_id: ID de la organización
        subfolder: Subcarpeta opcional (logos, landing, etc)
        
    Returns:
        Path: Path absoluto a la carpeta
    """
    from django.conf import settings
    from pathlib import Path
    
    base_path = Path(settings.MEDIA_ROOT) / f'org_{organization_id}'
    
    if subfolder:
        return base_path / subfolder
    
    return base_path


def create_organization_media_folders(organization_id):
    """
    Crea la estructura de carpetas para una nueva organización
    
    Args:
        organization_id: ID de la organización
    """
    from pathlib import Path
    
    folders = [
        'logos',
        'landing/hero',
        'landing/services',
        'doctors/signatures',
        'doctors/photos',
        'products/images',
        'ar_frames/front',
        'ar_frames/side',
        'ar_frames/overlay',
        'invoices',
        'reports',
    ]
    
    for folder in folders:
        path = get_organization_media_path(organization_id, folder)
        path.mkdir(parents=True, exist_ok=True)
        
        # Crear archivo .gitkeep para preservar carpetas vacías
        gitkeep = path / '.gitkeep'
        gitkeep.touch(exist_ok=True)


def get_organization_storage_usage(organization_id):
    """
    Calcula el uso de almacenamiento de una organización
    
    Args:
        organization_id: ID de la organización
        
    Returns:
        dict: Información de uso de almacenamiento
    """
    import os
    from pathlib import Path
    
    org_path = get_organization_media_path(organization_id)
    
    if not org_path.exists():
        return {
            'total_bytes': 0,
            'total_mb': 0,
            'total_gb': 0,
            'file_count': 0
        }
    
    total_size = 0
    file_count = 0
    
    for dirpath, dirnames, filenames in os.walk(org_path):
        for filename in filenames:
            if filename != '.gitkeep':
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                    file_count += 1
                except OSError:
                    pass
    
    return {
        'total_bytes': total_size,
        'total_mb': round(total_size / (1024 * 1024), 2),
        'total_gb': round(total_size / (1024 * 1024 * 1024), 2),
        'file_count': file_count
    }
