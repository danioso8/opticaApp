# Generated migration for Cash Categories

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0001_initial'),
        ('cash_register', '0002_alter_cashmovement_category'),
    ]

    operations = [
        migrations.CreateModel(
            name='CashCategory',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Nombre')),
                ('category_type', models.CharField(choices=[('INCOME', 'Ingreso'), ('EXPENSE', 'Egreso')], max_length=10, verbose_name='Tipo')),
                ('description', models.TextField(blank=True, verbose_name='Descripción')),
                ('is_active', models.BooleanField(default=True, verbose_name='Activa')),
                ('created_at', models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')),
                ('organization', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='cash_categories', to='organizations.organization', verbose_name='Organización')),
            ],
            options={
                'verbose_name': 'Categoría de Caja',
                'verbose_name_plural': 'Categorías de Caja',
                'ordering': ['category_type', 'name'],
                'unique_together': {('organization', 'name', 'category_type')},
            },
        ),
    ]
