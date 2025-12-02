# Generated migration for optics-specific fields

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='patient',
            name='occupation',
            field=models.CharField(blank=True, max_length=200, verbose_name='Ocupación'),
        ),
        migrations.AddField(
            model_name='patient',
            name='residence_area',
            field=models.CharField(blank=True, max_length=200, verbose_name='Zona de Residencia'),
        ),
        migrations.AddField(
            model_name='patient',
            name='business_name',
            field=models.CharField(blank=True, max_length=200, verbose_name='Nombre del Negocio'),
        ),
        migrations.AddField(
            model_name='patient',
            name='business_address',
            field=models.TextField(blank=True, verbose_name='Dirección del Negocio'),
        ),
        migrations.AddField(
            model_name='patient',
            name='business_phone',
            field=models.CharField(blank=True, max_length=20, verbose_name='Teléfono del Negocio'),
        ),
        migrations.AddField(
            model_name='patient',
            name='business_type',
            field=models.CharField(blank=True, max_length=100, verbose_name='Tipo de Negocio'),
        ),
        migrations.AddField(
            model_name='patient',
            name='civil_status',
            field=models.CharField(blank=True, max_length=50, verbose_name='Estado Civil'),
        ),
        migrations.AddField(
            model_name='patient',
            name='bank_entity',
            field=models.CharField(blank=True, max_length=100, verbose_name='Entidad Bancaria'),
        ),
        migrations.AddField(
            model_name='patient',
            name='account_number',
            field=models.CharField(blank=True, max_length=50, verbose_name='Número de Cuenta'),
        ),
    ]
