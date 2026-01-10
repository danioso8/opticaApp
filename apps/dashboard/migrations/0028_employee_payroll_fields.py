# Generated migration for adding payroll fields to Employee model

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dashboard', '0010_delete_auditlog'),
    ]

    operations = [
        migrations.AddField(
            model_name='employee',
            name='incluir_en_nomina',
            field=models.BooleanField(
                default=False,
                help_text='Si está activado, este empleado aparecerá en el módulo de nómina electrónica',
                verbose_name='Incluir en Nómina'
            ),
        ),
        migrations.AddField(
            model_name='employee',
            name='ciudad',
            field=models.CharField(
                blank=True,
                default='Bogotá',
                max_length=100,
                verbose_name='Ciudad'
            ),
        ),
        migrations.AddField(
            model_name='employee',
            name='departamento_ubicacion',
            field=models.CharField(
                blank=True,
                default='Cundinamarca',
                max_length=100,
                verbose_name='Departamento/Estado'
            ),
        ),
    ]
