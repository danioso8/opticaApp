"""
Servicios de lógica de negocio para workflows
"""
from django.utils import timezone
from django.db import transaction
from django.contrib.contenttypes.models import ContentType

from apps.workflows.models import (
    WorkflowDefinition, WorkflowTransition, WorkflowAction,
    WorkflowInstance, WorkflowHistory, WorkflowApproval
)


class WorkflowService:
    """Servicio para gestión de workflows"""
    
    @staticmethod
    def create_workflow(organization, name, slug, content_type, initial_state, created_by, **kwargs):
        """
        Crea una nueva definición de workflow
        
        Args:
            organization: Organización
            name: Nombre del workflow
            slug: Slug único
            content_type: Tipo de contenido al que aplica
            initial_state: Estado inicial
            created_by: Usuario creador
            **kwargs: Otros parámetros
        
        Returns:
            WorkflowDefinition: El workflow creado
        """
        workflow = WorkflowDefinition.objects.create(
            organization=organization,
            name=name,
            slug=slug,
            content_type=content_type,
            initial_state=initial_state,
            created_by=created_by,
            **kwargs
        )
        
        return workflow
    
    @staticmethod
    def start_workflow(workflow, content_object, started_by):
        """
        Inicia una instancia de workflow para un objeto
        
        Args:
            workflow: WorkflowDefinition
            content_object: Objeto al que se aplica el workflow
            started_by: Usuario que inicia
        
        Returns:
            WorkflowInstance: La instancia creada
        """
        content_type = ContentType.objects.get_for_model(content_object)
        
        instance = WorkflowInstance.objects.create(
            workflow=workflow,
            organization=workflow.organization,
            content_type=content_type,
            object_id=content_object.id,
            current_state=workflow.initial_state,
            status='active',
            started_by=started_by
        )
        
        # Registrar en historial
        WorkflowHistoryService.log_transition(
            instance=instance,
            from_state='',
            to_state=workflow.initial_state,
            user=started_by,
            comment='Workflow iniciado'
        )
        
        # Ejecutar acciones del estado inicial
        WorkflowActionService.execute_actions_for_state(
            instance=instance,
            state=workflow.initial_state,
            trigger='on_enter'
        )
        
        return instance
    
    @staticmethod
    def get_available_transitions(instance, user=None):
        """
        Obtiene las transiciones disponibles desde el estado actual
        
        Args:
            instance: WorkflowInstance
            user: Usuario (para verificar permisos)
        
        Returns:
            QuerySet: Transiciones disponibles
        """
        transitions = WorkflowTransition.objects.filter(
            workflow=instance.workflow,
            from_state=instance.current_state,
            is_active=True
        )
        
        # Si hay usuario, filtrar por permisos
        if user:
            # TODO: Implementar verificación de permisos
            pass
        
        return transitions.order_by('order')
    
    @staticmethod
    def can_transition(instance, transition, user=None):
        """
        Verifica si se puede realizar una transición
        
        Args:
            instance: WorkflowInstance
            transition: WorkflowTransition
            user: Usuario que intenta la transición
        
        Returns:
            tuple: (can_transition, error_message)
        """
        # Verificar que la instancia esté activa
        if not instance.is_active():
            return False, "La instancia de workflow no está activa"
        
        # Verificar que la transición sea desde el estado actual
        if transition.from_state != instance.current_state:
            return False, f"La transición no es válida desde el estado {instance.current_state}"
        
        # Verificar permisos si hay usuario
        if user and transition.required_permission:
            # TODO: Implementar verificación de permisos
            pass
        
        # Verificar condiciones
        if transition.conditions:
            # TODO: Implementar evaluación de condiciones
            pass
        
        return True, None
    
    @staticmethod
    @transaction.atomic
    def execute_transition(instance, transition, user, comment='', ip_address=None):
        """
        Ejecuta una transición de workflow
        
        Args:
            instance: WorkflowInstance
            transition: WorkflowTransition
            user: Usuario que ejecuta
            comment: Comentario opcional
            ip_address: IP del usuario
        
        Returns:
            tuple: (success, message)
        """
        # Verificar si se puede hacer la transición
        can_do, error = WorkflowService.can_transition(instance, transition, user)
        
        if not can_do:
            return False, error
        
        # Si requiere aprobación, crear solicitud
        if transition.require_approval:
            approval = WorkflowApprovalService.request_approval(
                instance=instance,
                transition=transition,
                requested_by=user
            )
            return True, "Solicitud de aprobación creada"
        
        # Ejecutar acciones "on_exit" del estado actual
        WorkflowActionService.execute_actions_for_state(
            instance=instance,
            state=instance.current_state,
            trigger='on_exit'
        )
        
        # Ejecutar acciones "on_transition"
        WorkflowActionService.execute_actions_for_transition(
            instance=instance,
            transition=transition,
            trigger='on_transition'
        )
        
        # Guardar estado anterior
        old_state = instance.current_state
        
        # Cambiar estado
        instance.current_state = transition.to_state
        
        # Si llegó a un estado final, marcar como completado
        if instance.is_in_final_state():
            instance.complete()
        else:
            instance.save()
        
        # Registrar en historial
        WorkflowHistoryService.log_transition(
            instance=instance,
            from_state=old_state,
            to_state=transition.to_state,
            user=user,
            transition=transition,
            comment=comment,
            ip_address=ip_address
        )
        
        # Ejecutar acciones "on_enter" del nuevo estado
        WorkflowActionService.execute_actions_for_state(
            instance=instance,
            state=transition.to_state,
            trigger='on_enter'
        )
        
        return True, f"Transición exitosa: {old_state} → {transition.to_state}"
    
    @staticmethod
    def get_workflow_for_object(content_object):
        """
        Obtiene el workflow activo para un objeto
        
        Args:
            content_object: Objeto
        
        Returns:
            WorkflowInstance o None
        """
        content_type = ContentType.objects.get_for_model(content_object)
        
        return WorkflowInstance.objects.filter(
            content_type=content_type,
            object_id=content_object.id,
            status='active'
        ).first()


