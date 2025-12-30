# 👥 Sistema de Gestión de Equipo y Permisos

## ✨ Funcionalidad Implementada

He creado un sistema completo de **Multi-usuario con Roles y Permisos Granulares** que permite a los usuarios gestionar su equipo de trabajo y controlar el acceso a diferentes módulos del sistema.

---

## 🎯 Características Principales

### 1. **Gestión de Miembros del Equipo**
- ✅ Agregar nuevos miembros al equipo
- ✅ Invitar usuarios por email (auto-creación de cuenta si no existe)
- ✅ Asignar roles predefinidos
- ✅ Activar/Desactivar miembros
- ✅ Eliminar miembros (solo propietario)
- ✅ Ver lista completa del equipo con estadísticas

### 2. **Sistema de Roles**
Se agregaron 6 roles diferentes:

| Rol | Descripción | Acceso |
|-----|-------------|--------|
| **🔱 Propietario** | Dueño de la organización | Acceso total sin restricciones |
| **👑 Administrador** | Gestor del sistema | Acceso completo + gestión de equipo |
| **👨‍⚕️ Doctor/Optómetra** | Profesional de la salud | Acceso clínico personalizable |
| **👔 Personal** | Staff general | Permisos personalizados |
| **💰 Cajero** | Punto de venta | Acceso a ventas y facturación |
| **👁️ Visualizador** | Solo lectura | Sin permisos de edición |

### 3. **Permisos Granulares por Módulo**
Sistema de permisos a 4 niveles:
- 👁️ **Ver**: Acceso de lectura al módulo
- ➕ **Crear**: Crear nuevos registros
- ✏️ **Editar**: Modificar registros existentes
- 🗑️ **Eliminar**: Borrar registros

### 4. **Módulos del Sistema**
Se crearon **19 módulos** organizados en 6 categorías:

#### 🎯 Núcleo (Core)
- Dashboard
- Citas
- Pacientes

#### 🏥 Médico
- Historia Clínica
- Exámenes Visuales
- Órdenes de Examen
- Doctores

#### 💵 Ventas
- Ventas (POS)
- Facturación (DIAN)
- Cotizaciones

#### 📦 Inventario
- Productos
- Inventario
- Proveedores

#### 📊 Reportes
- Analytics
- Reportes

#### ⚙️ Configuración
- Configuración General
- Gestión de Equipo
- Landing Page
- Notificaciones

---

## 🚀 Cómo Usar

### Acceder a la Gestión de Equipo

1. **Ubicación en el Dashboard:**
   - Sidebar → Configuración → **Gestión de Equipo**
   - Ruta directa: `/dashboard/team/`

2. **Permisos necesarios:**
   - Solo **Propietarios** y **Administradores** pueden acceder

### Agregar un Nuevo Miembro

1. Clic en **"Agregar Miembro"**
2. Llenar el formulario:
   - **Email** (obligatorio)
   - Nombre y apellido (opcional)
   - **Rol** (seleccionar de la lista)
3. El sistema:
   - Busca si el usuario existe
   - Si no existe, crea cuenta automáticamente
   - Envía email de invitación
   - Redirige a configurar permisos

### Configurar Permisos de un Miembro

1. En la lista de equipo, clic en **"Permisos"** del miembro
2. Seleccionar módulos que puede acceder
3. Para cada módulo, marcar permisos:
   - ✅ Ver
   - ✅ Crear
   - ✅ Editar
   - ✅ Eliminar
4. **Acciones Rápidas disponibles:**
   - Marcar todos: Ver
   - Marcar todos: Crear
   - Marcar todos: Editar
   - Marcar todos: Eliminar
   - Desmarcar todo
5. Guardar cambios

### Editar un Miembro

1. Clic en **icono de edición** (✏️)
2. Cambiar rol o estado activo/inactivo
3. Guardar

### Eliminar un Miembro

1. Clic en **icono de eliminar** (🗑️)
2. Confirmar eliminación
3. **Solo el propietario puede eliminar miembros**

---

## 🎨 Interfaz Visual

### Lista de Equipo
- **Cards con colores por rol:**
  - 🟠 Propietario: Degradado dorado
  - 🔵 Administrador: Degradado azul
  - 🟢 Doctor: Degradado verde
  - 🟣 Personal: Degradado morado
  - 🔴 Cajero: Degradado rojo
  - ⚫ Visualizador: Degradado gris

