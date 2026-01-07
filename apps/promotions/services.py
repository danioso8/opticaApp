"""
Servicio para envío seguro de campañas de promociones
Implementa límites y delays para evitar bloqueo de WhatsApp
"""
import logging
import time
from datetime import datetime, timedelta
from django.utils import timezone
from django.db import transaction
from apps.promotions.models import PromotionCampaign, PromotionMessage
from apps.appointments.whatsapp_baileys_client import whatsapp_baileys_client

logger = logging.getLogger(__name__)


class CampaignSender:
    """Servicio para envío controlado de campañas"""
    
    def __init__(self, campaign):
        self.campaign = campaign
        self.org_id = campaign.organization.id
        self.client = whatsapp_baileys_client
    
    def is_sending_allowed(self):
        """Verifica si está en horario permitido para enviar"""
        now = timezone.now()
        current_hour = now.hour
        
        # Verificar horario
        if not (self.campaign.send_hour_start <= current_hour < self.campaign.send_hour_end):
            logger.info(f"Fuera de horario de envío. Hora actual: {current_hour}")
            return False
        
        # Verificar día de la semana (no enviar sábados y domingos)
        if now.weekday() >= 5:  # 5=Sábado, 6=Domingo
            logger.info(f"No se envía en fin de semana. Día: {now.weekday()}")
            return False
        
        return True
    
    def check_whatsapp_connection(self):
        """Verifica que WhatsApp esté conectado"""
        try:
            status = self.client.get_status(self.org_id)
            if status and status.get('status') == 'connected':
                logger.info(f"WhatsApp conectado para org {self.org_id}")
                return True
            else:
                logger.warning(f"WhatsApp no conectado para org {self.org_id}")
                return False
        except Exception as e:
            logger.error(f"Error verificando conexión WhatsApp: {e}")
            return False
    
    def get_daily_sent_count(self):
        """Cuenta cuántos mensajes se han enviado hoy"""
        today = timezone.now().date()
        count = PromotionMessage.objects.filter(
            campaign=self.campaign,
            status='sent',
            sent_at__date=today
        ).count()
        logger.info(f"Mensajes enviados hoy: {count}/{self.campaign.daily_limit}")
        return count
    
    def can_send_more_today(self):
        """Verifica si se pueden enviar más mensajes hoy"""
        daily_sent = self.get_daily_sent_count()
        return daily_sent < self.campaign.daily_limit
    
    def personalize_message(self, message_obj):
        """Personaliza el mensaje para un paciente específico"""
        template = self.campaign.message_template
        patient = message_obj.patient
        promotion = self.campaign.promotion
        
        # Variables disponibles
        variables = {
            'name': patient.full_name.split()[0],  # Primer nombre
            'full_name': patient.full_name,
            'code': promotion.code,
            'discount': promotion.discount_percentage,
            'category': promotion.get_category_display(),
            'category_emoji': promotion.get_category_display_emoji(),
            'end_date': promotion.end_date.strftime('%d/%m/%Y'),
            'organization': self.campaign.organization.name,
        }
        
        # Reemplazar variables
        message = template.format(**variables)
        
        # Agregar variación aleatoria para evitar mensajes idénticos
        # (WhatsApp puede detectar spam si todos los mensajes son iguales)
        import random
        variations = [
            "",
            " 😊",
            " 👍",
            " ✨",
        ]
        message += random.choice(variations)
        
        return message
    
    def send_single_message(self, message_obj):
        """Envía un mensaje individual"""
        try:
            # Personalizar mensaje
            personalized_message = self.personalize_message(message_obj)
            message_obj.message_text = personalized_message
            
            # Enviar vía WhatsApp
            result = self.client.send_message(
                self.org_id,
                message_obj.phone_number,
                personalized_message
            )
            
            if result and result.get('success'):
                # Éxito
                message_obj.status = 'sent'
                message_obj.sent_at = timezone.now()
                message_obj.save()
                
                # Actualizar estadísticas
                self.campaign.messages_sent += 1
                self.campaign.save()
                
                logger.info(f"✅ Mensaje enviado a {message_obj.patient.full_name}")
                return True
            else:
                # Falló
                message_obj.status = 'failed'
                message_obj.error_message = result.get('error', 'Error desconocido')
                message_obj.send_attempts += 1
                message_obj.save()
                
                # Actualizar estadísticas
                self.campaign.messages_failed += 1
                self.campaign.save()
                
                logger.error(f"❌ Error enviando a {message_obj.patient.full_name}: {message_obj.error_message}")
                return False
                
        except Exception as e:
            message_obj.status = 'failed'
            message_obj.error_message = str(e)
            message_obj.send_attempts += 1
            message_obj.save()
            
            # Actualizar estadísticas
            self.campaign.messages_failed += 1
            self.campaign.save()
            
            logger.error(f"❌ Excepción enviando a {message_obj.patient.full_name}: {e}")
            return False
    
    def process_batch(self, batch_size=None):
        """Procesa un lote de mensajes pendientes"""
        if batch_size is None:
            batch_size = self.campaign.daily_limit
        
        # Verificaciones previas
        if not self.is_sending_allowed():
            logger.warning("No está permitido enviar en este momento")
            return 0
        
        if not self.check_whatsapp_connection():
            logger.error("WhatsApp no está conectado")
            return 0
        
        if not self.can_send_more_today():
            logger.info("Se alcanzó el límite diario de envíos")
            return 0
        
        # Calcular cuántos mensajes se pueden enviar
        daily_sent = self.get_daily_sent_count()
        remaining_today = self.campaign.daily_limit - daily_sent
        actual_batch_size = min(batch_size, remaining_today)
        
        # Obtener mensajes pendientes
        pending_messages = PromotionMessage.objects.filter(
            campaign=self.campaign,
            status='pending'
        ).order_by('created_at')[:actual_batch_size]
        
        sent_count = 0
        
        logger.info(f"Procesando lote de {pending_messages.count()} mensajes...")
        
        for message_obj in pending_messages:
            # Verificar nuevamente el límite antes de cada envío
            if not self.can_send_more_today():
                logger.info("Límite diario alcanzado durante el lote")
                break
            
            # Enviar mensaje
            success = self.send_single_message(message_obj)
            
            if success:
                sent_count += 1
            
            # Delay entre mensajes (simular comportamiento humano)
            if message_obj != pending_messages.last():
                delay = self.campaign.delay_seconds
                logger.info(f"Esperando {delay} segundos antes del siguiente mensaje...")
                time.sleep(delay)
        
        logger.info(f"Lote completado: {sent_count} mensajes enviados")
        
        # Actualizar estado de la campaña
        self.campaign.update_stats()
        
        # Si no hay más mensajes pendientes, marcar como completada
        if not PromotionMessage.objects.filter(campaign=self.campaign, status='pending').exists():
            self.campaign.status = 'completed'
            self.campaign.completed_at = timezone.now()
            self.campaign.save()
            logger.info(f"🎉 Campaña '{self.campaign.name}' completada")
        
        return sent_count
    
    def retry_failed_messages(self):
        """Reintenta enviar mensajes fallidos"""
        failed_messages = PromotionMessage.objects.filter(
            campaign=self.campaign,
            status='failed'
        ).filter(send_attempts__lt=3)
        
        logger.info(f"Reintentando {failed_messages.count()} mensajes fallidos...")
        
        # Cambiar estado a pendiente para que se reintenten
        for msg in failed_messages:
            msg.status = 'pending'
            msg.save()
        
        # Procesar
        return self.process_batch()