class WorkflowActionService:
    """Servicio para ejecutar acciones de workflow"""
    
    @staticmethod
    def execute_actions_for_state(instance, state, trigger):
        """
        Ejecuta acciones asociadas a un estado
        
        Args:
            instance: WorkflowInstance
            state: Estado
            trigger: Tipo de trigger (on_enter, on_exit)
        """
        actions = WorkflowAction.objects.filter(
            workflow=instance.workflow,
            state=state,
            trigger=trigger,
            is_active=True
        ).order_by('order')
        
        for action in actions:
            WorkflowActionService.execute_action(instance, action)
    
    @staticmethod
    def execute_actions_for_transition(instance, transition, trigger):
        """
        Ejecuta acciones asociadas a una transición
        
        Args:
            instance: WorkflowInstance
            transition: WorkflowTransition
            trigger: Tipo de trigger
        """
        actions = WorkflowAction.objects.filter(
            workflow=instance.workflow,
            transition=transition,
            trigger=trigger,
            is_active=True
        ).order_by('order')
        
        for action in actions:
            WorkflowActionService.execute_action(instance, action)
    
    @staticmethod
    def execute_action(instance, action):
        """
        Ejecuta una acción específica
        
        Args:
            instance: WorkflowInstance
            action: WorkflowAction
        
        Returns:
            bool: True si la acción se ejecutó exitosamente
        """
        try:
            if action.action_type == 'send_notification':
                return WorkflowActionService._send_notification(instance, action)
            
            elif action.action_type == 'send_email':
                return WorkflowActionService._send_email(instance, action)
            
            elif action.action_type == 'create_task':
                return WorkflowActionService._create_task(instance, action)
            
            elif action.action_type == 'update_field':
                return WorkflowActionService._update_field(instance, action)
            
            elif action.action_type == 'call_webhook':
                return WorkflowActionService._call_webhook(instance, action)
            
            elif action.action_type == 'assign_user':
                return WorkflowActionService._assign_user(instance, action)
            
            return False
        
        except Exception as e:
            print(f"Error ejecutando acción {action.id}: {e}")
            return False
    
    @staticmethod
    def _send_notification(instance, action):
        """Envía una notificación"""
        try:
            from apps.notifications.services import NotificationService
            
            params = action.parameters
            
            NotificationService.create_notification(
                organization=instance.organization,
                user_id=params.get('user_id'),
                title=params.get('title', 'Notificación de Workflow'),
                message=params.get('message', ''),
                notification_type='workflow',
                channel=params.get('channel', 'app'),
                related_object=instance.content_object
            )
            
            return True
        except Exception as e:
            print(f"Error enviando notificación: {e}")
            return False
    
    @staticmethod
    def _send_email(instance, action):
        """Envía un email"""
        # TODO: Implementar envío de email
        return True
    
    @staticmethod
    def _create_task(instance, action):
        """Crea una tarea"""
        try:
            from apps.tasks.services import TaskService
            
            params = action.parameters
            
            TaskService.create_task(
                organization=instance.organization,
                created_by=instance.started_by,
                title=params.get('title', 'Tarea de Workflow'),
                description=params.get('description', ''),
                assigned_to_id=params.get('assigned_to_id'),
                priority=params.get('priority', 'medium'),
                related_object=instance.content_object
            )
            
            return True
        except Exception as e:
            print(f"Error creando tarea: {e}")
            return False
    
    @staticmethod
    def _update_field(instance, action):
        """Actualiza un campo del objeto"""
        try:
            params = action.parameters
            field_name = params.get('field_name')
            field_value = params.get('field_value')
            
            if field_name and hasattr(instance.content_object, field_name):
                setattr(instance.content_object, field_name, field_value)
                instance.content_object.save()
                return True
            
            return False
        except Exception as e:
            print(f"Error actualizando campo: {e}")
            return False
    
    @staticmethod
    def _call_webhook(instance, action):
        """Llama a un webhook"""
        # TODO: Implementar llamada a webhook
        return True
    
    @staticmethod
    def _assign_user(instance, action):
        """Asigna un usuario al objeto"""
        try:
            params = action.parameters
            user_id = params.get('user_id')
            field_name = params.get('field_name', 'assigned_to')
            
            if user_id and hasattr(instance.content_object, field_name):
                from django.contrib.auth import get_user_model
                User = get_user_model()
                
                user = User.objects.get(id=user_id)
                setattr(instance.content_object, field_name, user)
                instance.content_object.save()
                return True
            
            return False
        except Exception as e:
            print(f"Error asignando usuario: {e}")
            return False


