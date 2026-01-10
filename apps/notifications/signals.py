"""
Signals para app notifications
"""
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from apps.notifications.models import Notification


# Aquí se pueden agregar signals para:
# - Enviar notificaciones en tiempo real via WebSockets
# - Actualizar contadores de notificaciones no leídas
# - Etc.

# Ejemplo (comentado):
# @receiver(post_save, sender=Notification)
# def send_realtime_notification(sender, instance, created, **kwargs):
#     """Envía notificación en tiempo real via WebSockets"""
#     if created:
#         from channels.layers import get_channel_layer
#         from asgiref.sync import async_to_sync
#         
#         channel_layer = get_channel_layer()
#         async_to_sync(channel_layer.group_send)(
#             f"user_{instance.user.id}",
#             {
#                 "type": "notification_message",
#                 "notification": {
#                     "id": instance.id,
#                     "title": instance.title,
#                     "message": instance.message,
#                     "type": instance.notification_type,
#                 }
#             }
#         )