def create_campaign_messages(campaign):
    """Crea los mensajes individuales para una campaña"""
    logger.info(f"Creando mensajes para campaña '{campaign.name}'...")
    
    # Obtener destinatarios según filtro
    recipients = campaign.get_recipients()
    
    created_count = 0
    
    with transaction.atomic():
        for patient in recipients:
            # Crear mensaje
            PromotionMessage.objects.create(
                campaign=campaign,
                patient=patient,
                phone_number=patient.phone_number,
                status='pending'
            )
            created_count += 1
        
        # Actualizar totales
        campaign.total_recipients = created_count
        campaign.messages_pending = created_count
        campaign.save()
    
    logger.info(f"✅ {created_count} mensajes creados")
    
    return created_count


def start_campaign(campaign_id):
    """Inicia una campaña de envío"""
    try:
        campaign = PromotionCampaign.objects.get(id=campaign_id)
        
        # Verificar que esté en estado correcto
        if campaign.status not in ['scheduled', 'draft']:
            logger.error(f"La campaña está en estado '{campaign.status}', no se puede iniciar")
            return False
        
        # Crear mensajes si no existen
        if campaign.messages.count() == 0:
            create_campaign_messages(campaign)
        
        # Cambiar estado
        campaign.status = 'in_progress'
        campaign.started_at = timezone.now()
        campaign.save()
        
        logger.info(f"🚀 Campaña '{campaign.name}' iniciada")
        
        # Enviar primer lote
        sender = CampaignSender(campaign)
        sent = sender.process_batch()
        
        logger.info(f"Primer lote: {sent} mensajes enviados")
        
        return True
        
    except PromotionCampaign.DoesNotExist:
        logger.error(f"Campaña {campaign_id} no encontrada")
        return False
    except Exception as e:
        logger.error(f"Error iniciando campaña: {e}")
        return False


def process_pending_campaigns():
    """
    Procesa campañas pendientes (para ejecutar en cron job)
    Ejecutar cada hora durante horario laboral
    """
    # Buscar campañas en progreso
    campaigns = PromotionCampaign.objects.filter(status='in_progress')
    
    logger.info(f"Procesando {campaigns.count()} campañas en progreso...")
    
    for campaign in campaigns:
        sender = CampaignSender(campaign)
        
        # Verificar si se puede enviar ahora
        if sender.is_sending_allowed() and sender.can_send_more_today():
            sent = sender.process_batch()
            logger.info(f"Campaña '{campaign.name}': {sent} mensajes enviados")
        else:
            logger.info(f"Campaña '{campaign.name}': No se puede enviar ahora")
    
    return True