class WorkflowHistoryService:
    """Servicio para historial de workflows"""
    
    @staticmethod
    def log_transition(instance, from_state, to_state, user, transition=None, comment='', ip_address=None, metadata=None):
        """
        Registra una transición en el historial
        
        Args:
            instance: WorkflowInstance
            from_state: Estado origen
            to_state: Estado destino
            user: Usuario
            transition: WorkflowTransition (opcional)
            comment: Comentario
            ip_address: IP del usuario
            metadata: Datos adicionales
        
        Returns:
            WorkflowHistory: El registro creado
        """
        history = WorkflowHistory.objects.create(
            instance=instance,
            organization=instance.organization,
            transition=transition,
            from_state=from_state,
            to_state=to_state,
            user=user,
            comment=comment,
            ip_address=ip_address,
            metadata=metadata or {}
        )
        
        return history
    
    @staticmethod
    def get_instance_history(instance):
        """Obtiene el historial de una instancia"""
        return WorkflowHistory.objects.filter(
            instance=instance
        ).order_by('-created_at')


class WorkflowApprovalService:
    """Servicio para aprobaciones de workflow"""
    
    @staticmethod
    def request_approval(instance, transition, requested_by, approver=None):
        """
        Solicita una aprobación para una transición
        
        Args:
            instance: WorkflowInstance
            transition: WorkflowTransition
            requested_by: Usuario solicitante
            approver: Aprobador específico (opcional)
        
        Returns:
            WorkflowApproval: La solicitud creada
        """
        approval = WorkflowApproval.objects.create(
            instance=instance,
            organization=instance.organization,
            transition=transition,
            requested_by=requested_by,
            approver=approver,
            status='pending'
        )
        
        # Notificar al aprobador
        if approver:
            try:
                from apps.notifications.services import NotificationService
                
                NotificationService.create_notification(
                    organization=instance.organization,
                    user=approver,
                    title=f"Solicitud de Aprobación: {transition.name}",
                    message=f"Se requiere tu aprobación para: {transition.name}",
                    notification_type='workflow_approval',
                    channel='app',
                    priority='high',
                    related_object=instance
                )
            except Exception as e:
                print(f"Error notificando aprobador: {e}")
        
        return approval
    
    @staticmethod
    def approve_transition(approval, user, comment=''):
        """
        Aprueba una transición
        
        Args:
            approval: WorkflowApproval
            user: Usuario que aprueba
            comment: Comentario
        
        Returns:
            tuple: (success, message)
        """
        approval.approve(user, comment)
        
        # Ejecutar la transición
        return WorkflowService.execute_transition(
            instance=approval.instance,
            transition=approval.transition,
            user=user,
            comment=f"Aprobado: {comment}"
        )
    
    @staticmethod
    def reject_transition(approval, user, comment=''):
        """
        Rechaza una transición
        
        Args:
            approval: WorkflowApproval
            user: Usuario que rechaza
            comment: Comentario
        
        Returns:
            bool: True si se rechazó exitosamente
        """
        approval.reject(user, comment)
        
        # Notificar al solicitante
        try:
            from apps.notifications.services import NotificationService
            
            NotificationService.create_notification(
                organization=approval.organization,
                user=approval.requested_by,
                title=f"Aprobación Rechazada: {approval.transition.name}",
                message=f"Tu solicitud fue rechazada. Motivo: {comment}",
                notification_type='workflow_approval_rejected',
                channel='app',
                priority='high',
                related_object=approval.instance
            )
        except Exception as e:
            print(f"Error notificando rechazo: {e}")
        
        return True
    
    @staticmethod
    def get_pending_approvals(user):
        """Obtiene aprobaciones pendientes para un usuario"""
        return WorkflowApproval.objects.filter(
            approver=user,
            status='pending'
        ).select_related('instance', 'transition').order_by('-requested_at')


def create_default_workflows(organization, created_by):
    """
    Crea workflows predeterminados
    
    Args:
        organization: Organización
        created_by: Usuario creador
    
    Returns:
        list: Workflows creados
    """
    # TODO: Definir workflows predeterminados según tipo de negocio
    # Por ejemplo: Aprobación de Presupuestos, Validación de Pedidos, etc.
    
    workflows = []
    
    return workflows
