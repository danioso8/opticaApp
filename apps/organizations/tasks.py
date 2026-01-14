# -*- coding: utf-8 -*-
"""
Tareas Celery para gestión automática de trials y suscripciones
"""
from celery import shared_task
from django.utils import timezone
from datetime import timedelta
from apps.organizations.models import Organization, TrialStatus
from apps.organizations.services.notifications import TrialNotificationService
import logging

logger = logging.getLogger(__name__)


@shared_task
def check_trial_status_daily():
    """
    Tarea diaria para verificar el estado de los trials
    Se ejecuta todos los días a las 9 AM
    """
    logger.info("🔍 Iniciando verificación diaria de trials")
    
    now = timezone.now()
    trials = TrialStatus.objects.filter(state='active')
    
    stats = {
        'day20': 0,
        'day25': 0,
        'day28': 0,
        'expired': 0,
        'grace': 0,
        'archive': 0,
    }
    
    for trial in trials:
        days_since_start = (now - trial.trial_start).days
        
        # Día 20: Primer recordatorio (10 días restantes)
        if days_since_start == 20:
            # Verificar que no se haya enviado ya
            if not trial.organization.notifications_log.filter(
                notification_type='trial_day20'
            ).exists():
                TrialNotificationService.send_trial_day20(trial.organization, trial)
                stats['day20'] += 1
                logger.info(f"📧 Día 20 enviado a {trial.organization.name}")
        
        # Día 25: Recordatorio + Stats (5 días restantes)
        elif days_since_start == 25:
            if not trial.organization.notifications_log.filter(
                notification_type='trial_day25'
            ).exists():
                TrialNotificationService.send_trial_day25(trial.organization, trial)
                stats['day25'] += 1
                logger.info(f"📧 Día 25 enviado a {trial.organization.name}")
        
        # Día 28: Urgencia (2 días restantes)
        elif days_since_start == 28:
            if not trial.organization.notifications_log.filter(
                notification_type='trial_day28'
            ).exists():
                TrialNotificationService.send_trial_day28(trial.organization)
                stats['day28'] += 1
                logger.info(f"📧 Día 28 enviado a {trial.organization.name}")
        
        # Día 30: Trial expirado
        elif days_since_start >= 30:
            if trial.state == 'active':
                trial.state = 'expired_readonly'
                trial.save()
                TrialNotificationService.send_trial_expired(trial.organization)
                stats['expired'] += 1
                logger.info(f"⏰ Trial expirado: {trial.organization.name} → Modo lectura")
    
    # Verificar trials en período de gracia
    grace_trials = TrialStatus.objects.filter(state='expired_readonly')
    for trial in grace_trials:
        days_since_start = (now - trial.trial_start).days
        
        # Día 37: Recordatorio en gracia
        if days_since_start == 37:
            if not trial.organization.notifications_log.filter(
                notification_type='grace_reminder'
            ).exists():
                TrialNotificationService.send_grace_reminder(trial.organization)
                trial.state = 'expired_grace'
                trial.save()
                stats['grace'] += 1
                logger.info(f"📧 Gracia enviado a {trial.organization.name}")
        
        # Día 45: Advertencia de archivo
        elif days_since_start == 45:
            if not trial.organization.notifications_log.filter(
                notification_type='archive_warning'
            ).exists():
                TrialNotificationService.send_archive_warning(trial.organization)
                stats['archive'] += 1
                logger.info(f"⚠️ Advertencia archivo: {trial.organization.name}")
    
    logger.info(f"✅ Verificación completada: {stats}")
    return stats


@shared_task
def archive_expired_organizations():
    """
    Tarea semanal para archivar organizaciones que no pagaron
    Día 90: Archivar datos
    """
    logger.info("📦 Iniciando proceso de archivo de organizaciones")
    
    now = timezone.now()
    trials = TrialStatus.objects.filter(
        state__in=['expired_grace', 'expired_readonly']
    )
    
    archived_count = 0
    
    for trial in trials:
        if trial.should_archive:
            # Marcar como archivado
            trial.state = 'expired_archived'
            trial.save()
            
            # Aquí podrías mover datos a un almacenamiento frío o comprimir
            logger.info(f"📦 Organización archivada: {trial.organization.name}")
            archived_count += 1
            
            # Enviar notificación
            from apps.organizations.services.notifications import TrialNotificationService
            try:
                user = trial.organization.owner
                subject = "Tus datos han sido archivados"
                message = f"""
Hola {user.first_name},

Tus datos de {trial.organization.name} han sido archivados de forma segura.

Puedes recuperarlos en cualquier momento activando un plan.

Recuperar datos: https://www.optikaapp.com/dashboard/modules/select/
"""
                
                from django.core.mail import send_mail
                send_mail(
                    subject=subject,
                    message=message,
                    from_email='noreply@optikaapp.com',
                    recipient_list=[user.email],
                    fail_silently=True,
                )
            except Exception as e:
                logger.error(f"Error enviando notificación de archivo: {str(e)}")
    
    logger.info(f"✅ {archived_count} organizaciones archivadas")
    return {'archived': archived_count}