- **Estadísticas en tiempo real:**
  - Total de miembros
  - Miembros activos
  - Cantidad de administradores
  - Cantidad de doctores

### Gestión de Permisos
- **Interfaz por categorías:**
  - Módulos agrupados por tipo (Core, Médico, Ventas, etc.)
  - Tabla interactiva con checkboxes
  - Colores por tipo de permiso
  - Tooltips informativos

- **Acciones rápidas:**
  - Botones para selección masiva
  - Auto-marcado de módulos al seleccionar permisos

---

## 🔐 Reglas de Seguridad

### Jerarquía de Roles
1. **Propietario** → Acceso total + no se puede eliminar
2. **Administrador** → Acceso total + gestión de equipo (excepto propietario)
3. **Resto de roles** → Permisos personalizados obligatorios

### Restricciones
- ✅ Propietarios y Admins tienen acceso automático a todo
- ✅ No se pueden configurar permisos de Propietarios y Admins
- ❌ No se puede cambiar el rol del propietario
- ❌ Solo el propietario puede eliminar miembros
- ❌ Los administradores no pueden editar al propietario

### Validaciones
- Email obligatorio al agregar miembro
- Rol obligatorio al crear miembro
- No duplicar emails en la misma organización
- Al menos un permiso "Ver" si se asigna módulo

---

## 📧 Sistema de Invitaciones

### Email Automático
Al agregar un nuevo miembro se envía automáticamente:

**Contenido del email:**
- Nombre de la organización
- Rol asignado
- Quien lo invitó
- Botón para iniciar sesión
- Instrucciones de acceso

**Diseño:**
- Gradiente corporativo (morado-azul)
- Responsive para móvil
- Logo del sistema
- Información clara y concisa

---

## 🛠️ Componentes Técnicos Creados

### Modelos (Django)
1. **`ModulePermission`** - Define módulos del sistema
   - code, name, description
   - category, icon, url_pattern
   - Configuración de permisos requeridos

2. **`OrganizationMember`** - Extendido con:
   - `invited_by` - Quién invitó al miembro
   - `custom_permissions` - Relación M2M con módulos
   - Métodos: `has_module_access()`, `can_view()`, `can_create()`, `can_edit()`, `can_delete()`

3. **`MemberModulePermission`** - Tabla intermedia
   - Permisos granulares (view, create, edit, delete)
   - granted_by - Quién otorgó los permisos
   - granted_at - Fecha de otorgamiento

### Vistas (views_team.py)
- `team_list()` - Lista de miembros
- `team_member_add()` - Agregar miembro
- `team_member_edit()` - Editar miembro
- `team_member_permissions()` - Gestionar permisos
- `team_member_delete()` - Eliminar miembro
- `team_modules_list()` - Listar módulos (owner only)

### Templates
- `team_list.html` - Vista principal
- `team_member_add.html` - Formulario de agregar
- `team_member_edit.html` - Formulario de editar
- `team_member_permissions.html` - Gestión de permisos
- `team_member_delete.html` - Confirmación de eliminación
- `email_invitation.html` - Email de invitación

### Comando de Gestión
- `init_modules` - Inicializa los 19 módulos del sistema
  ```bash
  python manage.py init_modules
  ```

### Rutas (URLs)
```python
/dashboard/team/                          # Lista de equipo
/dashboard/team/add/                      # Agregar miembro
/dashboard/team/<id>/edit/                # Editar miembro
/dashboard/team/<id>/permissions/         # Gestionar permisos
/dashboard/team/<id>/delete/              # Eliminar miembro
/dashboard/team/modules/                  # Lista de módulos (config)
```

---

## 📝 Migraciones Aplicadas

### Migración 0022 (organizations)
- ✅ Creado modelo `ModulePermission`
- ✅ Agregado campo `invited_by` a `OrganizationMember`
- ✅ Modificado campo `role` (agregados doctor y cashier)
- ✅ Creado modelo `MemberModulePermission`
- ✅ Agregado `custom_permissions` M2M

### Migración 0014 (billing)
- ✅ Agregados campos `es_factura_electronica` y `requiere_envio_dian`

---

## 🎓 Guía de Uso Rápida

