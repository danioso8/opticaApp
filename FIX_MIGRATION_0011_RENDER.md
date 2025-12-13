# Solución: Error de Migración 0011 en Render

## Problema
```
psycopg2.errors.DuplicateColumn: la columna "companion_name" de la relación "appointments_appointment" ya existe
```

Las columnas de acompañante ya existen en la base de datos de Render, pero Django no tiene registrada la migración 0011 que las creó.

## Solución: Marcar la migración como aplicada (fake)

### Opción 1: Usando el script Python (Recomendado)

1. En **Render Shell**, ejecuta:
```bash
python manage.py shell < fake_migration_0011_render.py
```

2. Si todo sale bien, ejecuta las migraciones restantes:
```bash
python manage.py migrate
```

### Opción 2: Comando directo

En **Render Shell**:
```bash
python manage.py migrate appointments 0011_appointment_companion_name_and_more --fake
python manage.py migrate
```

### Opción 3: Script manual en Shell

Abre **Render Shell** y pega este código:

```python
from django.db import connection
from django.db.migrations.recorder import MigrationRecorder

# Verificar columnas
with connection.cursor() as cursor:
    cursor.execute("""
        SELECT column_name 
        FROM information_schema.columns 
        WHERE table_name='appointments_appointment' 
        AND column_name IN ('companion_name', 'companion_phone', 'companion_relationship', 'has_companion')
    """)
    print(f"Columnas existentes: {[row[0] for row in cursor.fetchall()]}")

# Registrar migración como aplicada
recorder = MigrationRecorder(connection)
recorder.record_applied('appointments', '0011_appointment_companion_name_and_more')
print("✅ Migración marcada como aplicada")
exit()
```

Luego ejecuta:
```bash
python manage.py migrate
```

## Verificación

Después de aplicar la solución, verifica que todo esté correcto:

```bash
python manage.py showmigrations appointments
```

Deberías ver:
```
[X] 0010_appointment_doctor_and_more
[X] 0011_appointment_companion_name_and_more
```

## ¿Por qué pasó esto?

Las columnas de acompañante fueron agregadas directamente en Render (probablemente con una migración anterior o manualmente), pero la tabla `django_migrations` no tiene registrada la migración 0011, causando que Django intente crearlas nuevamente.

## Prevención futura

- Siempre usar `python manage.py makemigrations` en local
- Hacer push de las migraciones al repositorio
- Dejar que Render ejecute automáticamente las migraciones
- NO ejecutar SQL directo en producción sin registrar la migración
