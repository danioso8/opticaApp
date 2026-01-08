# 📋 PROPUESTA DE REORGANIZACIÓN DEL SIDEBAR

## 🎯 Objetivos
1. Mejor organización por categorías funcionales
2. Sistema de permisos granular por módulo
3. Submenús colapsables para reducir visual clutter
4. Iconos consistentes y reconocibles
5. Indicadores visuales de acceso restringido

## 📊 Estructura Propuesta

### 🏢 **MIS EMPRESAS** (Solo Owner/Admin)
- Gestión de organizaciones multi-tenant

---

### 📊 **VENTAS Y FACTURACIÓN**
- Dashboard de Ventas (Todos los usuarios con acceso)
- Punto de Venta - POS (Cajeros, Vendedores, Admin)
- Facturas Electrónicas (Admin, Contador)
- Notas Crédito/Débito (Admin, Contador)
- Reportes de Ventas (Admin, Contador, Gerente)

### 👥 **PACIENTES Y CITAS**
- Pacientes (Doctores, Recepción, Admin)
- Lista de Citas (Todos)
- Agendamiento (Recepción, Admin)
- Exámenes Especiales (Doctores, Admin)

### 👨‍⚕️ **PROFESIONALES**
- Doctores/Optómetras (Admin, RRHH)
- Laboratorios Ópticos (Admin, Encargado Laboratorio)

### 🏥 **PERSONAL Y NÓMINA**
- Empleados (Admin, RRHH)
- Nómina Electrónica (Admin, RRHH, Contador)
- Workflow Nómina (Admin, RRHH)
- Contratos Laborales (Admin, RRHH)
- Vacaciones (Admin, RRHH, Empleados pueden ver las suyas)
- Préstamos (Admin, RRHH)
- Prestaciones Sociales (Admin, RRHH, Contador)
- Provisiones (Admin, Contador)
- PILA (Admin, Contador)
- Incapacidades (Admin, RRHH)

### 💰 **FINANZAS**
- Caja y Tesorería
  - Dashboard de Caja (Admin, Cajeros, Contador)
  - Cajas Registradoras (Admin)
  - Movimientos (Cajeros, Admin)
  - Cierres de Caja (Cajeros, Admin, Contador)
  - Reportes (Admin, Contador)
- Cuentas por Cobrar (Admin, Contador)
- Cuentas por Pagar (Admin, Contador)
- Reportes Financieros (Admin, Contador, Gerente)

### 📦 **INVENTARIO Y COMPRAS**
- Inventario (Admin, Encargado Inventario)
- Productos (Admin, Vendedores ver)
- Proveedores (Admin, Compras)
- Órdenes de Compra (Admin, Compras)
- Recepción de Mercancía (Admin, Almacén)

### 🎯 **MARKETING**
- Promociones (Admin, Marketing)
- Campañas (Admin, Marketing)
- WhatsApp Masivo (Admin, Marketing - requiere plan)

### ⚙️ **CONFIGURACIÓN** (Solo Admin/Owner)
- Configuración General
- Config. Facturación
- Config. DIAN
- Config. WhatsApp
- Landing Page
- Parámetros Clínicos
- Equipo y Permisos

---

## 🔐 Sistema de Permisos por Rol

### **Owner/Admin**
- Acceso total a todos los módulos
- Gestión de equipos y permisos
- Configuración del sistema

### **Contador**
- Facturas, Notas Crédito/Débito
- Nómina y Prestaciones
- Reportes Financieros
- Cierres de Caja (solo lectura)

### **RRHH**
- Empleados
- Nómina completa
- Contratos, Vacaciones, Préstamos
- Incapacidades

### **Doctor/Optómetra**
- Pacientes (completo)
- Citas (sus propias citas)
- Exámenes Especiales
- Doctores (solo lectura)

### **Cajero**
- Punto de Venta
- Caja (abrir, cerrar, movimientos)
- Ventas (crear, listar)

### **Vendedor**
- Punto de Venta
- Productos (lectura)
- Pacientes (lectura)

### **Recepción**
- Citas (completo)
- Pacientes (completo)
- Agendamiento

### **Encargado Inventario**
- Inventario (completo)
- Productos (completo)
- Recepción de Mercancía

### **Compras**
- Proveedores
- Órdenes de Compra
- Recepción de Mercancía

### **Marketing**
- Promociones
- Campañas
- WhatsApp Masivo

### **Visualizador (Viewer)**
- Dashboards (solo lectura)
- Reportes (solo lectura)

---

## 💡 Implementación Técnica

### Context Processor para Permisos
```python
def user_permissions_processor(request):
    if not request.user.is_authenticated:
        return {}
    
    # Verificar si el usuario es owner/admin
    is_owner_or_admin = False
    member = None
    
    if hasattr(request, 'organization') and request.organization:
        member = OrganizationMember.objects.filter(
            organization=request.organization,
            user=request.user,
            is_active=True
        ).first()
        
        if member:
            is_owner_or_admin = member.role in ['owner', 'admin']
    
    # Construir diccionario de permisos por módulo
    perms = {
        'all_access': is_owner_or_admin,
        'member': member,
    }
    
    # Si es owner/admin, tiene todos los permisos
    if is_owner_or_admin:
        # Agregar permisos completos
        pass
    elif member:
        # Cargar permisos personalizados
        for module_perm in member.module_permissions.all():
            module_code = module_perm.module.code
            perms[module_code] = {
                'can_view': module_perm.can_view,
                'can_create': module_perm.can_create,
                'can_edit': module_perm.can_edit,
                'can_delete': module_perm.can_delete,
            }
    
    return {
        'user_perms': perms,
        'is_owner_or_admin': is_owner_or_admin,
    }
```

### Template Tags
```django
{% if user_perms.all_access or user_perms.sales.can_view %}
    <!-- Mostrar opción -->
{% endif %}

{% if user_perms.all_access or user_perms.sales.can_create %}
    <!-- Mostrar botón crear -->
{% endif %}
```

---

## 🎨 Diseño Visual del Sidebar

### Categorías con Iconos
- 📊 Ventas y Facturación (color: blue-600)
- 👥 Pacientes y Citas (color: green-600)
- 👨‍⚕️ Profesionales (color: purple-600)
- 🏥 Personal y Nómina (color: orange-600)
- 💰 Finanzas (color: emerald-600)
- 📦 Inventario y Compras (color: amber-600)
- 🎯 Marketing (color: pink-600)
- ⚙️ Configuración (color: gray-600)

### Estados Visuales
- Activo: bg-indigo-800
- Hover: hover:bg-indigo-700
- Deshabilitado: opacity-50 cursor-not-allowed
- Requiere plan: badge amarillo "PRO"
- Nuevo: badge verde "NUEVO"

---

## ✅ Ventajas de esta Reorganización

1. **Claridad**: Agrupación lógica por función empresarial
2. **Escalabilidad**: Fácil agregar nuevos módulos
3. **Seguridad**: Permisos granulares por rol
4. **UX**: Menos scrolling, submenús colapsables
5. **Mantenimiento**: Estructura consistente y documentada
