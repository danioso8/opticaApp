# Generated migration for WhatsApp usage limits

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0023_alter_organizationmember_role'),
    ]

    operations = [
        migrations.AddField(
            model_name='subscriptionplan',
            name='whatsapp_messages_included',
            field=models.IntegerField(default=100, help_text='Mensajes WhatsApp incluidos en el plan. 0 = ilimitado (Enterprise)', verbose_name='Mensajes WhatsApp Incluidos/Mes'),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='whatsapp_overage_price',
            field=models.DecimalField(decimal_places=3, default=0.02, help_text='Precio en USD por cada mensaje WhatsApp que exceda el límite incluido', max_digits=6, verbose_name='Precio por Mensaje Adicional'),
        ),
    ]