@shared_task
def delete_archived_organizations():
    """
    Tarea mensual para eliminar organizaciones archivadas hace mucho tiempo
    Día 210: Eliminación permanente
    """
    logger.info("🗑️ Iniciando proceso de eliminación de organizaciones")
    
    trials = TrialStatus.objects.filter(state='expired_archived')
    
    deleted_count = 0
    
    for trial in trials:
        if trial.should_delete:
            org_name = trial.organization.name
            user_email = trial.organization.owner.email if trial.organization.owner else None
            
            # Enviar última notificación
            if user_email:
                try:
                    from django.core.mail import send_mail
                    send_mail(
                        subject="Cuenta eliminada - Esperamos verte pronto",
                        message=f"Tu cuenta de {org_name} ha sido eliminada permanentemente.",
                        from_email='noreply@optikaapp.com',
                        recipient_list=[user_email],
                        fail_silently=True,
                    )
                except:
                    pass
            
            # ELIMINAR (comentado por seguridad - descomentar en producción)
            # trial.organization.delete()
            logger.warning(f"⚠️ PENDIENTE ELIMINACIÓN: {org_name}")
            deleted_count += 1
    
    logger.info(f"✅ {deleted_count} organizaciones marcadas para eliminación")
    return {'deleted': deleted_count}


@shared_task
def send_welcome_email_after_registration(organization_id):
    """
    Enviar email y WhatsApp de bienvenida inmediatamente después del registro
    """
    try:
        organization = Organization.objects.get(id=organization_id)
        
        # Crear TrialStatus si no existe
        trial, created = TrialStatus.objects.get_or_create(
            organization=organization,
            defaults={
                'trial_start': timezone.now(),
                'state': 'active',
            }
        )
        
        # Enviar notificaciones de bienvenida
        TrialNotificationService.send_trial_welcome(organization)
        
        logger.info(f"✅ Bienvenida enviada a {organization.name}")
        return {'success': True, 'organization': organization.name}
        
    except Organization.DoesNotExist:
        logger.error(f"❌ Organización {organization_id} no encontrada")
        return {'success': False, 'error': 'Organization not found'}
    except Exception as e:
        logger.error(f"❌ Error en bienvenida: {str(e)}")
        return {'success': False, 'error': str(e)}


@shared_task
def update_module_usage_stats():
    """
    Actualizar estadísticas de uso de módulos para cada organización
    Se ejecuta diariamente para trackear qué módulos usa cada organización
    """
    logger.info("📊 Actualizando estadísticas de uso de módulos")
    
    from apps.audit.models import AuditLog
    from datetime import datetime, timedelta
    
    trials = TrialStatus.objects.filter(state='active')
    
    for trial in trials:
        # Obtener logs de los últimos 30 días
        thirty_days_ago = timezone.now() - timedelta(days=30)
        
        logs = AuditLog.objects.filter(
            organization=trial.organization,
            timestamp__gte=thirty_days_ago
        ).values('action_type').annotate(
            count=models.Count('id')
        )
        
        # Mapear acciones a módulos
        module_usage = {}
        for log in logs:
            action = log['action_type']
            count = log['count']
            
            # Mapeo simple de acciones a módulos
            if 'appointment' in action.lower():
                module_usage['appointments'] = module_usage.get('appointments', 0) + count
            elif 'patient' in action.lower():
                module_usage['patients'] = module_usage.get('patients', 0) + count
            elif 'whatsapp' in action.lower():
                module_usage['whatsapp'] = module_usage.get('whatsapp', 0) + count
            elif 'invoice' in action.lower() or 'sale' in action.lower():
                module_usage['pos'] = module_usage.get('pos', 0) + count
            elif 'history' in action.lower() or 'clinical' in action.lower():
                module_usage['clinical_history'] = module_usage.get('clinical_history', 0) + count
        
        # Actualizar trial status
        trial.most_used_modules = module_usage
        trial.save()
        
        logger.debug(f"📊 Stats actualizadas para {trial.organization.name}: {module_usage}")
    
    logger.info(f"✅ Estadísticas actualizadas para {trials.count()} organizaciones")
    return {'updated': trials.count()}
