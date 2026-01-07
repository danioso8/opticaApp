"""
Configuración de signals para Appointments
"""
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from apps.appointments.models import Appointment
from apps.appointments.signals import notify_new_appointment
from apps.appointments.notifications import notify_appointment_cancelled, notify_appointment_rescheduled
import logging

logger = logging.getLogger(__name__)

# Variable temporal para guardar el estado anterior
_appointment_old_state = {}


@receiver(pre_save, sender=Appointment)
def appointment_pre_save(sender, instance, **kwargs):
    """Signal antes de guardar - captura el estado anterior"""
    if instance.pk:  # Solo si ya existe
        try:
            old = Appointment.objects.get(pk=instance.pk)
            _appointment_old_state[instance.pk] = {
                'status': old.status,
                'appointment_date': old.appointment_date,
                'appointment_time': old.appointment_time,
            }
        except Appointment.DoesNotExist:
            pass


@receiver(post_save, sender=Appointment)
def appointment_post_save(sender, instance, created, **kwargs):
    """Signal que se ejecuta después de guardar una cita"""
    if created:
        logger.info(f"🔔 Signal: Nueva cita creada #{instance.id}")
        notify_new_appointment(instance)
    else:
        logger.info(f"📝 Signal: Cita actualizada #{instance.id}")
        
        # Verificar si se canceló
        old_state = _appointment_old_state.get(instance.pk)
        if old_state:
            # Detectar cancelación
            if old_state['status'] != 'cancelled' and instance.status == 'cancelled':
                logger.info(f"❌ Signal: Cita cancelada #{instance.id}")
                notify_appointment_cancelled(instance)
            
            # Detectar reagendamiento (cambio de fecha u hora)
            elif (old_state['appointment_date'] != instance.appointment_date or 
                  old_state['appointment_time'] != instance.appointment_time):
                logger.info(f"🔄 Signal: Cita reagendada #{instance.id}")
                notify_appointment_rescheduled(
                    instance, 
                    old_state['appointment_date'], 
                    old_state['appointment_time']
                )
            
            # Limpiar estado temporal
            del _appointment_old_state[instance.pk]

