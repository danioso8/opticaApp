# Generated manually on 2025-12-17
from django.db import migrations, connection


def convert_to_varchar(apps, schema_editor):
    """Solo ejecutar en PostgreSQL - SQLite ya maneja esto correctamente"""
    if connection.vendor == 'postgresql':
        with connection.cursor() as cursor:
            cursor.execute("""
                ALTER TABLE patients_clinicalhistory 
                ALTER COLUMN refraction_od_sphere TYPE VARCHAR(10) 
                USING refraction_od_sphere::text;
            """)
            cursor.execute("""
                ALTER TABLE patients_clinicalhistory 
                ALTER COLUMN refraction_os_sphere TYPE VARCHAR(10) 
                USING refraction_os_sphere::text;
            """)


def reverse_convert(apps, schema_editor):
    """Reversión - solo en PostgreSQL"""
    if connection.vendor == 'postgresql':
        with connection.cursor() as cursor:
            cursor.execute("""
                ALTER TABLE patients_clinicalhistory 
                ALTER COLUMN refraction_od_sphere TYPE NUMERIC 
                USING CASE WHEN refraction_od_sphere ~ '^[-+]?[0-9]*\\.?[0-9]+$' 
                      THEN refraction_od_sphere::numeric 
                      ELSE NULL END;
            """)
            cursor.execute("""
                ALTER TABLE patients_clinicalhistory 
                ALTER COLUMN refraction_os_sphere TYPE NUMERIC 
                USING CASE WHEN refraction_os_sphere ~ '^[-+]?[0-9]*\\.?[0-9]+$' 
                      THEN refraction_os_sphere::numeric 
                      ELSE NULL END;
            """)


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0018_convert_sphere_to_charfield'),
    ]

    operations = [
        migrations.RunPython(convert_to_varchar, reverse_convert),
    ]


