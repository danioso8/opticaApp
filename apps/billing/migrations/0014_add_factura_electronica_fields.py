# Generated manually on 2025-12-29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('billing', '0013_alter_dianconfiguration_organization_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='invoice',
            name='es_factura_electronica',
            field=models.BooleanField(
                default=False,
                verbose_name='Es Factura Electrónica',
                help_text='Si es True, consume consecutivo DIAN y se envía ante la DIAN. Si es False, es factura normal/interna.'
            ),
        ),
        migrations.AddField(
            model_name='invoice',
            name='requiere_envio_dian',
            field=models.BooleanField(
                default=False,
                verbose_name='Requiere Envío a DIAN',
                help_text='Indica si el usuario solicitó que esta factura sea enviada a la DIAN'
            ),
        ),
    ]
