# 🚀 SaaS Core Package - Sistema Reutilizable

**Autor**: Daniel (danioso8)  
**Proyecto Base**: OpticaApp  
**Fecha**: 30 de diciembre de 2024  

---

## 📋 ¿Qué es esto?

Este es un **paquete reutilizable** que extrae toda la funcionalidad SaaS de OpticaApp para que puedas crear **nuevos proyectos en minutos** sin tener que reconfigurar:

- ✅ Wompi (pagos)
- ✅ WhatsApp (notificaciones)
- ✅ Facturación electrónica DIAN
- ✅ Sistema de suscripciones
- ✅ Trial de 90 días
- ✅ Renovación automática
- ✅ Multi-tenancy
- ✅ Emails automáticos
- ✅ Landing pages

---

## 🎯 Proyectos Disponibles

Ya vienen **3 configuraciones pre-hechas**:

### 1. OpticaApp (Healthcare)
```bash
python setup_new_project.py saas_config.json ../OpticaAppNew
```
- 7-20 módulos según plan
- Enfocado en: Pacientes, Citas, Historia Clínica, Doctores
- Precio: $12-$200 USD/mes

### 2. InmobiliariaApp (Real Estate)
```bash
python setup_new_project.py templates/inmobiliaria_config.json ../InmobiliariaApp
```
- Módulos: Propiedades, Clientes, Asesores, Tours Virtuales, CRM
- Precio: $15-$250 USD/mes
- Incluye: Lead Scoring, Galería, API para portales

### 3. CompraVentaApp (Retail)
```bash
python setup_new_project.py templates/compraventa_config.json ../CompraVentaApp
```
- Módulos: Productos, Ventas, POS, Inventario, E-commerce
- Precio: $10-$220 USD/mes
- Incluye: Código de barras, Programa de lealtad, Multi-sede

---

## 🛠️ Cómo Usar

### Paso 1: Navegar al paquete
```bash
cd d:\ESCRITORIO\OpticaApp\saas_core_package
```

### Paso 2: Crear nuevo proyecto
```bash
# Para inmobiliaria
python setup_new_project.py templates/inmobiliaria_config.json D:\ESCRITORIO\InmobiliariaApp

# Para compraventa
python setup_new_project.py templates/compraventa_config.json D:\ESCRITORIO\CompraVentaApp
```

### Paso 3: El script automáticamente:
1. ✅ Crea la estructura de directorios
2. ✅ Copia todos los archivos core desde OpticaApp
3. ✅ Genera `plan_features.py` personalizado con tus módulos
4. ✅ Crea `requirements.txt` con dependencias
5. ✅ Genera `.env.example` con variables necesarias
6. ✅ Crea README.md personalizado

### Paso 4: Configurar el nuevo proyecto
```bash
cd D:\ESCRITORIO\InmobiliariaApp
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env
# Editar .env con tus credenciales
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

---

## 📁 Estructura del Paquete

```
saas_core_package/
│
├── saas_config.json              # Configuración de OpticaApp
│
├── templates/                    # Configuraciones predefinidas
│   ├── inmobiliaria_config.json  # Para inmobiliarias
│   └── compraventa_config.json   # Para compraventa
│
├── setup_new_project.py          # Script principal
│
└── INSTRUCCIONES.md              # Este archivo
```

---

## 🎨 Crear Tu Propia Configuración

Puedes crear una configuración para cualquier industria:

### 1. Duplicar un template
```bash
cp templates/inmobiliaria_config.json templates/mi_config.json
```

### 2. Editar el JSON

```json
{
  "project_name": "MiApp",
  "industry": "mi_industria",
  "developer": "Daniel (danioso8)",
  
  "subscription_plans": [
    {
      "code": "free",
      "name": "Gratis",
      "price_usd": 10,
      "modules": ["dashboard", "mi_modulo1", "mi_modulo2"]
    }
  ],
  
  "modules": {
    "mi_modulo1": {
      "name": "Mi Módulo",
      "icon": "bi-star",
      "description": "Descripción del módulo"
    }
  }
}
```

### 3. Generar proyecto
```bash
python setup_new_project.py templates/mi_config.json ../MiApp
```

---

## 🔧 Lo Que Se Copia Automáticamente

### Archivos Core
- ✅ `apps/users/` - Todo el sistema de autenticación, suscripciones, pagos
- ✅ `apps/organizations/` - Multi-tenancy, planes, decoradores
- ✅ `apps/dashboard/` - Dashboard base
- ✅ `apps/billing/` - Facturación DIAN
- ✅ `config/settings.py` - Configuración Django
- ✅ Templates HTML completos
- ✅ Comandos de management (cron jobs)

### Lo Que Debes Personalizar Manualmente
- ⚠️ Models específicos de tu industria (ej: Property, Product, etc.)
- ⚠️ Views específicas de tu negocio
- ⚠️ Templates personalizados (puedes usar los base como referencia)

---

## 📊 Comparación de Configuraciones

| Característica | OpticaApp | InmobiliariaApp | CompraVentaApp |
|----------------|-----------|-----------------|----------------|
| **Industria** | Healthcare | Real Estate | Retail |
| **Planes** | 5 | 5 | 5 |
| **Trial** | 90 días | 90 días | 90 días |
| **Plan Free** | $12/mes | $15/mes | $10/mes |
| **Plan Max** | $200/mes | $250/mes | $220/mes |
| **Módulos** | 20 | 19 | 20 |
| **Wompi** | ✅ | ✅ | ✅ |
| **WhatsApp** | ✅ | ✅ | ✅ |
| **DIAN** | ✅ | ✅ | ✅ |

---

## 🎯 Módulos por Industria

### Healthcare (OpticaApp)
- Pacientes
- Historia Clínica
- Exámenes Visuales
- Doctores/Optómetras
- Citas

### Real Estate (InmobiliariaApp)
- Propiedades
- Asesores Inmobiliarios
- Tours Virtuales
- CRM de Prospectos
- Lead Scoring

### Retail (CompraVentaApp)
- Punto de Venta (POS)
- Escáner Códigos de Barras
- E-commerce
- Programa de Lealtad
- Multi-sede

---

## 🔐 Variables de Entorno

El script genera automáticamente `.env.example` con:

### Básicas (Todas las industrias)
```env
DEBUG=True
SECRET_KEY=...
DATABASE_URL=...
```

### Wompi (Si está habilitado)
```env
WOMPI_PUBLIC_KEY=pub_test_xxxxx
WOMPI_PRIVATE_KEY=prv_test_xxxxx
WOMPI_TEST_MODE=True
```

### WhatsApp (Si está habilitado)
```env
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

