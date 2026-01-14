# Sistema de Sidebar Personalizable

**Fecha de Implementación:** Enero 14, 2026  
**Estado:** Implementado (pendiente migración de BD)  
**Versión:** 1.0.0

## 📋 Índice

1. [Descripción General](#descripción-general)
2. [Funcionalidades](#funcionalidades)
3. [Arquitectura Técnica](#arquitectura-técnica)
4. [Componentes Implementados](#componentes-implementados)
5. [Flujo de Uso](#flujo-de-uso)
6. [Estado Actual](#estado-actual)
7. [Pendientes](#pendientes)
8. [Instrucciones de Completación](#instrucciones-de-completación)

---

## 📖 Descripción General

Sistema que permite a cada usuario personalizar el menú lateral (sidebar) de OpticaApp según sus preferencias:

- **Reordenar items** del menú arrastrando y soltando
- **Crear grupos** (submenús) agrupando items relacionados
- **Nombrar grupos** con nombres personalizados e iconos
- **Persistencia** por usuario y organización
- **Edición in-situ** directamente en el sidebar sin necesidad de páginas adicionales

### Problema que Resuelve

Los usuarios tienen diferentes flujos de trabajo y priorizan diferentes módulos. Un sidebar estático no se adapta a las necesidades individuales. Este sistema permite que cada usuario organice su espacio de trabajo de manera óptima.

---

## ✨ Funcionalidades

### 1. Modo Edición
- **Activación:** Botón "⚙️ Modo Edición" en el header del sidebar
- **Indicadores visuales:** 
  - Ícono de arrastre (⋮⋮) en cada item
  - Borde punteado verde al activar
  - Animaciones de hover y drag
- **Desactivación automática:** Al guardar cambios

### 2. Reordenamiento de Items
- **Drag & Drop:** Arrastra cualquier item para cambiar su posición
- **Feedback visual:** 
  - Item se vuelve semi-transparente al arrastrar
  - Drop zones se iluminan al pasar sobre ellos
- **Restricciones:** El item "Personalizar Menú" no se puede mover

### 3. Creación de Grupos
- **Método:** Arrastra un item sobre otro item
- **Modal interactivo:**
  - Campo de texto para nombre del grupo
  - Selector de 6 iconos predefinidos:
    - 📊 Estadísticas
    - 👥 Personas
    - 💰 Finanzas
    - ⚙️ Configuración
    - 📋 Gestión
    - 🏥 Clínica
- **Validación:** Nombre requerido antes de crear

### 4. Gestión de Grupos
- **Expandir/Colapsar:** Click en el grupo
- **Editar nombre:** Click en el nombre del grupo
- **Eliminar grupo:** Click en el ícono (×) - los items regresan al nivel principal
- **Agregar items:** Arrastra items existentes al grupo

### 5. Persistencia de Configuración
- **Nivel 1 - LocalStorage:** 
  - Guardado inmediato al hacer cambios
  - Funciona sin base de datos
  - Específico por navegador
  
- **Nivel 2 - Base de Datos (pendiente migración):**
  - Guardado por usuario y organización
  - Sincronización entre dispositivos
  - Versionado de configuración

### 6. Restaurar Configuración
- **Botón:** "Restaurar Predeterminado" en modo edición
- **Acción:** Vuelve al orden original del sidebar
- **Confirmación:** Requiere confirmación del usuario

---

## 🏗️ Arquitectura Técnica

### Diagrama de Componentes

```
┌─────────────────────────────────────────────────────────┐
│                    FRONTEND (base.html)                 │
├─────────────────────────────────────────────────────────┤
│  • Botón Modo Edición                                   │
│  • SidebarEditor (JavaScript)                           │
│  • Modal de Creación de Grupos                          │
│  • SortableJS (Drag & Drop)                             │
│  • LocalStorage Manager                                 │
└──────────────────┬──────────────────────────────────────┘
                   │ AJAX (Fetch API)
                   │ GET/POST con CSRF Token
┌──────────────────▼──────────────────────────────────────┐
│              BACKEND API (Django)                       │
├─────────────────────────────────────────────────────────┤
│  views_sidebar_api.py                                   │
│  ├─ get_sidebar_config()   [GET]                        │
│  ├─ save_sidebar_config()  [POST]                       │
│  └─ reset_sidebar_config() [POST]                       │
└──────────────────┬──────────────────────────────────────┘
                   │ Django ORM
┌──────────────────▼──────────────────────────────────────┐
│              MODELO (models_sidebar.py)                 │
├─────────────────────────────────────────────────────────┤
│  SidebarCustomization                                   │
│  ├─ user (FK User)                                      │
│  ├─ organization (FK Organization)                      │
│  ├─ config (JSONField)                                  │
│  └─ version (IntegerField)                              │
└──────────────────┬──────────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────────┐
│           POSTGRESQL (dashboard_sidebarcustomization)   │
└─────────────────────────────────────────────────────────┘
```

### Tecnologías Utilizadas

| Componente | Tecnología | Versión |
|------------|------------|---------|
| Backend | Django | 4.x |
| Frontend | JavaScript ES6 | - |
| Drag & Drop | SortableJS | 1.15.0 |
| Estilos | Tailwind CSS + Custom CSS | - |
| Base de Datos | PostgreSQL | - |
| Persistencia Temporal | LocalStorage API | - |

---

## 🔧 Componentes Implementados

### 1. Modelo de Datos

**Archivo:** `apps/dashboard/models_sidebar.py`

```python
class SidebarCustomization(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE)
    config = models.JSONField(default=dict)  # Configuración flexible
    version = models.IntegerField(default=1)  # Control de versiones
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = [['user', 'organization']]
```

**Estructura del JSONField `config`:**

```json
{
  "items": [
    {
      "id": "dashboard",
      "type": "link",
      "label": "Dashboard",
      "url": "/dashboard/",
      "icon": "home"
    },
    {
      "id": "group_finances",
      "type": "group",
      "label": "Finanzas",
      "icon": "💰",
      "items": [
        {
          "id": "ventas",
          "type": "link",
          "label": "Ventas",
          "url": "/ventas/"
        },
        {
          "id": "gastos",
          "type": "link",
          "label": "Gastos",
          "url": "/gastos/"
        }
      ]
    }
  ],
  "version": 1
}
```

### 2. API REST

**Archivo:** `apps/dashboard/views_sidebar_api.py`

#### Endpoints:

##### GET `/api/sidebar/config/`
- **Propósito:** Obtener configuración actual del usuario
- **Autenticación:** Required
- **Parámetros:** organization_id (query)
- **Respuesta:**
```json
{
  "success": true,
  "config": { /* JSONField config */ }
}
```

##### POST `/api/sidebar/save/`
- **Propósito:** Guardar nueva configuración
- **Autenticación:** Required
- **Body:**
```json
{
  "organization_id": 2,
  "config": { /* nueva configuración */ }
}
```
- **Respuesta:**
```json
{
  "success": true,
  "message": "Configuración guardada exitosamente"
}
```

##### POST `/api/sidebar/reset/`
- **Propósito:** Restaurar configuración predeterminada
- **Autenticación:** Required
- **Body:**
```json
{
  "organization_id": 2
}
```

### 3. Interfaz de Usuario

**Archivo:** `apps/dashboard/templates/dashboard/base.html`

#### 3.1 HTML Agregado

**Botón de Modo Edición (Header Sidebar):**
```html
<button id="editSidebarBtn" 
        class="w-full px-4 py-2 text-sm text-gray-600 hover:bg-gray-100 
               flex items-center gap-2 transition-colors">
    <span class="text-lg">⚙️</span>
    <span>Modo Edición</span>
</button>
```

**Modal de Creación de Grupos:**
```html
<div id="createGroupModal" class="hidden fixed inset-0 bg-black bg-opacity-50 
                                  z-[9999] flex items-center justify-center">
    <!-- Formulario con nombre e iconos -->
</div>
```

#### 3.2 CSS Personalizado (130+ líneas)

**Estilos principales:**

```css
/* Modo edición activo */
#sidebar-nav.edit-mode .nav-item {
    border: 2px dashed #10b981;
    cursor: move;
}

/* Item siendo arrastrado */
.dragging {
    opacity: 0.5;
    transform: rotate(2deg);
}

/* Zona de drop activa */
.drop-target {
    background: linear-gradient(135deg, #10b981 0%, #059669 100%);
    transform: scale(1.02);
}

/* Animación de pulso */
@keyframes pulse-green {
    0%, 100% { box-shadow: 0 0 0 0 rgba(16, 185, 129, 0.7); }
    50% { box-shadow: 0 0 0 10px rgba(16, 185, 129, 0); }
}
```

#### 3.3 JavaScript (400+ líneas)

**Objeto Principal: SidebarEditor**

```javascript
const SidebarEditor = {
    isEditMode: false,
    currentConfig: null,
    draggedElement: null,
    
    // Inicialización
    init() {
        this.loadConfig();
        this.setupEventListeners();
        this.initSortable();
    },
    
    // Toggle modo edición
    toggleEditMode() { /* ... */ },
    
    // Guardar configuración
    async saveConfig() { /* AJAX POST a /api/sidebar/save/ */ },
    
    // Cargar configuración
    async loadConfig() { /* AJAX GET desde /api/sidebar/config/ */ },
    
    // Aplicar configuración
    applyConfig(config) { /* Renderiza grupos y orden */ },
    
    // Crear grupo desde modal
    createGroupFromModal(item1, item2, name, icon) { /* ... */ },
    
    // Drag & Drop handlers
    handleDragStart(e) { /* ... */ },
    handleDragOver(e) { /* ... */ },
    handleDrop(e) { /* ... */ }
};
```

**Integración SortableJS:**

```javascript
function initSortable() {
    new Sortable(document.getElementById('sidebar-nav'), {
        animation: 150,
        handle: '.drag-handle',
        ghostClass: 'dragging',
        onEnd: function(evt) {
            SidebarEditor.saveConfig();
        }
    });
}
```

### 4. Rutas (URLs)

**Archivo:** `apps/dashboard/urls.py`

```python
from . import views_sidebar_api

urlpatterns = [
    # ... rutas existentes ...
    
    # API Sidebar Customization
    path('api/sidebar/config/', 
         views_sidebar_api.get_sidebar_config, 
         name='api_get_sidebar_config'),
    
    path('api/sidebar/save/', 
         views_sidebar_api.save_sidebar_config, 
         name='api_save_sidebar_config'),
    
    path('api/sidebar/reset/', 
         views_sidebar_api.reset_sidebar_config, 
         name='api_reset_sidebar_config'),
]
```

### 5. Migración

**Archivo:** `apps/dashboard/migrations/0013_sidebarcustomization.py`

```python
operations = [
    migrations.CreateModel(
        name='SidebarCustomization',
        fields=[
            ('id', models.BigAutoField(auto_created=True, primary_key=True)),
            ('config', models.JSONField(default=dict)),
            ('version', models.IntegerField(default=1)),
            ('created_at', models.DateTimeField(auto_now_add=True)),
            ('updated_at', models.DateTimeField(auto_now=True)),
            ('organization', models.ForeignKey(...)),
            ('user', models.ForeignKey(...)),
        ],
        options={
            'unique_together': {('user', 'organization')},
        },
    ),
]
```

**Dependencia:** `('dashboard', '0028_employee_payroll_fields')`

---

## 📱 Flujo de Uso

### Escenario 1: Reordenar Items

1. Usuario hace click en "⚙️ Modo Edición"
2. Sidebar muestra bordes verdes punteados e iconos de arrastre
3. Usuario arrastra item "Ventas" y lo suelta sobre "Citas"
4. Items intercambian posiciones
5. Sistema guarda automáticamente en localStorage
6. Usuario sale del modo edición
7. Configuración persiste en próximas sesiones

### Escenario 2: Crear Grupo "Finanzas"

1. Usuario activa modo edición
2. Arrastra item "Ventas" sobre item "Gastos"
3. Se abre modal "Crear Grupo"
4. Ingresa nombre: "Finanzas"
5. Selecciona icono: 💰
6. Click en "Crear Grupo"
7. Se crea grupo expandido con ambos items
8. Sistema guarda configuración
9. Grupo persiste en sidebar

### Escenario 3: Editar Grupo Existente

1. Usuario hace click en nombre del grupo "Finanzas"
2. Aparece input editable
3. Cambia nombre a "Contabilidad"
4. Presiona Enter
5. Nombre actualizado
6. Configuración guardada automáticamente

### Escenario 4: Eliminar Grupo

1. Usuario hace click en (×) del grupo "Contabilidad"
2. Sistema pregunta: "¿Desagrupar items?"
3. Usuario confirma
4. Items "Ventas" y "Gastos" regresan al nivel principal
5. Grupo eliminado
6. Configuración guardada

---

## 📊 Estado Actual

### ✅ Completado

- [x] Modelo `SidebarCustomization` creado
- [x] API REST completa (3 endpoints)
- [x] UI completa con modo edición
- [x] Sistema drag & drop funcional
- [x] Modal para crear grupos
- [x] Selector de iconos (6 opciones)
- [x] Auto-save en localStorage
- [x] CSS responsivo y animaciones
- [x] CSRF protection en AJAX
- [x] Validación de datos en backend
- [x] Código commiteado a GitHub (commits: 107b58e, 2e4d9c6)
- [x] Código desplegado en servidor Contabo

### 🔄 En Progreso

- [ ] Migración de base de datos (bloqueada por `KeyError: 'whatsapp_enabled'`)

### ❌ Pendiente

- [ ] Tabla `dashboard_sidebarcustomization` en PostgreSQL
- [ ] Sincronización BD con localStorage
- [ ] Pruebas de usuario en producción
- [ ] Documentación de usuario final

---

## ⚠️ Pendientes

### 1. Resolver Error de Migración

**Problema Actual:**
```
KeyError: 'whatsapp_enabled'
File "/django/db/migrations/operations/fields.py", line 165
state.remove_field(app_label, self.model_name_lower, self.name)
```

**Causa:** Migración anterior intenta remover campo `whatsapp_enabled` que no existe en el modelo actual.

**Impacto:** Bloquea TODAS las migraciones de la app `dashboard`, incluyendo la creación de `SidebarCustomization`.

### 2. Crear Tabla Manualmente (Solución Temporal)

Si no se puede resolver el error de migración, crear tabla directamente:

```sql
CREATE TABLE dashboard_sidebarcustomization (
    id BIGSERIAL PRIMARY KEY,
    config JSONB DEFAULT '{}',
    version INTEGER DEFAULT 1,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    user_id INTEGER REFERENCES users_user(id) ON DELETE CASCADE,
    organization_id INTEGER REFERENCES organizations_organization(id) ON DELETE CASCADE,
    UNIQUE(user_id, organization_id)
);

CREATE INDEX idx_sidebar_user_org ON dashboard_sidebarcustomization(user_id, organization_id);
```

Luego hacer fake de la migración:
```bash
python manage.py migrate --fake dashboard 0013_sidebarcustomization
```

### 3. Migración de Datos LocalStorage → BD

Una vez creada la tabla, implementar endpoint para migrar configuraciones:

```python
# views_sidebar_api.py
def migrate_localstorage_to_db(request):
    """Endpoint para migrar config de localStorage a BD"""
    config = request.POST.get('config')
    # Guardar en SidebarCustomization
```

### 4. Sincronización Multi-Dispositivo

Implementar lógica para sincronizar cambios entre:
- LocalStorage (navegador actual)
- Base de datos (servidor)
- Otros dispositivos del usuario

**Estrategia sugerida:**
- Usar `version` field para control de versiones
- Comparar versiones al cargar configuración
- Resolver conflictos priorizando cambio más reciente

---

## 🚀 Instrucciones de Completación

### Paso 1: Resolver Migración

**Opción A - Investigar y Corregir:**
```bash
# Conectar a servidor
ssh root@84.247.129.180

# Ver migración problemática
cd /var/www/opticaapp
source venv/bin/activate
python manage.py showmigrations dashboard

# Identificar migración con RemoveField 'whatsapp_enabled'
# Comentar o corregir esa operación
```

**Opción B - Crear Tabla Manualmente:**
```bash
# Conectar a PostgreSQL
psql -U opticaapp_user -d opticaapp_db

# Ejecutar SQL de creación (ver sección Pendientes #2)

# Fake la migración
python manage.py migrate --fake dashboard 0013_sidebarcustomization
```

### Paso 2: Reiniciar Aplicación

```bash
pm2 restart opticaapp
pm2 logs opticaapp --lines 50
```

### Paso 3: Verificar Funcionalidad

1. Acceder a https://opticaapp.com
2. Iniciar sesión con usuario de prueba
3. Click en "⚙️ Modo Edición"
4. Reordenar 2-3 items
5. Crear un grupo
6. Recargar página
7. Verificar que cambios persisten

### Paso 4: Monitoreo

```bash
# Ver logs de aplicación
pm2 logs opticaapp

# Ver logs de PostgreSQL
tail -f /var/log/postgresql/postgresql-*.log

# Verificar tabla creada
psql -U opticaapp_user -d opticaapp_db -c "\d dashboard_sidebarcustomization"
```

### Paso 5: Pruebas

**Casos de prueba:**

1. **Reordenamiento:**
   - Mover item al inicio
   - Mover item al final
   - Mover item al medio
   - Verificar persistencia

2. **Grupos:**
   - Crear grupo con 2 items
   - Agregar 3er item a grupo existente
   - Editar nombre de grupo
   - Eliminar grupo
   - Verificar persistencia

3. **Restaurar:**
   - Hacer varios cambios
   - Click en "Restaurar Predeterminado"
   - Confirmar que vuelve al orden original

4. **Multi-Usuario:**
   - Usuario A hace cambios
   - Usuario B en misma organización NO debe ver cambios de A
   - Verificar aislamiento por usuario

5. **Multi-Dispositivo (cuando esté en BD):**
   - Usuario hace cambios en PC
   - Verificar que se ven en móvil/tablet

---

## 📚 Referencias Técnicas

### Archivos Modificados

```
apps/dashboard/
├── models_sidebar.py              [NUEVO - 45 líneas]
├── views_sidebar_api.py           [NUEVO - 89 líneas]
├── urls.py                        [MODIFICADO - 3 líneas agregadas]
├── migrations/
│   └── 0013_sidebarcustomization.py  [NUEVO - 32 líneas]
└── templates/dashboard/
    └── base.html                  [MODIFICADO - 497 líneas agregadas]
```

### Commits Relacionados

- **107b58e** - feat: Sistema completo de edición sidebar con drag & drop
- **2e4d9c6** - fix: Corregir dependencia de migración sidebar (0012 → 0028)
- **af8f883** - feat: Agregar item "Personalizar Menú" al perfil

### Documentos Relacionados

- [ANALISIS_COMPLETO_09ENE2026.md](./ANALISIS_COMPLETO_09ENE2026.md)
- [CAMBIOS_07ENE2026.md](./CAMBIOS_07ENE2026.md)

### Enlaces Útiles

- **SortableJS:** https://github.com/SortableJS/Sortable
- **Django JSONField:** https://docs.djangoproject.com/en/4.0/ref/models/fields/#jsonfield
- **LocalStorage API:** https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage

---

## 🎯 Roadmap Futuro

### Versión 1.1 (Próxima)
- [ ] Migración automática localStorage → BD
- [ ] Sincronización en tiempo real (WebSockets)
- [ ] Presets de configuración (por rol/departamento)
- [ ] Importar/Exportar configuración

### Versión 1.2
- [ ] Temas de color por grupo
- [ ] Iconos personalizados (subir imagen)
- [ ] Sidebar colapsable con memorización
- [ ] Atajos de teclado para navegación

### Versión 2.0
- [ ] Drag & drop desde catálogo de módulos
- [ ] Compartir configuración entre usuarios
- [ ] Analytics de uso de módulos
- [ ] Recomendaciones IA de organización

---

## 👥 Contribuciones

**Desarrollador Principal:** GitHub Copilot + Usuario  
**Fecha Inicio:** Enero 13, 2026  
**Fecha Implementación:** Enero 14, 2026  
**Tiempo de Desarrollo:** ~4 horas  

**Líneas de Código:**
- Python: 166 líneas
- JavaScript: 430 líneas
- CSS: 130 líneas
- HTML: 50 líneas
- **Total:** 776 líneas

---

## 📞 Soporte

Para reportar bugs o solicitar mejoras:
1. Crear issue en repositorio GitHub
2. Etiquetar con `sidebar-customization`
3. Incluir capturas de pantalla si aplica

**Contacto:** Oceanoptics4@gmail.com

---

**Última actualización:** Enero 14, 2026  
**Versión documento:** 1.0.0