### Escenario 1: Agregar un Doctor
```
1. Dashboard → Configuración → Gestión de Equipo
2. Clic en "Agregar Miembro"
3. Email: doctor@ejemplo.com
4. Nombre: Dr. Juan Pérez
5. Rol: Doctor/Optómetra
6. Guardar
7. En la pantalla de permisos:
   - Marcar módulos: Citas, Pacientes, Historia Clínica, Exámenes Visuales
   - Para cada uno: ✅ Ver, ✅ Crear, ✅ Editar
   - Dashboard: ✅ Ver
8. Guardar Permisos
```

### Escenario 2: Agregar un Cajero
```
1. Agregar Miembro
2. Email: cajero@ejemplo.com
3. Rol: Cajero
4. Permisos:
   - Ventas: ✅ Ver, ✅ Crear, ✅ Editar
   - Facturación: ✅ Ver, ✅ Crear
   - Productos: ✅ Ver
   - Inventario: ✅ Ver
5. Guardar
```

### Escenario 3: Personal Administrativo
```
1. Agregar Miembro
2. Rol: Personal
3. Permisos:
   - Citas: ✅ Ver, ✅ Crear, ✅ Editar
   - Pacientes: ✅ Ver, ✅ Crear
   - Ventas: ✅ Ver
4. Guardar
```

---

## 🔄 Flujo de Invitación

```
1. Admin agrega miembro con email → 
2. Sistema verifica si usuario existe → 
3a. SI existe: Lo agrega a organización
3b. NO existe: Crea usuario nuevo con password aleatorio
4. Envía email de invitación →
5. Usuario recibe email →
6. Usuario ingresa al sistema →
7. Si es primera vez: Solicita restablecer contraseña →
8. Inicia sesión →
9. Accede según permisos asignados
```

---

## ✅ Ventajas del Sistema

1. **🔐 Seguridad**: Control granular de accesos
2. **📊 Escalabilidad**: Fácil agregar más módulos
3. **👥 Colaboración**: Equipos pueden trabajar juntos
4. **🎯 Flexibilidad**: Permisos personalizados por rol
5. **📧 Automatización**: Invitaciones automáticas
6. **👁️ Visibilidad**: Dashboard de equipo con métricas
7. **🎨 UX Moderna**: Interfaz intuitiva y colorida
8. **📱 Responsive**: Funciona en todos los dispositivos

---

## 🚦 Testing Recomendado

### Test 1: Agregar Miembro Nuevo
- ✅ Email no existente crea usuario
- ✅ Se envía email de invitación
- ✅ Se redirige a configuración de permisos

### Test 2: Agregar Miembro Existente
- ✅ Email existente lo agrega sin crear usuario
- ✅ Validación de no duplicados en organización

### Test 3: Permisos Granulares
- ✅ Doctor solo ve módulos asignados
- ✅ Cajero solo accede a ventas
- ✅ Viewer solo lectura

### Test 4: Jerarquía de Roles
- ✅ Admin puede gestionar staff
- ✅ Admin NO puede eliminar owner
- ✅ Owner puede eliminar cualquier miembro

### Test 5: Acciones Rápidas
- ✅ "Marcar todos: Ver" marca todos los checkboxes de ver
- ✅ "Desmarcar todo" limpia todos los permisos

---

## 📚 Próximos Pasos Recomendados

### Mejoras Futuras
1. **Roles Personalizados**: Crear roles custom desde el dashboard
2. **Plantillas de Permisos**: Guardar configuraciones predefinidas
3. **Historial de Cambios**: Log de modificaciones de permisos
4. **Notificaciones**: Avisar cuando se cambian permisos
5. **Expiración de Membresías**: Membresías temporales
6. **Multi-Sucursal**: Permisos por sucursal
7. **API de Permisos**: Endpoint REST para verificar permisos

### Integraciones
- Sincronizar con Active Directory
- SSO (Single Sign-On)
- 2FA (Autenticación de dos factores)

---

## 🎉 ¡Listo para Usar!

El sistema está **completamente funcional** y listo para gestionar equipos de cualquier tamaño. 

**Acceso directo:**
http://localhost:8000/dashboard/team/

**Comandos útiles:**
```bash
# Reinicializar módulos
python manage.py init_modules

# Ver migraciones
python manage.py showmigrations organizations

# Crear superusuario si no existe
python manage.py createsuperuser
```

---

## 📞 Soporte

Si necesitas ayuda o tienes dudas sobre el sistema de gestión de equipo, puedes:
1. Revisar la documentación de los módulos
2. Consultar los comentarios en el código
3. Ver ejemplos en las templates

¡Disfruta de tu nuevo sistema de gestión de equipo! 🚀
