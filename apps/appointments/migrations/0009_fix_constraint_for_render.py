# Generated manually to fix constraint issue in Render
from django.db import migrations, models
from django.db.models import Q


def remove_old_constraints(apps, schema_editor):
    """Eliminar constraints anteriores si existen (solo para PostgreSQL)"""
    if schema_editor.connection.vendor == 'postgresql':
        with schema_editor.connection.cursor() as cursor:
            # Eliminar el constraint nuevo si existe (de intentos anteriores)
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
                END $$;
            """)
            
            # Eliminar el unique_together anterior si existe
            cursor.execute("""
                DO $$ 
                BEGIN
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
        # Primero limpiar constraints en la base de datos
        migrations.RunPython(remove_old_constraints, migrations.RunPython.noop),
        
        # Separar estado y base de datos para evitar errores
        migrations.SeparateDatabaseAndState(
            state_operations=[
                # Esto solo actualiza el estado de Django
                migrations.AlterUniqueTogether(
                    name='appointment',
                    unique_together=set(),
                ),
            ],
            database_operations=[
                # La base de datos ya se limpió arriba
            ],
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
