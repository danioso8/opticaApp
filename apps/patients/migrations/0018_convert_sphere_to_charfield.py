# Generated manually on 2025-12-17
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0017_fix_clinical_history_fields'),
    ]

    operations = [
        migrations.AlterField(
            model_name='clinicalhistory',
            name='refraction_od_sphere',
            field=models.CharField(blank=True, help_text='Ej: +2.50, -1.25, N', max_length=10, verbose_name='OD Esfera'),
        ),
        migrations.AlterField(
            model_name='clinicalhistory',
            name='refraction_os_sphere',
            field=models.CharField(blank=True, help_text='Ej: +2.50, -1.25, N', max_length=10, verbose_name='OS Esfera'),
        ),
    ]
