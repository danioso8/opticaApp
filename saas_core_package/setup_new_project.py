"""
SaaS Core Package - Setup Script
Autor: Daniel (danioso8)
Fecha: 30 de diciembre de 2024

Este script automatiza la creación de un nuevo proyecto SaaS
usando la configuración base de OpticaApp.
"""

import os
import json
import shutil
from pathlib import Path

class SaaSProjectGenerator:
    def __init__(self, config_file):
        """Inicializa el generador con un archivo de configuración"""
        self.config_file = config_file
        self.config = self.load_config()
        self.project_name = self.config.get('project_name', 'NewSaaSApp')
        
    def load_config(self):
        """Carga el archivo de configuración JSON"""
        with open(self.config_file, 'r', encoding='utf-8') as f:
            return json.load(f)
    
    def create_project_structure(self, target_dir):
        """Crea la estructura base del proyecto"""
        print(f"📁 Creando estructura de proyecto en {target_dir}...")
        
        # Crear directorios principales
        dirs = [
            f"{target_dir}/apps/users",
            f"{target_dir}/apps/organizations",
            f"{target_dir}/apps/dashboard",
            f"{target_dir}/apps/billing",
            f"{target_dir}/config",
            f"{target_dir}/static",
            f"{target_dir}/media",
            f"{target_dir}/templates",
        ]
        
        for dir_path in dirs:
            os.makedirs(dir_path, exist_ok=True)
            print(f"  ✅ {dir_path}")
    
    def copy_core_files(self, source_dir, target_dir):
        """Copia archivos core desde OpticaApp"""
        print(f"\n📋 Copiando archivos core...")
        
        # Lista de archivos a copiar (funcionalidad común)
        core_files = [
            # Users app
            ('apps/users/models.py', 'apps/users/models.py'),
            ('apps/users/views.py', 'apps/users/views.py'),
            ('apps/users/payment_views.py', 'apps/users/payment_views.py'),
            ('apps/users/wompi_service.py', 'apps/users/wompi_service.py'),
            ('apps/users/urls.py', 'apps/users/urls.py'),
            ('apps/users/forms.py', 'apps/users/forms.py'),
            
            # Organizations app
            ('apps/organizations/models.py', 'apps/organizations/models.py'),
            ('apps/organizations/middleware.py', 'apps/organizations/middleware.py'),
            ('apps/organizations/plan_features.py', 'apps/organizations/plan_features.py'),
            ('apps/organizations/decorators.py', 'apps/organizations/decorators.py'),
            ('apps/organizations/views.py', 'apps/organizations/views.py'),
            
            # Config
            ('config/settings.py', 'config/settings.py'),
            ('config/urls.py', 'config/urls.py'),
            ('config/wsgi.py', 'config/wsgi.py'),
        ]
        
        for source, target in core_files:
            src_path = os.path.join(source_dir, source)
            tgt_path = os.path.join(target_dir, target)
            
            if os.path.exists(src_path):
                os.makedirs(os.path.dirname(tgt_path), exist_ok=True)
                shutil.copy2(src_path, tgt_path)
                print(f"  ✅ {source}")
            else:
                print(f"  ⚠️  No encontrado: {source}")
    
    def copy_templates(self, source_dir, target_dir):
        """Copia templates HTML"""
        print(f"\n🎨 Copiando templates...")
        
        template_dirs = [
            'apps/users/templates',
            'apps/organizations/templates',
            'apps/dashboard/templates',
        ]
        
        for template_dir in template_dirs:
            src_path = os.path.join(source_dir, template_dir)
            tgt_path = os.path.join(target_dir, template_dir)
            
            if os.path.exists(src_path):
                try:
                    shutil.copytree(src_path, tgt_path, dirs_exist_ok=True)
                    print(f"  ✅ {template_dir}")
                except Exception as e:
                    print(f"  ⚠️  Error copiando {template_dir}: {e}")
    
    def copy_management_commands(self, source_dir, target_dir):
        """Copia comandos de management (cron jobs)"""
        print(f"\n⚙️  Copiando comandos de management...")
        
        commands = [
            'apps/users/management/commands/renew_subscriptions.py',
            'apps/users/management/commands/send_renewal_reminders.py',
            'apps/users/management/commands/check_trial_expiration.py',
        ]
        
        for command in commands:
            src_path = os.path.join(source_dir, command)
            tgt_path = os.path.join(target_dir, command)
            
            if os.path.exists(src_path):
                os.makedirs(os.path.dirname(tgt_path), exist_ok=True)
                shutil.copy2(src_path, tgt_path)
                print(f"  ✅ {command}")
            else:
                print(f"  ⚠️  No encontrado: {command}")
    
    def generate_plan_features(self, target_dir):
        """Genera plan_features.py personalizado desde la configuración"""
        print(f"\n🔧 Generando plan_features.py personalizado...")
        
        modules = self.config.get('modules', {})
        plans = self.config.get('subscription_plans', [])
        
        # Generar MODULES dict
        modules_code = "MODULES = {\n"
        for module_code, module_data in modules.items():
            modules_code += f"    '{module_code}': {{\n"
            modules_code += f"        'name': '{module_data['name']}',\n"
            modules_code += f"        'icon': '{module_data['icon']}',\n"
            modules_code += f"        'description': '{module_data['description']}',\n"
            modules_code += f"    }},\n"
        modules_code += "}\n\n"
        
        # Generar PLAN_MODULES dict
        plan_modules_code = "PLAN_MODULES = {\n"
        for plan in plans:
            plan_code = plan['code']
            plan_modules = plan.get('modules', [])
            plan_modules_code += f"    '{plan_code}': {plan_modules},\n"
        plan_modules_code += "}\n"
        
        # Template completo del archivo
        full_code = f'''"""
Configuración de Módulos y Planes - {self.project_name}
Generado automáticamente desde configuración
Autor: {self.config.get('developer', 'Unknown')}
"""

{modules_code}
{plan_modules_code}

def has_module_access(user, module_code):
    """Verifica si el usuario tiene acceso a un módulo"""
    if user.is_superuser:
        return True
    
    try:
        subscription = user.usersubscription_set.filter(
            is_active=True
        ).first()
        
        if not subscription:
            return False
        
        plan_code = subscription.plan.code
        allowed_modules = PLAN_MODULES.get(plan_code, [])
        
        return module_code in allowed_modules
    except:
        return False

def get_user_modules(user):
    """Retorna la lista de módulos disponibles para el usuario"""
    if user.is_superuser:
        return list(MODULES.keys())
    
    try:
        subscription = user.usersubscription_set.filter(
            is_active=True
        ).first()
        
        if not subscription:
            return []
        
        plan_code = subscription.plan.code
        return PLAN_MODULES.get(plan_code, [])
    except:
        return []

def get_module_info(module_code):
    """Retorna información de un módulo específico"""
    return MODULES.get(module_code, {{}})
'''
        
        # Escribir archivo
        output_path = os.path.join(target_dir, 'apps/organizations/plan_features.py')
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(full_code)
        
        print(f"  ✅ Generado: apps/organizations/plan_features.py")
    
    def generate_requirements(self, target_dir):
        """Genera requirements.txt"""
        print(f"\n📦 Generando requirements.txt...")
        
        requirements = [
            "Django>=3.2,<4.0",
            "djangorestframework>=3.12",
            "psycopg2-binary>=2.9",
            "python-decouple>=3.6",
            "requests>=2.28",
            "Pillow>=9.0",
            "gunicorn>=20.1",
            "whitenoise>=6.0",
        ]
        
        # Agregar integraciones según config
        integrations = self.config.get('integrations', {})
        
        if integrations.get('twilio_whatsapp', {}).get('enabled'):
            requirements.append("twilio>=7.0")
        
        requirements_path = os.path.join(target_dir, 'requirements.txt')
        
        with open(requirements_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(requirements))
        
        print(f"  ✅ requirements.txt generado")
    
    def generate_env_template(self, target_dir):
        """Genera .env.example con variables necesarias"""
        print(f"\n🔐 Generando .env.example...")
        
        env_vars = [
            "# Django Configuration",
            "DEBUG=True",
            "SECRET_KEY=your-secret-key-here",
            "ALLOWED_HOSTS=localhost,127.0.0.1",
            "",
            "# Database",
            "DATABASE_URL=sqlite:///db.sqlite3",
            "",
        ]
        
        # Wompi
        if self.config.get('integrations', {}).get('wompi', {}).get('enabled'):
            env_vars.extend([
                "# Wompi Payment Gateway",
                "WOMPI_PUBLIC_KEY=pub_test_xxxxx",
                "WOMPI_PRIVATE_KEY=prv_test_xxxxx",
                "WOMPI_EVENTS_SECRET=xxxxx",
                "WOMPI_INTEGRITY_SECRET=xxxxx",
                "WOMPI_TEST_MODE=True",
                "",
            ])
        
        # WhatsApp
        if self.config.get('integrations', {}).get('twilio_whatsapp', {}).get('enabled'):
            env_vars.extend([
                "# Twilio WhatsApp",
                "TWILIO_ACCOUNT_SID=ACxxxxx",
                "TWILIO_AUTH_TOKEN=xxxxx",
                "TWILIO_WHATSAPP_FROM=whatsapp:+14155238886",
                "",
            ])
        
        # Email
        if self.config.get('integrations', {}).get('email', {}).get('enabled'):
            env_vars.extend([
                "# Email Configuration",
                "EMAIL_HOST=smtp.gmail.com",
                "EMAIL_PORT=587",
                "EMAIL_USE_TLS=True",
                "EMAIL_HOST_USER=your-email@gmail.com",
                "EMAIL_HOST_PASSWORD=your-app-password",
                "DEFAULT_FROM_EMAIL=noreply@yourapp.com",
                "",
            ])
        
        env_path = os.path.join(target_dir, '.env.example')
        
        with open(env_path, 'w', encoding='utf-8') as f:
            f.write('\n'.join(env_vars))
        
        print(f"  ✅ .env.example generado")
    
    def generate_readme(self, target_dir):
        """Genera README.md personalizado"""
        print(f"\n📖 Generando README.md...")
        
        readme_content = f"""# {self.project_name}

**Desarrollador**: {self.config.get('developer', 'Unknown')}  
**Industria**: {self.config.get('industry', 'general')}  
**Base**: OpticaApp SaaS Core  

## 🚀 Descripción

Sistema SaaS multi-tenant para {self.config.get('industry', 'negocios')} con las siguientes características:

### ✨ Funcionalidades Core
- ✅ Multi-tenancy (múltiples organizaciones)
- ✅ Sistema de suscripciones con {len(self.config.get('subscription_plans', []))} planes
- ✅ Trial de {self.config.get('core_features', {}).get('trial_system', {}).get('duration_days', 90)} días
- ✅ Renovación automática
- ✅ Pagos con Wompi (Colombia)
- ✅ Notificaciones WhatsApp
- ✅ Verificación de email
- ✅ Landing pages personalizables
- ✅ Facturación electrónica DIAN

### 📋 Módulos Disponibles
"""
        
        # Agregar módulos por plan
        for plan in self.config.get('subscription_plans', []):
            readme_content += f"\n**{plan['name']}** (${plan['price_usd']} USD/mes):\n"
            for module_code in plan.get('modules', []):
                module_info = self.config.get('modules', {}).get(module_code, {})
                readme_content += f"- {module_info.get('name', module_code)}\n"
        
        readme_content += f"""
## 🛠️ Instalación

### 1. Clonar el proyecto
```bash
cd {self.project_name}
```

### 2. Crear entorno virtual
```bash
python -m venv .venv
.venv\\Scripts\\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

### 3. Instalar dependencias
```bash
pip install -r requirements.txt
```

### 4. Configurar variables de entorno
```bash
cp .env.example .env
# Editar .env con tus credenciales
```

### 5. Migraciones
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 6. Ejecutar servidor
```bash
python manage.py runserver
```

## 🔧 Configuración

### Wompi (Pagos)
1. Crear cuenta en https://wompi.co
2. Obtener claves API (producción y sandbox)
3. Agregar en `.env`

### Twilio (WhatsApp)
1. Crear cuenta en https://twilio.com
2. Activar WhatsApp sandbox
3. Agregar credenciales en `.env`

### DIAN (Facturación Electrónica)
1. Obtener certificado digital
2. Configurar resolución de facturación
3. Subir certificado en admin

## 📞 Soporte

Desarrollado por: {self.config.get('developer', 'Unknown')}

---

**Generado con SaaS Core Package - OpticaApp Base**
"""
        
        readme_path = os.path.join(target_dir, 'README.md')
        
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(readme_content)
        
        print(f"  ✅ README.md generado")
    
    def run(self, source_dir, target_dir):
        """Ejecuta el proceso completo de generación"""
        print(f"\n{'='*60}")
        print(f"  🚀 SaaS Project Generator")
        print(f"  Proyecto: {self.project_name}")
        print(f"  Industria: {self.config.get('industry', 'general')}")
        print(f"{'='*60}\n")
        
        self.create_project_structure(target_dir)
        self.copy_core_files(source_dir, target_dir)
        self.copy_templates(source_dir, target_dir)
        self.copy_management_commands(source_dir, target_dir)
        self.generate_plan_features(target_dir)
        self.generate_requirements(target_dir)
        self.generate_env_template(target_dir)
        self.generate_readme(target_dir)
        
        print(f"\n{'='*60}")
        print(f"  ✅ Proyecto generado exitosamente!")
        print(f"  📁 Ubicación: {target_dir}")
        print(f"{'='*60}\n")
        
        print("📝 Próximos pasos:")
        print(f"  1. cd {target_dir}")
        print("  2. python -m venv .venv")
        print("  3. .venv\\Scripts\\activate")
        print("  4. pip install -r requirements.txt")
        print("  5. cp .env.example .env")
        print("  6. python manage.py migrate")
        print("  7. python manage.py runserver")


def main():
    """Función principal"""
    import sys
    
    if len(sys.argv) < 3:
        print("Uso: python setup_new_project.py <config_file> <target_directory>")
        print("\nEjemplos:")
        print("  python setup_new_project.py templates/inmobiliaria_config.json ../InmobiliariaApp")
        print("  python setup_new_project.py templates/compraventa_config.json ../CompraVentaApp")
        sys.exit(1)
    
    config_file = sys.argv[1]
    target_dir = sys.argv[2]
    
    # Directorio fuente (OpticaApp)
    source_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    # Validar que existe el archivo de configuración
    if not os.path.exists(config_file):
        print(f"❌ Error: No se encontró el archivo {config_file}")
        sys.exit(1)
    
    # Crear generador y ejecutar
    generator = SaaSProjectGenerator(config_file)
    generator.run(source_dir, target_dir)


if __name__ == '__main__':
    main()
