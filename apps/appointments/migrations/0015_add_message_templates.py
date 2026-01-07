# Generated manually
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0014_update_notification_settings_whatsapp'),
    ]

    operations = [
        migrations.AddField(
            model_name='notificationsettings',
            name='reminder_hours_before',
            field=models.IntegerField(
                default=24,
                verbose_name='Horas antes del recordatorio',
                help_text='Cuántas horas antes de la cita enviar recordatorio'
            ),
        ),
        migrations.AddField(
            model_name='notificationsettings',
            name='arrival_minutes_before',
            field=models.IntegerField(
                default=10,
                verbose_name='Minutos de anticipación',
                help_text='Cuántos minutos antes debe llegar el paciente'
            ),
        ),
        migrations.AddField(
            model_name='notificationsettings',
            name='confirmation_message_template',
            field=models.TextField(
                default='✅ CITA CONFIRMADA - {organization}\n\nHola {patient_name},\n\nTu cita ha sido agendada exitosamente:\n\n📅 Fecha: {date}\n🕒 Hora: {time}\n👤 Doctor: {doctor}\n\nLlega {arrival_minutes} minutos antes de tu cita.\n\nSi necesitas cancelar o reagendar, contáctanos con anticipación.\n\n¡Te esperamos! 👓',
                verbose_name='Plantilla de confirmación',
                help_text='Variables: {organization}, {patient_name}, {date}, {time}, {doctor}, {arrival_minutes}'
            ),
        ),
        migrations.AddField(
            model_name='notificationsettings',
            name='reminder_message_template',
            field=models.TextField(
                default='⏰ RECORDATORIO DE CITA - {organization}\n\nHola {patient_name},\n\nTe recordamos tu cita:\n\n📅 Fecha: {date}\n🕒 Hora: {time}\n👤 Doctor: {doctor}\n\nLlega {arrival_minutes} minutos antes de tu cita.\n\nSi no puedes asistir, contáctanos lo antes posible.\n\n¡Nos vemos pronto! 👓',
                verbose_name='Plantilla de recordatorio',
                help_text='Variables: {organization}, {patient_name}, {date}, {time}, {doctor}, {arrival_minutes}'
            ),
        ),
        migrations.AddField(
            model_name='notificationsettings',
            name='cancellation_message_template',
            field=models.TextField(
                default='❌ CITA CANCELADA - {organization}\n\nHola {patient_name},\n\nTu cita ha sido cancelada:\n\n📅 Fecha: {date}\n🕒 Hora: {time}\n\nSi deseas reagendar, contáctanos.\n\nGracias por tu comprensión. 👓',
                verbose_name='Plantilla de cancelación',
                help_text='Variables: {organization}, {patient_name}, {date}, {time}'
            ),
        ),
        migrations.AddField(
            model_name='notificationsettings',
            name='rescheduled_message_template',
            field=models.TextField(
                default='🔄 CITA REAGENDADA - {organization}\n\nHola {patient_name},\n\nTu cita ha sido reagendada:\n\n📅 Nueva Fecha: {date}\n🕒 Nueva Hora: {time}\n👤 Doctor: {doctor}\n\nLlega {arrival_minutes} minutos antes de tu cita.\n\n¡Te esperamos! 👓',
                verbose_name='Plantilla de reagendamiento',
                help_text='Variables: {organization}, {patient_name}, {date}, {time}, {doctor}, {arrival_minutes}'
            ),
        ),
    ]
