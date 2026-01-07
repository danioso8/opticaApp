"""
Migración para permitir NULL en campos de refracción
"""
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0023_auto_20251231_2100'),  # Ajusta al número de tu última migración
    ]

    operations = [
        migrations.AlterField(
            model_name='clinicalhistory',
            name='refraction_od_sphere',
            field=models.CharField(blank=True, help_text='Ej: +2.50, -1.25, N/A', max_length=10, null=True, verbose_name='OD Esfera'),
        ),
        migrations.AlterField(
            model_name='clinicalhistory',
            name='refraction_od_prism',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='OD Prisma'),
        ),
        migrations.AlterField(
            model_name='clinicalhistory',
            name='refraction_os_sphere',
            field=models.CharField(blank=True, help_text='Ej: +2.50, -1.25, N/A', max_length=10, null=True, verbose_name='OS Esfera'),
        ),
        migrations.AlterField(
            model_name='clinicalhistory',
            name='refraction_os_prism',
            field=models.CharField(blank=True, max_length=20, null=True, verbose_name='OS Prisma'),
        ),
    ]
