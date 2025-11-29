import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
from django.utils import timezone


class AppointmentsConsumer(AsyncWebsocketConsumer):
    """
    WebSocket consumer para actualizaciones en tiempo real de citas
    """
    
    async def connect(self):
        """Cuando un cliente se conecta"""
        self.room_group_name = 'appointments'
        
        # Join room group
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        
        await self.accept()
        
        # Enviar mensaje de bienvenida
        await self.send(text_data=json.dumps({
            'type': 'connection_established',
            'message': 'Conectado al sistema de citas en tiempo real'
        }))
    
    async def disconnect(self, close_code):
        """Cuando un cliente se desconecta"""
        # Leave room group
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
    
    async def receive(self, text_data):
        """Recibir mensaje del cliente"""
        text_data_json = json.loads(text_data)
        message_type = text_data_json.get('type')
        
        # Aquí puedes manejar diferentes tipos de mensajes del cliente
        if message_type == 'ping':
            await self.send(text_data=json.dumps({
                'type': 'pong',
                'timestamp': str(timezone.now())
            }))
    
    # Handlers para eventos desde el grupo
    
    async def new_appointment(self, event):
        """Enviar notificación de nueva cita"""
        await self.send(text_data=json.dumps({
            'type': 'new_appointment',
            'appointment': event['appointment'],
            'message': event['message']
        }))
    
    async def appointment_updated(self, event):
        """Enviar notificación de cita actualizada"""
        await self.send(text_data=json.dumps({
            'type': 'appointment_updated',
            'appointment': event['appointment'],
            'message': event['message']
        }))
    
    async def appointment_cancelled(self, event):
        """Enviar notificación de cita cancelada"""
        await self.send(text_data=json.dumps({
            'type': 'appointment_cancelled',
            'appointment_id': event['appointment_id'],
            'message': event['message']
        }))
    
    async def system_toggled(self, event):
        """Enviar notificación de cambio en estado del sistema"""
        await self.send(text_data=json.dumps({
            'type': 'system_toggled',
            'is_open': event['is_open'],
            'message': event['message']
        }))
