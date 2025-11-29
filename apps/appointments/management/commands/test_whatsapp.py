"""
Comando para probar notificaciones de WhatsApp
"""
from django.core.management.base import BaseCommand
from apps.appointments.models import Appointment
from apps.appointments.whatsapp_local import whatsapp_notifier


class Command(BaseCommand):
    help = 'Prueba las notificaciones de WhatsApp'

    def add_arguments(self, parser):
        parser.add_argument(
            '--appointment-id',
            type=int,
            help='ID de la cita para enviar notificación de prueba'
        )
        parser.add_argument(
            '--phone',
            type=str,
            help='Número de teléfono para enviar mensaje de prueba'
        )

    def handle(self, *args, **options):
        appointment_id = options.get('appointment_id')
        phone = options.get('phone')

        # Verificar si el servidor está corriendo
        import requests
        try:
            response = requests.get(f'{whatsapp_notifier.api_url}/status', timeout=2)
            status = response.json()
            
            if not status.get('connected'):
                self.stdout.write(
                    self.style.WARNING('⚠️ WhatsApp Bot no está conectado')
                )
                self.stdout.write(f'Inicia el bot con: cd whatsapp-bot && npm start')
                self.stdout.write(f'Luego ve a: {whatsapp_notifier.api_url}/qr')
                return
            
            self.stdout.write(self.style.SUCCESS('✅ WhatsApp Bot está conectado y listo'))
        except requests.exceptions.ConnectionError:
            self.stdout.write(
                self.style.ERROR('❌ Servidor WhatsApp no está corriendo')
            )
            self.stdout.write('Inicia el bot con:')
            self.stdout.write('  cd whatsapp-bot')
            self.stdout.write('  npm install  (solo la primera vez)')
            self.stdout.write('  npm start')
            self.stdout.write(f'\nLuego ve a: {whatsapp_notifier.api_url}/qr para conectar')
            return

        # Si se proporciona ID de cita
        if appointment_id:
            try:
                appointment = Appointment.objects.get(id=appointment_id)
                self.stdout.write(f'\n📋 Enviando notificación a: {appointment.full_name}')
                self.stdout.write(f'📞 Teléfono: {appointment.phone_number}')
                
                success = whatsapp_notifier.send_appointment_confirmation(appointment)
                
                if success:
                    self.stdout.write(
                        self.style.SUCCESS(f'✅ ¡Notificación enviada exitosamente!')
                    )
                else:
                    self.stdout.write(
                        self.style.ERROR('❌ Error al enviar la notificación')
                    )
                    
            except Appointment.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'❌ No existe una cita con ID {appointment_id}')
                )
            return

        # Si se proporciona un teléfono, crear cita temporal
        if phone:
            from datetime import datetime, timedelta
            from django.utils import timezone
            
            # Crear cita temporal para prueba
            test_date = timezone.now().date() + timedelta(days=1)
            test_time = datetime.strptime('14:00', '%H:%M').time()
            
            test_appointment = Appointment(
                full_name='Cliente de Prueba',
                phone_number=phone,
                appointment_date=test_date,
                appointment_time=test_time,
                status='pending'
            )
            
            self.stdout.write(f'\n📋 Enviando mensaje de prueba a: {phone}')
            success = whatsapp_notifier.send_appointment_confirmation(test_appointment)
            
            if success:
                self.stdout.write(
                    self.style.SUCCESS('✅ ¡Mensaje de prueba enviado!')
                )
            else:
                self.stdout.write(
                    self.style.ERROR('❌ Error al enviar el mensaje')
                )
            return

        # Si no se proporciona nada, mostrar ayuda
        self.stdout.write('\n📖 Uso:')
        self.stdout.write('  python manage.py test_whatsapp --appointment-id 1')
        self.stdout.write('  python manage.py test_whatsapp --phone 3001234567')
        
        # Mostrar citas disponibles
        recent_appointments = Appointment.objects.all().order_by('-id')[:5]
        
        if recent_appointments:
            self.stdout.write('\n📋 Citas recientes disponibles para prueba:')
            for apt in recent_appointments:
                self.stdout.write(
                    f'  ID {apt.id}: {apt.full_name} - {apt.phone_number}'
                )