### Email
```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_HOST_USER=...
EMAIL_HOST_PASSWORD=...
```

---

## 🚀 Deploy en Render.com

Todos los proyectos generados son compatibles con Render.com:

### 1. Crear Web Service
- Build Command: `pip install -r requirements.txt && python manage.py collectstatic --noinput && python manage.py migrate`
- Start Command: `gunicorn config.wsgi:application`

### 2. Agregar PostgreSQL

### 3. Configurar Variables de Entorno
- Copiar todas las de `.env.example`
- Agregar `RENDER_DISK_PATH=/var/data`

### 4. Cron Jobs (Render)
```bash
# Renovaciones automáticas
0 2 * * * cd /opt/render/project/src && python manage.py renew_subscriptions

# Recordatorios
0 9 * * * cd /opt/render/project/src && python manage.py send_renewal_reminders
```

---

## 📝 Ejemplos de Uso

### Crear app inmobiliaria
```bash
cd d:\ESCRITORIO\OpticaApp\saas_core_package
python setup_new_project.py templates/inmobiliaria_config.json D:\ESCRITORIO\InmobiliariaApp
cd D:\ESCRITORIO\InmobiliariaApp
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

### Crear app de compraventa
```bash
cd d:\ESCRITORIO\OpticaApp\saas_core_package
python setup_new_project.py templates/compraventa_config.json D:\ESCRITORIO\CompraVentaApp
cd D:\ESCRITORIO\CompraVentaApp
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver
```

---

## ⚡ Ventajas de Este Sistema

### ✅ Ahorro de Tiempo
- **Sin este paquete**: 2-3 semanas configurando Wompi, WhatsApp, DIAN, suscripciones
- **Con este paquete**: 5 minutos + personalización de tu industria

### ✅ Reutilización
- Todo el código de autenticación
- Sistema completo de pagos
- Multi-tenancy funcionando
- Emails automáticos
- Landing pages

### ✅ Personalización
- Cambias solo los módulos específicos de tu negocio
- El core (pagos, suscripciones, emails) funciona igual

### ✅ Mantenimiento
- Mejoras al core de OpticaApp se pueden portar fácilmente
- Bugs corregidos una vez, aplican a todos los proyectos

---

## 🆘 Troubleshooting

### Error: "No se encontró el archivo config"
**Solución**: Verifica la ruta del archivo JSON
```bash
python setup_new_project.py templates/inmobiliaria_config.json ../InmobiliariaApp
```

### Error: "Target directory already exists"
**Solución**: Cambia el nombre del directorio o elimina el existente
```bash
rm -rf ../InmobiliariaApp
```

### Falta un archivo core
**Solución**: Verifica que OpticaApp esté completo. El script copia desde la ubicación actual.

---

## 📞 Soporte

**Desarrollador**: Daniel (danioso8)  
**Email**: danisobarzo@gmail.com  
**Proyecto Base**: OpticaApp

---

## 🎓 Conceptos Clave

### Multi-Tenancy
Todos los proyectos usan el modelo "shared database" con campo `organization_id` para aislar datos.

### Subscription System
- Trial automático de 90 días
- Renovación automática con Wompi
- 5 planes escalables
- Control de acceso por módulos

### Module Access Control
- Decoradores `@require_module('module_code')`
- Template tags `{% has_module 'module_code' %}`
- Badges de upgrade automáticos

---

## 📈 Roadmap

- [ ] Agregar más templates (Salud, Educación, Turismo)
- [ ] Generador automático de Models según módulos
- [ ] Sistema de plugins
- [ ] API GraphQL opcional
- [ ] Dashboard de analytics centralizado

---

**¡Listo para crear tu próximo SaaS en minutos!** 🚀
