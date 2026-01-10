# Módulos Compartidos - OpticaApp

Librería de módulos compartidos entre OpticaApp, PanelGenerador y todas las apps generadas.

## 📁 Estructura

```
shared/
├── __init__.py
├── core/                    # Componentes base
│   ├── __init__.py
│   ├── mixins.py           # Mixins para modelos Django
│   └── validators.py       # Validadores personalizados
├── utils/                   # Utilidades
│   ├── __init__.py
│   ├── formatters.py       # Formateadores de datos
│   ├── generators.py       # Generadores de códigos
│   └── helpers.py          # Funciones helper
└── services/                # Servicios reutilizables
    ├── __init__.py
    ├── email_service.py    # Servicio de email
    └── file_service.py     # Servicio de archivos
```

## 🔵 Core - Componentes Base

### Mixins (`shared.core.mixins`)

**TimeStampedMixin**
- Añade `created_at` y `updated_at` a cualquier modelo
- Uso: `class MyModel(TimeStampedMixin, models.Model)`

**OrganizationMixin**
- Añade relación con organización (multi-tenancy)
- Uso: `class MyModel(OrganizationMixin, models.Model)`

**SoftDeleteMixin**
- Eliminación suave con `is_deleted`, `deleted_at`, `deleted_by`
- Métodos: `soft_delete(user)`, `restore()`

**ActiveMixin**
- Campo `is_active` para activar/desactivar registros

**OrderMixin**
- Campo `order` para ordenamiento manual

### Validadores (`shared.core.validators`)

- `validate_phone()` - Teléfonos colombianos
- `validate_email_custom()` - Email con restricciones
- `validate_nit()` - NIT colombiano
- `validate_cedula()` - Cédula de ciudadanía
- `validate_positive_number()` - Números positivos
- `validate_percentage()` - Valores 0-100
- `validate_non_future_date()` - Fechas no futuras
- `validate_business_hours()` - Horario laboral 6am-10pm

## 🔧 Utils - Utilidades

### Formatters (`shared.utils.formatters`)

```python
from shared.utils import format_currency, format_phone, format_nit

# Moneda
format_currency(1234567)  # "$ 1.234.567"
format_currency(1000, 'USD')  # "US$ 1.000"

# Teléfono
format_phone('3001234567')  # "+57 300 123 4567"

# NIT
format_nit('900123456')  # "900.123.456-7"

# Porcentaje
format_percentage(0.15)  # "15%"
format_percentage(15.5, decimals=1)  # "15.5%"
```

### Generators (`shared.utils.generators`)

```python
from shared.utils import generate_code, generate_token, generate_password

# Código alfanumérico
generate_code(8, prefix='ORD')  # "ORD-A1B2C3D4"

# Token de seguridad
generate_token(32)  # "a1b2c3d4..."

# Contraseña segura
generate_password(12)  # "aB3$xY9!mN2p"

# Código de verificación
generate_verification_code(6)  # "123456"
```

### Helpers (`shared.utils.helpers`)

```python
from shared.utils import get_client_ip, calculate_age, truncate_text

# IP del cliente
ip = get_client_ip(request)

# Calcular edad
edad = calculate_age(fecha_nacimiento)

# Truncar texto
truncate_text("Texto muy largo...", max_length=20)  # "Texto muy largo..."

# División segura
safe_divide(10, 0, default=0)  # 0 (sin error)

# Limpiar diccionario
clean_dict({'a': 1, 'b': None, 'c': ''}, remove_none=True)  # {'a': 1, 'c': ''}
```

## 📧 Services - Servicios

### EmailService (`shared.services.EmailService`)

```python
from shared.services import EmailService

# Email simple
EmailService.send_email(
    to_emails='cliente@example.com',
    subject='Hola',
    html_content='<h1>Mensaje</h1>',
    text_content='Mensaje'
)

# Email con template
EmailService.send_email(
    to_emails='cliente@example.com',
    subject='Bienvenido',
    template_name='emails/welcome.html',
    context={'nombre': 'Juan', 'empresa': 'MiEmpresa'}
)

# Email con template predefinido
EmailService.send_template_email(
    to_emails='paciente@example.com',
    template_key='appointment_reminder',
    context={'cita': cita_obj},
    organization=org
)

# Emails en lote
recipients = [
    {'email': 'user1@example.com', 'context': {'name': 'User 1'}},
    {'email': 'user2@example.com', 'context': {'name': 'User 2'}},
]
result = EmailService.send_bulk_emails(
    recipients_data=recipients,
    subject='Hola {name}',
    template_name='emails/template.html'
)
# result = {'sent': 2, 'failed': 0}
```

