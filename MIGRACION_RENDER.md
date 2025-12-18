# GUÍA DE MIGRACIÓN A NUEVA CUENTA DE RENDER

## Ventajas del Plan de $19/mes
- ✅ Múltiples proyectos/servicios
- ✅ Más recursos (RAM, CPU)
- ✅ Backups automáticos diarios
- ✅ Sin límite de horas de build
- ✅ Mejor soporte

## PASOS PARA LA MIGRACIÓN

### 1. BACKUP DE LA BASE DE DATOS ACTUAL

#### Opción A: Desde Render Dashboard (Recomendado)
1. Ve a https://dashboard.render.com/
2. Selecciona tu PostgreSQL Database actual
3. Ve a la pestaña **"Backups"**
4. Descarga el backup más reciente
5. Guárdalo como `optica_backup.sql`

#### Opción B: Usando pg_dump
Si tienes PostgreSQL instalado localmente:

```bash
# Obtén la External Database URL de tu BD actual en Render
pg_dump "postgresql://user:password@host:port/database" > optica_backup.sql
```

#### Opción C: Desde Render Shell
1. Ve a tu Web Service en Render
2. Click en **"Shell"** en el menú izquierdo
3. Ejecuta:
```bash
pg_dump $DATABASE_URL > backup.sql
cat backup.sql  # Copiar y guardar localmente
```

### 2. CREAR NUEVA CUENTA/PROYECTO EN RENDER

1. **Nueva cuenta de Render:**
   - Ve a https://render.com/
   - Crea una nueva cuenta con otro email
   - O usa la misma cuenta y crea un nuevo Team

2. **Suscribirse al plan de $19:**
   - Ve a Settings → Billing
   - Selecciona el plan "Starter" ($19/mes)
   - Completa el pago

### 3. CREAR NUEVA BASE DE DATOS POSTGRESQL

1. En el Dashboard de la nueva cuenta
2. Click en **"New +"** → **"PostgreSQL"**
3. Configuración:
   - Name: `opticaapp-db` (o el nombre que prefieras)
   - Region: Same as your web service (recomendado Ohio/US East)
   - PostgreSQL Version: 15 o 16
   - Plan: Según necesites (Starter $7 o superior)
4. Click **"Create Database"**
5. Espera a que se aprovisione (2-3 minutos)

### 4. OBTENER CREDENCIALES DE LA NUEVA BD

1. Una vez creada, ve a la pestaña **"Info"**
2. Copia estas credenciales:
   - **Internal Database URL** (para conectar desde Render)
   - **External Database URL** (para conectar localmente)
   - Hostname
   - Port
   - Database
   - Username
   - Password

### 5. RESTAURAR EL BACKUP EN LA NUEVA BD

#### Opción A: Desde tu máquina local (si tienes psql)
```bash
# Usa la External Database URL de la NUEVA base de datos
psql "postgresql://nuevo_user:nuevo_pass@nuevo_host:port/nuevo_db" < optica_backup.sql
```

#### Opción B: Crear Web Service temporal en Render
1. Crea un nuevo Web Service en la nueva cuenta
2. Conecta tu repositorio de GitHub
3. En Environment Variables, agrega:
   - `DATABASE_URL` = Internal Database URL de la nueva BD
4. En el Shell del Web Service:
```bash
# Subir el backup (puedes usar cat y pegar el contenido)
# O subirlo vía Git en un archivo temporal
psql $DATABASE_URL < backup.sql
```

### 6. CREAR NUEVO WEB SERVICE

1. Click en **"New +"** → **"Web Service"**
2. Conecta tu repositorio de GitHub
3. Configuración:
   - Name: `opticaapp` (o el que prefieras)
   - Region: Same as database
   - Branch: `main`
   - Runtime: `Python 3`
   - Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput`
   - Start Command: `daphne -b 0.0.0.0 -p $PORT config.asgi:application`

### 7. CONFIGURAR VARIABLES DE ENTORNO

En el nuevo Web Service, ve a **"Environment"** y agrega:

```
DATABASE_URL=<Internal Database URL de tu nueva BD>
SECRET_KEY=<tu secret key actual o genera una nueva>
DEBUG=False
ALLOWED_HOSTS=*.onrender.com
DJANGO_SETTINGS_MODULE=config.settings
PYTHONUNBUFFERED=1
WEB_CONCURRENCY=2
```

Para generar un nuevo SECRET_KEY:
```python
python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())"
```

### 8. DEPLOY Y VERIFICACIÓN

1. El deploy se iniciará automáticamente
2. Espera a que complete (5-10 minutos)
3. Una vez desplegado, verifica:
   - Accede a la URL del nuevo servicio
   - Login con tu usuario
   - Verifica que los datos estén presentes
   - Prueba crear/editar registros

### 9. EJECUTAR MIGRACIONES (si es necesario)

Si hay nuevas migraciones pendientes, ve al Shell del Web Service:
```bash
python manage.py migrate
python manage.py createsuperuser  # Solo si no tienes usuarios
```

### 10. ACTUALIZAR DOMINIO (Opcional)

Si tienes un dominio personalizado:
1. Ve a Settings → Custom Domains
2. Agrega tu dominio
3. Actualiza los registros DNS según las instrucciones

## CHECKLIST DE VERIFICACIÓN

- [ ] Backup de BD actual descargado
- [ ] Nueva cuenta de Render creada
- [ ] Plan de $19 activado
- [ ] Nueva BD PostgreSQL creada
- [ ] Backup restaurado en nueva BD
- [ ] Nuevo Web Service creado
- [ ] Variables de entorno configuradas
- [ ] Deploy completado exitosamente
- [ ] Login funciona
- [ ] Datos verificados
- [ ] Funcionalidades probadas

## TIPS IMPORTANTES

1. **No elimines la cuenta antigua** hasta verificar que todo funcione perfectamente en la nueva
2. **Mantén el backup** en un lugar seguro
3. **Documenta las URLs** de ambos servicios durante la transición
4. **Prueba exhaustivamente** antes de hacer el cambio definitivo
5. **Considera mantener la BD antigua** como respaldo por unos días

## ROLLBACK (Si algo sale mal)

Si necesitas volver atrás:
1. La cuenta antigua sigue funcionando
2. Simplemente vuelve a usar la URL antigua
3. Puedes eliminar la nueva cuenta si no la necesitas

## SOPORTE

Si encuentras problemas:
- Render Docs: https://render.com/docs
- Render Community: https://community.render.com/
- Render Support: support@render.com

---

**NOTA:** Este proceso puede tomar entre 30-60 minutos. Planifica hacerlo en un momento de bajo tráfico.
