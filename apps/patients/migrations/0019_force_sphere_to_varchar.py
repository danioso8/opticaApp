# Generated manually on 2025-12-17
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('patients', '0018_convert_sphere_to_charfield'),
    ]

    operations = [
        # Paso 1: Cambiar el tipo con conversión explícita usando SQL raw
        migrations.RunSQL(
            # Forward: convertir de numeric a varchar
            sql=[
                "ALTER TABLE patients_clinicalhistory ALTER COLUMN refraction_od_sphere TYPE VARCHAR(10) USING refraction_od_sphere::text;",
                "ALTER TABLE patients_clinicalhistory ALTER COLUMN refraction_os_sphere TYPE VARCHAR(10) USING refraction_os_sphere::text;",
            ],
            # Reverse: volver a numeric (opcional)
            reverse_sql=[
                "ALTER TABLE patients_clinicalhistory ALTER COLUMN refraction_od_sphere TYPE NUMERIC USING CASE WHEN refraction_od_sphere ~ '^[-+]?[0-9]*\\.?[0-9]+$' THEN refraction_od_sphere::numeric ELSE NULL END;",
                "ALTER TABLE patients_clinicalhistory ALTER COLUMN refraction_os_sphere TYPE NUMERIC USING CASE WHEN refraction_os_sphere ~ '^[-+]?[0-9]*\\.?[0-9]+$' THEN refraction_os_sphere::numeric ELSE NULL END;",
            ]
        ),
    ]
