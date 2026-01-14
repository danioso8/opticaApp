# Generated migration for WhatsAppConnection model

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organizations', '0025_alter_organization_owner'),
        ('notifications', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WhatsAppConnection',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('phone_number', models.CharField(blank=True, help_text='Número de teléfono vinculado (formato: 573001234567)', max_length=20, null=True, verbose_name='Número de WhatsApp')),
                ('status', models.CharField(choices=[('connected', 'Conectado'), ('disconnected', 'Desconectado'), ('connecting', 'Conectando'), ('qr_ready', 'QR Listo para escanear'), ('error', 'Error')], default='disconnected', max_length=20, verbose_name='Estado')),
                ('session_exists', models.BooleanField(default=False, help_text='Indica si hay archivos de sesión guardados en el servidor', verbose_name='Sesión existe')),
                ('last_connected_at', models.DateTimeField(blank=True, help_text='Última vez que WhatsApp se conectó exitosamente', null=True, verbose_name='Última conexión')),
                ('last_disconnected_at', models.DateTimeField(blank=True, null=True, verbose_name='Última desconexión')),
                ('disconnection_reason', models.CharField(blank=True, help_text='Última razón de desconexión (para diagnóstico)', max_length=200, null=True, verbose_name='Razón de desconexión')),
                ('reconnect_attempts', models.IntegerField(default=0, help_text='Contador de intentos de reconexión automática', verbose_name='Intentos de reconexión')),
                ('last_reconnect_attempt', models.DateTimeField(blank=True, null=True, verbose_name='Último intento de reconexión')),
                ('manually_disconnected', models.BooleanField(default=False, help_text='True si el usuario cerró sesión intencionalmente. Previene reconexión automática.', verbose_name='Desconectado manualmente')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('disconnected_by', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='whatsapp_disconnections', to=settings.AUTH_USER_MODEL, verbose_name='Desconectado por')),
                ('organization', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='whatsapp_connection', to='organizations.Organization', verbose_name='Organización')),
            ],
            options={
                'verbose_name': 'Conexión de WhatsApp',
                'verbose_name_plural': 'Conexiones de WhatsApp',
                'ordering': ['-last_connected_at'],
            },
        ),
    ]
