# Generated manually on 2025-12-29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('organizations', '0020_add_schedule_fields_to_landing_config'),
    ]

    operations = [
        # Campos de descripción y marketing
        migrations.AddField(
            model_name='subscriptionplan',
            name='coverage_description',
            field=models.TextField(blank=True, help_text='Describe qué tipo de negocio es ideal para este plan. Ej: "Perfecto para ópticas pequeñas en crecimiento"', verbose_name='Descripción de Cobertura'),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='ideal_for',
            field=models.CharField(blank=True, help_text='Target del plan. Ej: "Ópticas pequeñas con 2-3 empleados"', max_length=200, verbose_name='Ideal Para'),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='plan_badge',
            field=models.CharField(blank=True, help_text='Ej: "MÁS POPULAR", "RECOMENDADO", "MEJOR VALOR"', max_length=50, verbose_name='Etiqueta/Badge'),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='highlighted_features',
            field=models.TextField(blank=True, help_text='Lista de características principales, una por línea. Estas se mostrarán como bullets.', verbose_name='Características Destacadas'),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='main_benefits',
            field=models.TextField(blank=True, help_text='Beneficios clave del plan, uno por línea', verbose_name='Beneficios Principales'),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='additional_features',
            field=models.TextField(blank=True, help_text='Otras características no listadas en los campos booleanos, una por línea', verbose_name='Características Adicionales'),
        ),
        
        # Landing page
        migrations.AddField(
            model_name='subscriptionplan',
            name='includes_landing_page',
            field=models.BooleanField(default=True, help_text='Todos los planes incluyen landing page personalizable', verbose_name='Incluye Landing Page'),
        ),
        
        # Campos para límites ilimitados
        migrations.AddField(
            model_name='subscriptionplan',
            name='unlimited_storage',
            field=models.BooleanField(default=False, help_text='Si está activo, ignora el límite de max_storage_mb', verbose_name='Almacenamiento Ilimitado'),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='unlimited_users',
            field=models.BooleanField(default=False, help_text='Si está activo, ignora max_users', verbose_name='Usuarios Ilimitados'),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='unlimited_appointments',
            field=models.BooleanField(default=False, help_text='Si está activo, ignora max_appointments_month', verbose_name='Citas Ilimitadas'),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='unlimited_patients',
            field=models.BooleanField(default=False, help_text='Si está activo, ignora max_patients', verbose_name='Pacientes Ilimitados'),
        ),
        migrations.AddField(
            model_name='subscriptionplan',
            name='unlimited_organizations',
            field=models.BooleanField(default=False, help_text='Si está activo, ignora max_organizations', verbose_name='Organizaciones Ilimitadas'),
        ),
    ]
