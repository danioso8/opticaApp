# Eliminación en Cascada y Solución de IDs Duplicados

## ✅ Cambios Implementados

### 1. Eliminación en Cascada de Datos Relacionados

Se modificaron los modelos para que cuando se elimine un usuario, **todos sus datos relacionados se eliminen automáticamente**:

#### Modelos Modificados:

**`apps/organizations/models.py`:**
- ✅ `Organization.owner`: `on_delete=models.PROTECT` → `on_delete=models.CASCADE`
  - Al eliminar un usuario, se eliminan TODAS sus organizaciones
  
- ✅ `OrganizationSubscription.plan`: `on_delete=models.PROTECT` → `on_delete=models.CASCADE`
  - Al eliminar un plan, se eliminan todas las suscripciones asociadas

**`apps/sales/models.py`:**
- ✅ `Sale.sold_by`: `on_delete=models.PROTECT` → `on_delete=models.SET_NULL`
  - Al eliminar un usuario vendedor, las ventas se preservan pero el campo se pone en NULL

#### Efecto en Cascada Completo:

Cuando eliminas un **Usuario**, automáticamente se elimina:

```
Usuario (delete)
  └─► Organizaciones (CASCADE)
       ├─► OrganizationMembers (CASCADE)
       ├─► OrganizationSubscriptions (CASCADE)
       ├─► LandingPageConfig (CASCADE)
       ├─► Pacientes (CASCADE)
       │    └─► ClinicalHistory (CASCADE)
       │    └─► Appointments (CASCADE)
       ├─► Productos (CASCADE)
       ├─► Ventas de la organización (CASCADE)
       ├─► Citas (CASCADE)
       └─► Todos los datos de la organización (CASCADE)
```

### 2. Scripts de Mantenimiento Creados

#### 📄 `fix_sequences.py`
**Función:** Resetea TODAS las secuencias de auto-incremento de la base de datos

**Uso:**
```bash
python fix_sequences.py
```

**Cuándo usar:**
- Después de importar datos desde backups
- Cuando aparecen errores de "duplicate key value"
- Después de eliminar muchos registros manualmente

**Soporte:**
- ✅ PostgreSQL
- ✅ SQLite
- ✅ Todas las tablas del sistema

#### 📄 `fix_organization_id.py`
**Función:** Resetea específicamente la secuencia de `organizations_organization`

**Uso:**
```bash
python fix_organization_id.py
```

**Cuándo usar:**
- Error: `duplicate key value violates unique constraint "organizations_organization_pkey"`
- Cuando específicamente falla la creación de organizaciones

**Output esperado:**
```
======================================================================
🔧 RESETEO DE SECUENCIA: organizations_organization
======================================================================

📊 Base de datos: PostgreSQL
  ℹ️  Máximo ID actual: 22
  ✅ Secuencia reseteada al siguiente valor: 23
  ✅ Valor actual de la secuencia: 23

======================================================================
✅ PROCESO COMPLETADO
======================================================================
```

#### 📄 `apps/users/management/commands/delete_user_cascade.py`
**Función:** Elimina un usuario y TODOS sus datos relacionados de forma segura

**Uso:**
```bash
# Con confirmación interactiva
python manage.py delete_user_cascade username_aqui

# Sin confirmación (forzado)
python manage.py delete_user_cascade username_aqui --force

# Simulación (ver qué se eliminaría sin borrar nada)
python manage.py delete_user_cascade username_aqui --dry-run
```

**Ejemplo de output:**
```
======================================================================
ELIMINAR USUARIO: daniel123 (Daniel García)
======================================================================

📊 Datos que serán eliminados:
  • Organizaciones propias: 3
  • Membresías: 5
  • Pacientes: 127
  • Citas: 456
  • Ventas: 89

🏢 Organizaciones:
  • Óptica Central (ID: 1)
  • Óptica Norte (ID: 5)
  • Óptica Sur (ID: 12)

⚠️  ADVERTENCIA: Esta acción NO se puede deshacer
¿Está seguro que desea eliminar este usuario y TODOS sus datos? (escriba "ELIMINAR" para confirmar):
```

### 3. Migraciones Aplicadas

✅ **organizations.0014_cascade_delete_on_user_deletion**
- Cambió `Organization.owner` a CASCADE
- Cambió `OrganizationSubscription.plan` a CASCADE

✅ **sales.0004_cascade_delete_on_user_deletion**
- Cambió `Sale.sold_by` a SET_NULL

✅ **patients.0026_alter_colorvisiontest_organization_and_more**
- Migración pendiente aplicada

## 🔧 Solución al Error de ID Duplicado

### Problema Original:
```
Error al crear organización: duplicate key value violates unique constraint 
"organizations_organization_pkey" 
DETAIL: Key (id)=(1) already exists.
```

