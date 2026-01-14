# Generated manually - 14 Jan 2026

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('organizations', '0001_initial'),
        ('dashboard', '0012_auto_06ene2026'),  # Ajustar según la última migración
    ]

    operations = [
        migrations.CreateModel(
            name='SidebarCustomization',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('config', models.JSONField(default=dict, help_text='Configuración del sidebar en formato JSON')),
                ('version', models.IntegerField(default=1, help_text='Versión de la configuración')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sidebar_customizations', to='organizations.organization')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='sidebar_customizations', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Personalización de Sidebar',
                'verbose_name_plural': 'Personalizaciones de Sidebar',
                'ordering': ['-updated_at'],
                'unique_together': {('user', 'organization')},
            },
        ),
    ]
