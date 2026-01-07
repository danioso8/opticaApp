# Generated migration for WhatsAppUsage model

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0015_add_message_templates'),
        ('organizations', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='WhatsAppUsage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('year', models.IntegerField()),
                ('month', models.IntegerField()),
                ('messages_sent', models.IntegerField(default=0)),
                ('messages_included', models.IntegerField(default=100)),
                ('messages_overage', models.IntegerField(default=0)),
                ('overage_cost', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
                ('cost_per_message', models.DecimalField(decimal_places=4, default=0.02, max_digits=6)),
                ('alert_80_sent', models.BooleanField(default=False)),
                ('alert_100_sent', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now=True)),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='whatsapp_usage', to='organizations.organization')),
            ],
            options={
                'verbose_name': 'Uso de WhatsApp',
                'verbose_name_plural': 'Usos de WhatsApp',
                'ordering': ['-year', '-month'],
                'unique_together': {('organization', 'year', 'month')},
            },
        ),
    ]