### FileService (`shared.services.FileService`)

```python
from shared.services import FileService

# Guardar archivo
path = FileService.save_file(
    file=uploaded_file,
    path='documents/factura.pdf',
    organization_id=1
)

# Eliminar archivo
FileService.delete_file(path)

# URL pública
url = FileService.get_file_url(path)

# Validar extensión
is_valid = FileService.validate_file_extension(
    'documento.pdf',
    allowed_extensions=['.pdf', '.doc', '.docx']
)

# Validar tamaño
is_valid = FileService.validate_file_size(file, max_size_mb=10)

# Hash del archivo
hash_md5 = FileService.calculate_file_hash(file)
```

## 🔄 Sincronización

Los módulos compartidos se sincronizan entre proyectos usando el script:

```bash
# Ver módulos disponibles
python sync_shared_modules.py list

# Ver estado de sincronización
python sync_shared_modules.py status

# Sincronizar a PanelGenerador
python sync_shared_modules.py panel

# Sincronizar a una app específica
python sync_shared_modules.py app DentalApp

# Sincronizar a todas las apps
python sync_shared_modules.py all
```

## 📝 Uso en Modelos

```python
from django.db import models
from shared.core import TimeStampedMixin, OrganizationMixin, SoftDeleteMixin
from shared.core import validate_phone, validate_email_custom

class Cliente(TimeStampedMixin, OrganizationMixin, SoftDeleteMixin, models.Model):
    nombre = models.CharField(max_length=200)
    email = models.EmailField(validators=[validate_email_custom])
    telefono = models.CharField(max_length=20, validators=[validate_phone])
    
    # Hereda automáticamente:
    # - created_at, updated_at (TimeStampedMixin)
    # - organization (OrganizationMixin)
    # - is_deleted, deleted_at, deleted_by (SoftDeleteMixin)
    
    def eliminar_cliente(self, usuario):
        """Elimina el cliente de forma suave"""
        self.soft_delete(user=usuario)
```

## 📝 Uso en Vistas

```python
from shared.utils import format_currency, get_client_ip
from shared.services import EmailService

def crear_factura(request):
    # Obtener IP del cliente
    ip = get_client_ip(request)
    
    # Crear factura
    factura = Factura.objects.create(
        total=100000,
        ip_cliente=ip
    )
    
    # Formatear monto
    total_formateado = format_currency(factura.total)
    
    # Enviar email
    EmailService.send_template_email(
        to_emails=factura.cliente.email,
        template_key='invoice_sent',
        context={
            'factura': factura,
            'total': total_formateado
        },
        organization=request.user.organization
    )
```

## 🆕 Añadir Nuevos Módulos Compartidos

1. Crear el archivo en la carpeta correspondiente:
   - `shared/core/` - Componentes base de Django
   - `shared/utils/` - Utilidades genéricas
   - `shared/services/` - Servicios reutilizables

2. Añadir docstrings completos

3. Actualizar el `__init__.py` de la categoría

4. Sincronizar a todas las apps:
   ```bash
   python sync_shared_modules.py all
   ```

## ⚙️ Actualización de Módulos

Cuando se actualiza un módulo compartido en OpticaApp:

1. Editar el archivo en `OpticaApp/shared/`
2. Ejecutar sincronización:
   ```bash
   python sync_shared_modules.py all
   ```
3. Los cambios se copian automáticamente a:
   - PanelGenerador
   - Todas las apps generadas

## ⚠️ Buenas Prácticas

1. **NO modifiques los módulos compartidos en apps generadas** - siempre edita en OpticaApp
2. **Mantén compatibilidad hacia atrás** - no rompas APIs existentes
3. **Documenta bien** - docstrings completos en todas las funciones
4. **Prueba antes de sincronizar** - asegúrate de que todo funcione
5. **Usa versionado semántico** - para cambios mayores

## 🔖 Versión

**Versión actual:** 1.0.0 (9 de enero 2026)

## 📄 Licencia

Propiedad de CompuEasys - Uso interno