### Causa:
La secuencia de auto-incremento en PostgreSQL no estaba sincronizada con el máximo ID en la tabla.

### Solución Aplicada:
1. ✅ Ejecutado `fix_organization_id.py`
2. ✅ Secuencia reseteada de 1 → 23
3. ✅ Ahora las nuevas organizaciones usarán IDs 23, 24, 25...

## 📋 Comandos Útiles

### Resetear secuencias después de backup/restore
```bash
python fix_sequences.py
```

### Verificar secuencia de una tabla específica (PostgreSQL)
```sql
SELECT last_value FROM organizations_organization_id_seq;
SELECT MAX(id) FROM organizations_organization;
```

### Eliminar usuario con todos sus datos
```bash
# Ver qué se eliminaría (simulación)
python manage.py delete_user_cascade username --dry-run

# Eliminar realmente
python manage.py delete_user_cascade username
```

### Verificar relaciones CASCADE en la base de datos
```sql
-- PostgreSQL
SELECT 
    tc.table_name, 
    kcu.column_name, 
    ccu.table_name AS foreign_table_name,
    ccu.column_name AS foreign_column_name,
    rc.delete_rule
FROM information_schema.table_constraints AS tc 
JOIN information_schema.key_column_usage AS kcu
  ON tc.constraint_name = kcu.constraint_name
JOIN information_schema.constraint_column_usage AS ccu
  ON ccu.constraint_name = tc.constraint_name
JOIN information_schema.referential_constraints AS rc
  ON rc.constraint_name = tc.constraint_name
WHERE tc.constraint_type = 'FOREIGN KEY'
  AND tc.table_schema = 'public'
ORDER BY tc.table_name;
```

## ⚠️ Advertencias Importantes

### Eliminación de Usuarios
- ⚠️ **NO SE PUEDE DESHACER**: Una vez eliminado, todos los datos se pierden permanentemente
- ⚠️ Incluye: organizaciones, pacientes, citas, ventas, historias clínicas, productos, etc.
- ✅ Usa `--dry-run` primero para ver qué se eliminaría
- ✅ Haz backup antes de eliminaciones masivas

### Secuencias
- ✅ Ejecuta `fix_sequences.py` después de restaurar backups
- ✅ Si importas datos con IDs específicos, resetea secuencias
- ⚠️ No ejecutes durante alta concurrencia (puede causar locks)

## 🎯 Casos de Uso

### Caso 1: Usuario salió de la empresa
```bash
# 1. Ver qué se eliminaría
python manage.py delete_user_cascade juan.perez --dry-run

# 2. Hacer backup (opcional pero recomendado)
python backup_database.py

# 3. Eliminar usuario y todos sus datos
python manage.py delete_user_cascade juan.perez
```

### Caso 2: Error de ID duplicado al crear organización
```bash
# Ejecutar script de fix
python fix_organization_id.py

# Reintentar crear organización
# Ahora debería funcionar sin error
```

### Caso 3: Después de restaurar backup
```bash
# 1. Restaurar backup
# 2. Resetear todas las secuencias
python fix_sequences.py

# 3. Verificar aplicación
python manage.py runserver
```

## 📊 Estado Actual

✅ Migraciones aplicadas correctamente
✅ Secuencias reseteadas (organization ID: 1 → 23)
✅ Scripts de mantenimiento creados
✅ Eliminación en cascada configurada
✅ Servidor funcionando correctamente

## 🔍 Testing

Para verificar que todo funciona:

```python
# En Django shell
python manage.py shell

from django.contrib.auth.models import User
from apps.organizations.models import Organization

# Crear usuario de prueba
test_user = User.objects.create_user('test_delete', 'test@example.com', 'password123')

# Crear organización
test_org = Organization.objects.create(
    name='Test Org',
    slug='test-org',
    email='test@test.com',
    owner=test_user
)

# Verificar
print(f"Usuario: {test_user.username}")
print(f"Org: {test_org.name}")

# Eliminar usuario (debería eliminar org también)
test_user.delete()

# Verificar que org fue eliminada
print(Organization.objects.filter(slug='test-org').exists())  # False
```

## 📞 Soporte

Si tienes problemas:

1. **Error de ID duplicado**: Ejecuta el script específico
   ```bash
   python fix_organization_id.py
   ```

2. **Múltiples errores de secuencias**: Ejecuta el script general
   ```bash
   python fix_sequences.py
   ```

3. **Verificar eliminación en cascada**: Usa el modo dry-run
   ```bash
   python manage.py delete_user_cascade usuario --dry-run
   ```

---

**Última actualización:** 26 de diciembre de 2025  
**Estado:** ✅ Todos los cambios aplicados y funcionando
