"""
Utilidades para registro de auditoría
"""
import json
from .models_audit import AuditLog


def log_action(user, organization, action, description, content_type=None, object_id=None, metadata=None, request=None):
    """
    Registra una acción en el sistema de auditoría
    
    Args:
        user: Usuario que realizó la acción
        organization: Organización en la que se realizó
        action: Código de la acción (ver AuditLog.ACTION_CHOICES)
        description: Descripción detallada
        content_type: Tipo de modelo afectado (opcional)
        object_id: ID del objeto afectado (opcional)
        metadata: Datos adicionales en JSON (opcional)
        request: Request HTTP para obtener IP (opcional)
    """
    ip_address = None
    if request:
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip_address = x_forwarded_for.split(',')[0]
        else:
            ip_address = request.META.get('REMOTE_ADDR')
    
    # Convertir metadata a JSON string si es un dict
    metadata_str = None
    if metadata:
        if isinstance(metadata, dict):
            metadata_str = json.dumps(metadata)
        elif isinstance(metadata, str):
            metadata_str = metadata
        else:
            metadata_str = str(metadata)
    
    return AuditLog.objects.create(
        user=user,
        organization=organization,
        action=action,
        description=description,
        content_type=content_type,
        object_id=object_id,
        metadata=metadata_str,
        ip_address=ip_address
    )
