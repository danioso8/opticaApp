"""
Servicios para el sistema de auditoría.
Proporciona funciones para logging, búsqueda y exportación de auditorías.
"""
from django.contrib.contenttypes.models import ContentType
from django.db.models import Q, Count
from django.utils import timezone
from datetime import timedelta
import csv
import json
from io import StringIO

from .models import AuditLog, AuditConfig, AuditRetentionLog


class AuditService:
    """
    Servicio para gestionar auditorías.
    """
    
    @staticmethod
    def log_action(action, user=None, organization=None, instance=None, 
                   changes=None, ip_address=None, user_agent=None, 
                   description='', metadata=None):
        """
        Registra una acción en el log de auditoría.
        
        Args:
            action: Tipo de acción (CREATE, UPDATE, DELETE, etc.)
            user: Usuario que realiza la acción
            organization: Organización
            instance: Instancia del modelo afectado
            changes: Diccionario con cambios
            ip_address: IP del cliente
            user_agent: User agent del navegador
            description: Descripción adicional
            metadata: Metadatos adicionales
        
        Returns:
            AuditLog: Registro creado
        """
        # Verificar si debe auditarse
        if instance:
            model_name = f"{instance._meta.app_label}.{instance._meta.model_name}"
            config = AuditService.get_config(model_name, organization)
            
            if config and not config.should_track_action(action):
                return None
        
        # Crear registro
        content_type = None
        object_id = None
        object_repr = ''
        
        if instance:
            content_type = ContentType.objects.get_for_model(instance)
            object_id = str(instance.pk)
            object_repr = str(instance)[:500]
        
        audit_log = AuditLog.objects.create(
            action=action,
            user=user,
            organization=organization,
            content_type=content_type,
            object_id=object_id,
            object_repr=object_repr,
            changes=changes or {},
            ip_address=ip_address,
            user_agent=user_agent or '',
            description=description,
            metadata=metadata or {}
        )
        
        return audit_log
    
    @staticmethod
    def get_config(model_name, organization=None):
        """
        Obtiene la configuración de auditoría para un modelo.
        Primero busca config específica de la org, luego global.
        
        Args:
            model_name: Nombre del modelo (app.model)
            organization: Organización
        
        Returns:
            AuditConfig o None
        """
        # Buscar configuración específica de la organización
        if organization:
            config = AuditConfig.objects.filter(
                model_name=model_name,
                organization=organization,
                is_active=True
            ).first()
            
            if config:
                return config
        
        # Buscar configuración global
        config = AuditConfig.objects.filter(
            model_name=model_name,
            organization__isnull=True,
            is_active=True
        ).first()
        
        return config
    
    @staticmethod
    def get_object_history(instance, limit=50):
        """
        Obtiene el historial de auditoría de un objeto.
        
        Args:
            instance: Instancia del modelo
            limit: Número máximo de registros
        
        Returns:
            QuerySet de AuditLog
        """
        content_type = ContentType.objects.get_for_model(instance)
        
        return AuditLog.objects.filter(
            content_type=content_type,
            object_id=str(instance.pk)
        ).select_related('user', 'organization')[:limit]
    
    @staticmethod
    def search_logs(organization=None, user=None, action=None, 
                    model_name=None, date_from=None, date_to=None,
                    ip_address=None, limit=100):
        """
        Busca registros de auditoría con filtros.
        
        Args:
            organization: Filtrar por organización
            user: Filtrar por usuario
            action: Filtrar por acción
            model_name: Filtrar por modelo (app.model)
            date_from: Fecha inicio
            date_to: Fecha fin
            ip_address: Filtrar por IP
            limit: Número máximo de resultados
        
        Returns:
            QuerySet de AuditLog
        """
        queryset = AuditLog.objects.all()
        
        if organization:
            queryset = queryset.filter(organization=organization)
        
        if user:
            queryset = queryset.filter(user=user)
        
        if action:
            queryset = queryset.filter(action=action)
        
        if model_name:
            app_label, model = model_name.split('.')
            content_type = ContentType.objects.get(
                app_label=app_label,
                model=model
            )
            queryset = queryset.filter(content_type=content_type)
        
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
        
        if ip_address:
            queryset = queryset.filter(ip_address=ip_address)
        
        return queryset.select_related('user', 'organization', 'content_type')[:limit]
    
    @staticmethod
    def export_to_csv(queryset):
        """
        Exporta logs de auditoría a CSV.
        
        Args:
            queryset: QuerySet de AuditLog
        
        Returns:
            StringIO con contenido CSV
        """
        output = StringIO()
        writer = csv.writer(output)
        
        # Headers
        writer.writerow([
            'Fecha',
            'Usuario',
            'Organización',
            'Acción',
            'Modelo',
            'Objeto',
            'Cambios',
            'IP',
            'Descripción'
        ])
        
        # Datos
        for log in queryset:
            writer.writerow([
                log.created_at.strftime('%d/%m/%Y %H:%M:%S'),
                log.user.get_full_name() if log.user else 'Sistema',
                log.organization.name if log.organization else '-',
                log.get_action_display(),
                str(log.content_type) if log.content_type else '-',
                log.object_repr,
                log.get_changes_display(),
                log.ip_address or '-',
                log.description
            ])
        
        output.seek(0)
        return output
    
    @staticmethod
    def export_to_json(queryset):
        """
        Exporta logs de auditoría a JSON.
        
        Args:
            queryset: QuerySet de AuditLog
        
        Returns:
            String JSON
        """
        logs = []
        
        for log in queryset:
            logs.append({
                'id': log.id,
                'created_at': log.created_at.isoformat(),
                'user': {
                    'id': log.user.id if log.user else None,
                    'name': log.user.get_full_name() if log.user else 'Sistema'
                },
                'organization': {
                    'id': log.organization.id if log.organization else None,
                    'name': log.organization.name if log.organization else None
                },
                'action': log.action,
                'action_display': log.get_action_display(),
                'model': str(log.content_type) if log.content_type else None,
                'object_id': log.object_id,
                'object_repr': log.object_repr,
                'changes': log.changes,
                'ip_address': log.ip_address,
                'user_agent': log.user_agent,
                'description': log.description,
                'metadata': log.metadata
            })
        
        return json.dumps(logs, indent=2, ensure_ascii=False)
    
    @staticmethod
    def get_activity_stats(organization=None, days=30):
        """
        Obtiene estadísticas de actividad.
        
        Args:
            organization: Organización
            days: Días hacia atrás
        
        Returns:
            Dict con estadísticas
        """
        date_from = timezone.now() - timedelta(days=days)
        queryset = AuditLog.objects.filter(created_at__gte=date_from)
        
        if organization:
            queryset = queryset.filter(organization=organization)
        
        # Total de acciones
        total = queryset.count()
        
        # Por tipo de acción
        by_action = queryset.values('action').annotate(
            count=Count('id')
        ).order_by('-count')
        
        # Por usuario
        by_user = queryset.filter(
            user__isnull=False
        ).values(
            'user__first_name', 'user__last_name', 'user__email'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        # Por modelo
        by_model = queryset.filter(
            content_type__isnull=False
        ).values(
            'content_type__app_label', 'content_type__model'
        ).annotate(
            count=Count('id')
        ).order_by('-count')[:10]
        
        return {
            'total': total,
            'by_action': list(by_action),
            'by_user': list(by_user),
            'by_model': list(by_model),
            'period_days': days
        }
    
    @staticmethod
    def cleanup_old_logs(days=None):
        """
        Elimina logs antiguos según retention policy.
        
        Args:
            days: Días de retención (si None, usa config de cada modelo)
        
        Returns:
            Dict con resultados
        """
        from time import time
        start_time = time()
        
        total_deleted = 0
        oldest_date = None
        details = {}
        
        if days:
            # Eliminar todos los logs más antiguos que X días
            cutoff_date = timezone.now() - timedelta(days=days)
            deleted = AuditLog.objects.filter(
                created_at__lt=cutoff_date
            ).delete()
            total_deleted = deleted[0]
            oldest_date = cutoff_date
        else:
            # Eliminar según configuración de cada modelo
            configs = AuditConfig.objects.filter(is_active=True)
            
            for config in configs:
                cutoff_date = timezone.now() - timedelta(days=config.retention_days)
                
                # Filtrar por modelo
                if config.organization:
                    deleted = AuditLog.objects.filter(
                        organization=config.organization,
                        created_at__lt=cutoff_date
                    ).delete()
                else:
                    deleted = AuditLog.objects.filter(
                        created_at__lt=cutoff_date
                    ).delete()
                
                count = deleted[0]
                total_deleted += count
                
                if count > 0:
                    details[config.model_name] = {
                        'deleted': count,
                        'cutoff_date': cutoff_date.isoformat()
                    }
                    
                    if not oldest_date or cutoff_date < oldest_date:
                        oldest_date = cutoff_date
        
        duration = time() - start_time
        
        # Registrar limpieza
        retention_log = AuditRetentionLog.objects.create(
            logs_deleted=total_deleted,
            oldest_date_deleted=oldest_date,
            duration_seconds=duration,
            details=details
        )
        
        return {
            'deleted': total_deleted,
            'oldest_date': oldest_date,
            'duration': duration,
            'details': details
        }


def create_default_configs():
    """
    Crea configuraciones de auditoría por defecto para modelos críticos.
    """
    # Modelos críticos que siempre deben auditarse
    critical_models = [
        'patients.Patient',
        'appointments.Appointment',
        'sales.Sale',
        'billing.Invoice',
        'billing.Payment',
        'inventory.Product',
        'inventory.StockMovement',
        'users.User',
        'organizations.Organization',
        'organizations.Member',
        'permissions.Role',
        'permissions.UserRole',
    ]
    
    for model_name in critical_models:
        AuditConfig.objects.get_or_create(
            model_name=model_name,
            organization=None,  # Global
            defaults={
                'track_creates': True,
                'track_updates': True,
                'track_deletes': True,
                'track_reads': False,
                'retention_days': 365,
                'is_active': True,
                'excluded_fields': ['updated_at', 'last_login']
            }
        )
    
    return len(critical_models)
