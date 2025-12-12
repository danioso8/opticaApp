# Generated manually to fix constraint issue in Render
from django.db import migrations, models
from django.db.models import Q


def remove_old_constraint(apps, schema_editor):
    """Eliminar el constraint anterior si existe (solo para PostgreSQL)"""
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            cursor.execute("""
                DO $$ 
                BEGIN
                    IF EXISTS (
                        SELECT 1 FROM pg_constraint 
                        WHERE conname = 'unique_active_appointment_slot'
                    ) THEN
                        ALTER TABLE appointments_appointment 
                        DROP CONSTRAINT unique_active_appointment_slot;
                    END IF;
                    
                    -- También intentar eliminar el unique_together anterior
                    IF EXISTS (
                        SELECT 1 FROM pg_constraint 
                        WHERE conname = 'appointments_appointment_organization_id_appointm_3be4b45c_uniq'
                    ) THEN
                        ALTER TABLE appointments_appointment 
                        DROP CONSTRAINT appointments_appointment_organization_id_appointm_3be4b45c_uniq;
                    END IF;
                END $$;
            """)


class Migration(migrations.Migration):

    dependencies = [
        ('appointments', '0008_auto_20251211_1943'),
    ]

    operations = [
        # Primero, ejecutar función Python para limpiar constraints
        migrations.RunPython(remove_old_constraint, migrations.RunPython.noop),
        
        # Eliminar unique_together (esto no falla si no existe)
        migrations.AlterUniqueTogether(
            name='appointment',
            unique_together=set(),
        ),
        
        # Ahora crear el constraint nuevo
        migrations.AddConstraint(
            model_name='appointment',
            constraint=models.UniqueConstraint(
                condition=~Q(status='cancelled'),
                fields=('organization', 'appointment_date', 'appointment_time'),
                name='unique_active_appointment_slot'
            ),
        ),
    ]
