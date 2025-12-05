# Solución para Error de Migración en Render

## Error
```
django.db.utils.OperationalError: cannot ALTER TABLE "patients_clinicalhistory" because it has pending trigger events
```

## Causa
PostgreSQL en Render está bloqueando la alteración de la tabla porque hay eventos trigger activos.

## Soluciones

### Opción 1: Marcar migración como aplicada (RECOMENDADO)
Si los cambios de la migración ya están en la base de datos:

```bash
# En Render Shell
python manage.py migrate patients 0015_auto_20251205_1231 --fake
```

### Opción 2: Rollback y reaplicar
```bash
# 1. Volver a la migración anterior
python manage.py migrate patients 0014

# 2. Aplicar nuevamente
python manage.py migrate patients 0015
```

### Opción 3: Ejecutar con run-syncdb
```bash
python manage.py migrate --run-syncdb
```

### Opción 4: Verificar y limpiar
```bash
# 1. Ver estado actual
python manage.py showmigrations patients

# 2. Si está bloqueada, usar fake
python manage.py migrate patients --fake

# 3. Intentar de nuevo
python manage.py migrate
```

## Pasos en Render

1. **Ir a tu servicio en Render**
2. **Abrir Shell** (botón "Shell" en el dashboard)
3. **Ejecutar:**
   ```bash
   cd /opt/render/project/src
   python manage.py showmigrations patients
   ```
4. **Si ves que 0015 NO tiene [X], ejecuta:**
   ```bash
   python manage.py migrate patients 0015_auto_20251205_1231 --fake
   ```
5. **Reinicia el servicio**

## Prevención
Para evitar este problema en el futuro, considera:
- Hacer migraciones más pequeñas
- Probar migraciones en staging antes de producción
- Usar `--fake-initial` cuando sea apropiado

## Verificación
Después de aplicar la solución:
```bash
python manage.py showmigrations patients
# Deberías ver [X] junto a 0015_auto_20251205_1231
```
