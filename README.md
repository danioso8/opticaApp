# 👓 OpticaApp - Sistema de Gestión para Ópticas

Sistema SaaS multi-tenant completo para la gestión integral de ópticas, clínicas oftalmológicas y centros visuales.

## 🌟 Características Principales

### 📊 Módulos del Sistema

- **Dashboard Analítico:** Métricas en tiempo real, KPIs, gráficos interactivos
- **Gestión de Pacientes:** Historias clínicas completas, exámenes oftalmológicos
- **Citas:** Sistema de agendamiento con notificaciones WhatsApp
- **Inventario:** Control de stock, movimientos, lotes, alertas
- **Ventas:** PDV, productos, descuentos, reportes
- **Facturación Electrónica:** Integración DIAN, facturas PDF profesionales
- **Nómina Electrónica:** Gestión completa de nómina, prestaciones sociales
- **Promociones:** Campañas de marketing, cupones, descuentos
- **WhatsApp:** Notificaciones automáticas y comunicación con clientes

### 🏢 Multi-tenant

- Gestión de múltiples organizaciones independientes
- Planes de suscripción personalizables
- Landing pages configurables por organización
- Control de permisos y roles

### 📱 Características Técnicas

- **Framework:** Django 5.2.8
- **Base de Datos:** PostgreSQL
- **Interfaz:** Bootstrap 5, Chart.js
- **WhatsApp:** Integración con Baileys
- **PDFs:** ReportLab con diseños profesionales
- **Facturación:** Integración con DIAN Colombia

## 🚀 Deployment

### Servidor de Producción: Contabo VPS

El sistema está desplegado en un VPS de Contabo con la siguiente configuración:

- **IP:** 84.247.129.180
- **Gestor de Procesos:** PM2
- **Servidor Web:** Gunicorn
- **Base de Datos:** PostgreSQL

📖 **[Ver Guía Completa de Deployment](README_DEPLOYMENT_CONTABO.md)**

### Inicio Rápido (Desarrollo Local)

```bash
# Clonar repositorio
git clone https://github.com/danioso8/opticaApp.git
cd opticaApp

# Crear entorno virtual
python -m venv .venv
source .venv/bin/activate  # En Windows: .venv\Scripts\activate

# Instalar dependencias
pip install -r requirements.txt

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Ejecutar migraciones
python manage.py migrate

# Crear superusuario
python manage.py createsuperuser

# Iniciar servidor de desarrollo
python manage.py runserver
```

Acceder a: http://localhost:8000

## 📁 Estructura del Proyecto

```
opticaApp/
├── apps/                       # Aplicaciones Django
│   ├── appointments/          # Sistema de citas
│   ├── billing/              # Facturación electrónica
│   ├── dashboard/            # Dashboard principal
│   ├── inventory/            # Control de inventario
│   ├── organizations/        # Multi-tenant
│   ├── patients/             # Gestión de pacientes
│   ├── payroll/              # Nómina electrónica
│   ├── promotions/           # Marketing y promociones
│   ├── public/               # Landing pages públicas
│   ├── sales/                # Punto de venta
│   └── users/                # Autenticación y usuarios
├── config/                    # Configuración Django
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── templates/                 # Templates HTML
├── static/                    # Archivos estáticos
├── whatsapp-server/          # Servidor WhatsApp (Node.js)
├── manage.py
├── requirements.txt
└── .env.example
```

## 🔧 Configuración

### Variables de Entorno Importantes

```bash
# Django
SECRET_KEY=tu-secret-key-segura
DEBUG=True  # False en producción
ALLOWED_HOSTS=localhost,127.0.0.1

# Base de Datos
DATABASE_URL=postgresql://usuario:password@localhost:5432/opticaapp_db

# WhatsApp (Opcional)
TWILIO_ACCOUNT_SID=ACxxxxx
TWILIO_AUTH_TOKEN=xxxxx
TWILIO_WHATSAPP_FROM=whatsapp:+14155238886
```

Ver `.env.example` para todas las opciones.

## 📚 Módulos Destacados

### 💰 Nómina Electrónica

Sistema completo de gestión de nómina con:
- Cálculo automático de devengos y deducciones
- Gestión de incapacidades y préstamos
- Provisiones mensuales
- PDF profesionales de desprendibles
- Reportes PILA

📖 [Documentación completa del módulo de nómina](apps/payroll/README.md)

### 🧾 Facturación Electrónica

- Generación de facturas electrónicas DIAN
- PDFs profesionales con diseño moderno
- Gestión de productos y servicios
- Control de inventario integrado
- Reportes de ventas

### 📱 WhatsApp Business

- Notificaciones automáticas de citas
- Recordatorios personalizables
- Mensajes de seguimiento
- Panel de configuración por organización

## 🛠️ Comandos Útiles

```bash
# Crear migraciones
python manage.py makemigrations

# Aplicar migraciones
python manage.py migrate

# Recoger archivos estáticos
python manage.py collectstatic

# Shell de Django
python manage.py shell

# Crear superusuario
python manage.py createsuperuser

# Ejecutar tests
python manage.py test
```

## 🔐 Seguridad

- Autenticación por organización
- Control de permisos granular
- Encriptación de datos sensibles
- Protección CSRF
- Validación de entrada
- Sesiones seguras

## 🌐 API de WhatsApp

El sistema incluye un servidor Node.js independiente para WhatsApp Business:

```bash
cd whatsapp-server
npm install
node index.js
```

Puerto: 3000  
Endpoint: `http://localhost:3000/api/send-message`

## 📊 Módulo de Inventario

- Control de stock en tiempo real
- Movimientos de entrada/salida
- Gestión por lotes
- Alertas de stock mínimo
- Kardex de productos
- Ajustes de inventario

## 🎯 Planes y Suscripciones

El sistema soporta múltiples planes de suscripción:
- **Básico:** Funcionalidades esenciales
- **Profesional:** Todas las características
- **Empresarial:** Facturación ilimitada

## 🤝 Contribución

Este es un proyecto privado. Para contribuir:
1. Fork del repositorio
2. Crear rama feature (`git checkout -b feature/AmazingFeature`)
3. Commit cambios (`git commit -m 'Add AmazingFeature'`)
4. Push a la rama (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

## 📄 Licencia

Proyecto propietario - Todos los derechos reservados © 2026

## 👤 Autor

**Daniel Osorio**
- GitHub: [@danioso8](https://github.com/danioso8)
- Email: danioso8@gmail.com

## 🗂️ Documentación Adicional

- [Guía de Deployment en Contabo](README_DEPLOYMENT_CONTABO.md)
- [Documentación de Nómina](apps/payroll/README.md)
- [Sistema de WhatsApp](whatsapp-server/README.md)
- [Guía de Despliegue Completa](GUIA_DESPLIEGUE_CONTABO.md)

---

**Última actualización:** Enero 2026  
**Versión:** 2.0  
**Estado:** En producción en Contabo VPS
