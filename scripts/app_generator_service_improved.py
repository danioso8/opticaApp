"""
Servicio mejorado para generación de apps con módulos compartidos
USAR ESTE ARCHIVO PARA REEMPLAZAR generador/services.py en PanelGenerador
"""
import os
import shutil
import subprocess
from pathlib import Path
from django.conf import settings
from django.utils.text import slugify
from .models import GeneratedApp, AppModule


class AppGeneratorService:
    """Servicio para generar aplicaciones con módulos compartidos"""
    
    # Módulos que SIEMPRE se copian (compartidos)
    SHARED_MODULES = [
        'shared/core',
        'shared/utils',
        'shared/services',
    ]
    
    # Módulos core que siempre se incluyen
    CORE_MODULES = [
        'organizations',
        'users',
        'dashboard',
        'permissions',
    ]

    @staticmethod
    def create_app(name, app_type, modules, created_by):
        """
        Crea una nueva aplicación
        
        Args:
            name: Nombre de la app
            app_type: Tipo (dental, restaurant, trade, etc.)
            modules: Lista de módulos a incluir
            created_by: Usuario que crea la app
        
        Returns:
            GeneratedApp instance
        """
        slug = slugify(name)

        # Crear registro en BD
        app = GeneratedApp.objects.create(
            name=name,
            slug=slug,
            app_type=app_type,
            domain=f"{slug}.compueasys.com",
            port=AppGeneratorService._get_next_available_port(),
            database_name=f"{slug}_db",
            project_path=os.path.join(settings.APPS_BASE_PATH, name),
            created_by=created_by,
            status='creating'
        )

        try:
            # 1. Copiar template base de OpticaApp
            AppGeneratorService._copy_template(app)
            
            # 2. Copiar módulos compartidos (SIEMPRE)
            AppGeneratorService._copy_shared_modules(app)

            # 3. Configurar módulos seleccionados
            AppGeneratorService._configure_modules(app, modules)
            
            # 4. Personalizar configuración
            AppGeneratorService._customize_settings(app)
            
            # 5. Crear base de datos (opcional - solo en producción)
            # AppGeneratorService._create_database(app)

            # Actualizar estado
            app.status = 'active'
            app.save()

            return app

        except Exception as e:
            app.status = 'error'
            app.save()
            raise e

    @staticmethod
    def _copy_template(app):
        """Copia el template base de OpticaApp"""
        source = settings.OPTICAAPP_TEMPLATE_PATH
        destination = app.project_path

        # Copiar proyecto completo
        if os.path.exists(destination):
            shutil.rmtree(destination)

        shutil.copytree(
            source,
            destination,
            ignore=shutil.ignore_patterns(
                '__pycache__',
                '*.pyc',
                'db.sqlite3',
                '.git',
                '.venv',
                'staticfiles',
                'media',
                'node_modules',
                '*.log'
            )
        )
    
    @staticmethod
    def _copy_shared_modules(app):
        """
        Copia los módulos compartidos desde OpticaApp
        Estos módulos se sincronizan y actualizan automáticamente
        """
        source_base = Path(settings.OPTICAAPP_TEMPLATE_PATH)
        dest_base = Path(app.project_path)
        
        for module_path in AppGeneratorService.SHARED_MODULES:
            source = source_base / module_path
            dest = dest_base / module_path
            
            if source.exists():
                # Eliminar si existe
                if dest.exists():
                    shutil.rmtree(dest)
                
                # Copiar módulo compartido
                shutil.copytree(source, dest)
        
        # Copiar __init__.py de shared
        source_init = source_base / 'shared' / '__init__.py'
        dest_init = dest_base / 'shared' / '__init__.py'
        
        if source_init.exists():
            dest_init.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_init, dest_init)

    @staticmethod
    def _configure_modules(app, modules):
        """Configura los módulos seleccionados"""
        # Añadir módulos core (siempre)
        all_modules = set(AppGeneratorService.CORE_MODULES + modules)
        
        for module_name in all_modules:
            AppModule.objects.create(
                app=app,
                module_name=module_name,
                is_active=True
            )
    
    @staticmethod
    def _customize_settings(app):
        """
        Personaliza el archivo settings.py de la app generada
        """
        settings_file = Path(app.project_path) / 'config' / 'settings.py'
        
        if not settings_file.exists():
            return
        
        # Leer settings actual
        with open(settings_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # Reemplazar valores
        replacements = {
            'SECRET_KEY = ': f"SECRET_KEY = '{AppGeneratorService._generate_secret_key()}'",
            'DEBUG = True': 'DEBUG = False' if settings.DEBUG == False else 'DEBUG = True',
            "NAME': 'opticaapp_db'": f"NAME': '{app.database_name}'",
        }
        
        for old, new in replacements.items():
            if old in content:
                content = content.replace(old, new)
        
        # Guardar cambios
        with open(settings_file, 'w', encoding='utf-8') as f:
            f.write(content)
    
    @staticmethod
    def _generate_secret_key():
        """Genera una SECRET_KEY única para Django"""
        from django.core.management.utils import get_random_secret_key
        return get_random_secret_key()
    
    @staticmethod
    def _get_next_available_port():
        """Obtiene el siguiente puerto disponible"""
        # Obtener el puerto más alto usado
        last_app = GeneratedApp.objects.order_by('-port').first()
        
        if last_app:
            return last_app.port + 1
        else:
            return 8002  # Empezar desde 8002 (8001 es el panel)
    
    @staticmethod
    def _create_database(app):
        """
        Crea la base de datos PostgreSQL para la app
        SOLO PARA PRODUCCIÓN
        """
        # Este comando requiere permisos de PostgreSQL
        commands = [
            f"CREATE DATABASE {app.database_name};",
            f"CREATE USER {app.slug}_user WITH PASSWORD '{app.slug}_pass';",
            f"GRANT ALL PRIVILEGES ON DATABASE {app.database_name} TO {app.slug}_user;",
        ]
        
        # TODO: Implementar con subprocess si estamos en producción
        pass
    
    @staticmethod
    def update_shared_modules(app):
        """
        Actualiza los módulos compartidos de una app existente
        """
        try:
            AppGeneratorService._copy_shared_modules(app)
            return True
        except Exception as e:
            print(f"Error actualizando módulos compartidos: {e}")
            return False
    
    @staticmethod
    def add_module_to_app(app, module_name):
        """
        Añade un módulo a una app existente
        
        Args:
            app: GeneratedApp instance
            module_name: Nombre del módulo a añadir
        """
        source_base = Path(settings.OPTICAAPP_TEMPLATE_PATH)
        dest_base = Path(app.project_path)
        
        # Copiar el módulo desde OpticaApp
        source_module = source_base / 'apps' / module_name
        dest_module = dest_base / 'apps' / module_name
        
        if not source_module.exists():
            raise ValueError(f"Módulo {module_name} no existe en OpticaApp")
        
        # Copiar módulo
        if dest_module.exists():
            shutil.rmtree(dest_module)
        
        shutil.copytree(source_module, dest_module)
        
        # Registrar en BD
        AppModule.objects.get_or_create(
            app=app,
            module_name=module_name,
            defaults={'is_active': True}
        )
        
        return True
    
    @staticmethod
    def remove_module_from_app(app, module_name):
        """
        Remueve un módulo de una app existente
        NO elimina archivos, solo lo marca como inactivo
        """
        try:
            module = AppModule.objects.get(app=app, module_name=module_name)
            module.is_active = False
            module.save()
            return True
        except AppModule.DoesNotExist:
            return False
    
    @staticmethod
    def list_available_modules():
        """
        Lista todos los módulos disponibles en OpticaApp
        """
        source_apps = Path(settings.OPTICAAPP_TEMPLATE_PATH) / 'apps'
        
        if not source_apps.exists():
            return []
        
        modules = []
        for item in source_apps.iterdir():
            if item.is_dir() and not item.name.startswith('_'):
                modules.append(item.name)
        
        return sorted(modules)
