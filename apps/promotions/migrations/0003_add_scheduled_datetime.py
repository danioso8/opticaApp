# Generated migration to add scheduled_datetime field

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('promotions', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='promotioncampaign',
            name='scheduled_datetime',
            field=models.DateTimeField(
                null=True,
                blank=True,
                help_text='Fecha y hora programada de inicio de la campaña'
            ),
        ),
    ]
