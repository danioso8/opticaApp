#!/usr/bin/env python
"""
Script para actualizar mensajes por defecto de WhatsApp en todas las organizaciones
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.appointments.models_notifications import NotificationSettings

# Mensajes por defecto mejorados
DEFAULT_MESSAGES = {
    'confirmation_message_template': '''✅ CITA CONFIRMADA - {organization}

Hola {patient_name},

Tu cita ha sido agendada exitosamente:

📅 Fecha: {date}
🕒 Hora: {time}
👤 Doctor: {doctor}

⏰ Por favor llega {arrival_minutes} minutos antes de tu cita.

Si necesitas cancelar o reagendar, contáctanos con anticipación.

¡Te esperamos! 👓''',

    'reminder_message_template': '''⏰ RECORDATORIO DE CITA - {organization}

Hola {patient_name},

Te recordamos tu cita programada para mañana:

📅 Fecha: {date}
🕒 Hora: {time}
👤 Doctor: {doctor}

⏰ Recuerda llegar {arrival_minutes} minutos antes.

Si no puedes asistir, por favor contáctanos lo antes posible para reagendar.

¡Nos vemos pronto! 👓''',

    'cancellation_message_template': '''❌ CITA CANCELADA - {organization}

Hola {patient_name},

Lamentamos informarte que tu cita ha sido cancelada:

📅 Fecha: {date}
🕒 Hora: {time}

Si deseas reagendar tu cita, por favor contáctanos.

Gracias por tu comprensión. 👓''',

    'rescheduled_message_template': '''🔄 CITA REAGENDADA - {organization}

Hola {patient_name},

Tu cita ha sido reagendada exitosamente:

📅 Nueva Fecha: {date}
🕒 Nueva Hora: {time}
👤 Doctor: {doctor}

⏰ Por favor llega {arrival_minutes} minutos antes de tu cita.

Si necesitas hacer algún cambio adicional, contáctanos.

¡Te esperamos! 👓'''
}

def update_messages():
    """Actualizar mensajes en todas las configuraciones"""
    print("=" * 70)
    print("🔄 ACTUALIZANDO MENSAJES DE WHATSAPP")
    print("=" * 70)
    print()
    
    # Obtener todas las configuraciones
    all_settings = NotificationSettings.objects.all()
    
    if not all_settings.exists():
        print("⚠️  No hay configuraciones de notificaciones en el sistema")
        print()
        print("Creando configuración global por defecto...")
        settings = NotificationSettings.objects.create(
            organization=None,
            **DEFAULT_MESSAGES
        )
        print(f"✅ Configuración global creada")
        print()
        return
    
    updated_count = 0
    
    for settings in all_settings:
        org_name = settings.organization.name if settings.organization else "Global"
        print(f"📝 Actualizando: {org_name}")
        
        # Actualizar cada plantilla
        for field_name, default_value in DEFAULT_MESSAGES.items():
            current_value = getattr(settings, field_name, '')
            
            # Solo actualizar si está vacío o tiene el valor antiguo genérico
            if not current_value or len(current_value) < 50:
                setattr(settings, field_name, default_value)
                print(f"   ✅ {field_name.replace('_', ' ').title()}")
        
        settings.save()
        updated_count += 1
        print()
    
    print("=" * 70)
    print(f"📊 RESUMEN:")
    print(f"   ✅ Configuraciones actualizadas: {updated_count}")
    print(f"   📱 Total configuraciones: {all_settings.count()}")
    print()
    print("🎉 ¡Mensajes actualizados correctamente!")
    print("=" * 70)

if __name__ == '__main__':
    update_messages()
