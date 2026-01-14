# -*- coding: utf-8 -*-
"""
Servicios de notificación para el sistema de trials y módulos
"""
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
from apps.organizations.models import SubscriptionNotification
import requests
import logging

logger = logging.getLogger(__name__)


class TrialNotificationService:
    """Servicio centralizado para envío de notificaciones de trial"""
    
    WHATSAPP_API_URL = getattr(settings, 'LANDING_WHATSAPP_API_URL', 'http://localhost:3000')
    WHATSAPP_NUMBER = getattr(settings, 'LANDING_WHATSAPP_NUMBER', '+573123456789')
    FROM_EMAIL = getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@optikaapp.com')
    
    @staticmethod
    def send_trial_welcome(organization):
        """Enviar notificación de bienvenida (Día 0)"""
        user = organization.owner
        
        # Email
        subject = f"¡Bienvenido a OpticaApp! - 30 días GRATIS"
        context = {
            'organization': organization,
            'user': user,
            'days': 30,
        }
        
        html_message = render_to_string('emails/trial_welcome.html', context)
        
        try:
            send_mail(
                subject=subject,
                message=f"Bienvenido {user.first_name}! Tu prueba de 30 días ha comenzado.",
                from_email=TrialNotificationService.FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            SubscriptionNotification.objects.create(
                organization=organization,
                notification_type='trial_welcome',
                channel='email',
                recipient_email=user.email,
                subject=subject,
                message=html_message,
                delivered=True,
            )
            
            logger.info(f"Email de bienvenida enviado a {user.email}")
        except Exception as e:
            logger.error(f"Error enviando email de bienvenida: {str(e)}")
        
        # WhatsApp
        message = f"""
🎉 *¡Bienvenido a OpticaApp!*

Hola {user.first_name},

✨ Tu prueba de *30 días GRATIS* ha comenzado
✅ Todos los módulos desbloqueados
✅ Sin límites

Accede aquí: https://www.optikaapp.com

¿Necesitas ayuda? Estamos aquí 😊
"""
        
        TrialNotificationService._send_whatsapp(organization, user, message, 'trial_welcome')
    
    @staticmethod
    def send_trial_day20(organization, trial_status):
        """Día 20: Recordatorio suave (10 días restantes)"""
        user = organization.owner
        
        subject = "10 días restantes de tu prueba - ¿Qué te ha parecido?"
        context = {
            'organization': organization,
            'user': user,
            'days_remaining': 10,
            'trial_status': trial_status,
        }
        
        html_message = render_to_string('emails/trial_day20.html', context)
        
        try:
            send_mail(
                subject=subject,
                message=f"Te quedan 10 días de prueba gratuita.",
                from_email=TrialNotificationService.FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            SubscriptionNotification.objects.create(
                organization=organization,
                notification_type='trial_day20',
                channel='email',
                recipient_email=user.email,
                subject=subject,
                message=html_message,
                delivered=True,
            )
        except Exception as e:
            logger.error(f"Error enviando email día 20: {str(e)}")
    
    @staticmethod
    def send_trial_day25(organization, trial_status):
        """Día 25: Recordatorio + Insights (5 días restantes)"""
        user = organization.owner
        
        # Obtener estadísticas de uso
        most_used = trial_status.most_used_modules or {}
        
        subject = "⏰ 5 días restantes - Tus estadísticas de uso"
        context = {
            'organization': organization,
            'user': user,
            'days_remaining': 5,
            'trial_status': trial_status,
            'most_used_modules': most_used,
        }
        
        html_message = render_to_string('emails/trial_day25.html', context)
        
        try:
            send_mail(
                subject=subject,
                message=f"Te quedan 5 días. Mira tus estadísticas de uso.",
                from_email=TrialNotificationService.FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            SubscriptionNotification.objects.create(
                organization=organization,
                notification_type='trial_day25',
                channel='email',
                recipient_email=user.email,
                subject=subject,
                message=html_message,
                delivered=True,
            )
        except Exception as e:
            logger.error(f"Error enviando email día 25: {str(e)}")
        
        # WhatsApp con estadísticas
        modules_text = "\n".join([f"✅ {k}: {v} veces" for k, v in list(most_used.items())[:3]])
        message = f"""
⏰ *Tu prueba termina en 5 días*

Hola {user.first_name},

📊 Mira lo que lograste:
{modules_text}

💡 Selecciona tu plan personalizado y sigue creciendo

Ver planes: https://www.optikaapp.com/dashboard/modules/select/
"""
        
        TrialNotificationService._send_whatsapp(organization, user, message, 'trial_day25')
    
    @staticmethod
    def send_trial_day28(organization):
        """Día 28: Urgencia moderada (2 días restantes)"""
        user = organization.owner
        
        subject = "🚨 Solo 2 días para elegir tu plan"
        context = {
            'organization': organization,
            'user': user,
            'days_remaining': 2,
        }
        
        html_message = render_to_string('emails/trial_day28.html', context)
        
        try:
            send_mail(
                subject=subject,
                message="Solo quedan 2 días de tu prueba gratuita.",
                from_email=TrialNotificationService.FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            SubscriptionNotification.objects.create(
                organization=organization,
                notification_type='trial_day28',
                channel='email',
                recipient_email=user.email,
                subject=subject,
                message=html_message,
                delivered=True,
            )
        except Exception as e:
            logger.error(f"Error enviando email día 28: {str(e)}")
    
    @staticmethod
    def send_trial_expired(organization):
        """Día 30: Trial expirado"""
        user = organization.owner
        
        subject = "Tu período de prueba ha terminado - Elige tu plan"
        context = {
            'organization': organization,
            'user': user,
        }
        
        html_message = render_to_string('emails/trial_expired.html', context)
        
        try:
            send_mail(
                subject=subject,
                message="Tu prueba ha terminado. Elige tu plan para continuar.",
                from_email=TrialNotificationService.FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            SubscriptionNotification.objects.create(
                organization=organization,
                notification_type='trial_expired',
                channel='email',
                recipient_email=user.email,
                subject=subject,
                message=html_message,
                delivered=True,
            )
        except Exception as e:
            logger.error(f"Error enviando email trial expirado: {str(e)}")
        
        message = f"""
⏰ *Tu prueba ha terminado*

Hola {user.first_name},

Tu período de 30 días gratuito ha finalizado.

✨ Elige tu plan personalizado:
💰 Desde $2/mes por módulo
🎁 Descuentos por volumen

Selecciona módulos: https://www.optikaapp.com/dashboard/modules/select/

¡Sigue creciendo con OpticaApp! 🚀
"""
        
        TrialNotificationService._send_whatsapp(organization, user, message, 'trial_expired')
    
    @staticmethod
    def send_grace_reminder(organization):
        """Día 37: Recordatorio en período de gracia"""
        user = organization.owner
        
        subject = "Te extrañamos - Última oportunidad"
        context = {
            'organization': organization,
            'user': user,
        }
        
        html_message = render_to_string('emails/grace_reminder.html', context)
        
        try:
            send_mail(
                subject=subject,
                message="Aún puedes activar tu cuenta. Te extrañamos.",
                from_email=TrialNotificationService.FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            SubscriptionNotification.objects.create(
                organization=organization,
                notification_type='grace_reminder',
                channel='email',
                recipient_email=user.email,
                subject=subject,
                message=html_message,
                delivered=True,
            )
        except Exception as e:
            logger.error(f"Error enviando email de gracia: {str(e)}")
        
        message = f"""
💔 *Te extrañamos*

Hola {user.first_name},

Notamos que aún no has seleccionado tu plan.

⏰ Última oportunidad para mantener tus datos

Activa tu cuenta: https://www.optikaapp.com/dashboard/modules/select/
"""
        
        TrialNotificationService._send_whatsapp(organization, user, message, 'grace_reminder')
    
    @staticmethod
    def send_archive_warning(organization):
        """Día 45: Advertencia de archivo"""
        user = organization.owner
        
        subject = "⚠️ URGENTE: Tus datos serán archivados pronto"
        context = {
            'organization': organization,
            'user': user,
            'days_until_archive': 45,
        }
        
        html_message = render_to_string('emails/archive_warning.html', context)
        
        try:
            send_mail(
                subject=subject,
                message="URGENTE: Tus datos serán archivados en 45 días.",
                from_email=TrialNotificationService.FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            
            SubscriptionNotification.objects.create(
                organization=organization,
                notification_type='archive_warning',
                channel='email',
                recipient_email=user.email,
                subject=subject,
                message=html_message,
                delivered=True,
            )
        except Exception as e:
            logger.error(f"Error enviando advertencia de archivo: {str(e)}")
    
    @staticmethod
    def _send_whatsapp(organization, user, message, notification_type):
        """Enviar mensaje por WhatsApp vía servidor Baileys"""
        try:
            # Obtener número de teléfono del usuario
            phone = getattr(user, 'phone', None)
            if not phone and hasattr(organization, 'phone'):
                phone = organization.phone
            
            if not phone:
                logger.warning(f"No hay número de teléfono para {organization.name}")
                return
            
            # Formatear número
            phone_clean = ''.join(filter(str.isdigit, str(phone)))
            if not phone_clean.startswith('57'):
                phone_clean = '57' + phone_clean
            
            # Enviar vía API de WhatsApp
            response = requests.post(
                f"{TrialNotificationService.WHATSAPP_API_URL}/send-message",
                json={
                    'phone': phone_clean,
                    'message': message,
                },
                timeout=10
            )
            
            if response.status_code == 200:
                SubscriptionNotification.objects.create(
                    organization=organization,
                    notification_type=notification_type,
                    channel='whatsapp',
                    recipient_phone=phone_clean,
                    message=message,
                    delivered=True,
                )
                logger.info(f"WhatsApp enviado a {phone_clean}")
            else:
                logger.error(f"Error enviando WhatsApp: {response.status_code}")
                
        except Exception as e:
            logger.error(f"Error en _send_whatsapp: {str(e)}")
