"""
Script de sincronización de módulos compartidos
Copia los módulos compartidos de OpticaApp a PanelGenerador y apps generadas
"""
import os
import shutil
from pathlib import Path


class SharedModulesSyncer:
    """Sincronizador de módulos compartidos"""
    
    OPTICAAPP_PATH = Path(r"D:\ESCRITORIO\OpticaApp")
    PANEL_GENERADOR_PATH = Path(r"D:\ESCRITORIO\PanelGenerador")
    APPS_BASE_PATH = Path(r"D:\ESCRITORIO")
    
    SHARED_MODULES = [
        'shared/core',
        'shared/utils', 
        'shared/services',
    ]
    
    @classmethod
    def sync_to_panel_generador(cls):
        """Sincroniza módulos compartidos al PanelGenerador"""
        print("🔄 Sincronizando módulos compartidos a PanelGenerador...")
        
        source_base = cls.OPTICAAPP_PATH
        dest_base = cls.PANEL_GENERADOR_PATH
        
        if not dest_base.exists():
            print(f"❌ PanelGenerador no encontrado en {dest_base}")
            return False
        
        for module_path in cls.SHARED_MODULES:
            source = source_base / module_path
            dest = dest_base / module_path
            
            if not source.exists():
                print(f"⚠️  Fuente no existe: {source}")
                continue
            
            # Eliminar destino si existe
            if dest.exists():
                shutil.rmtree(dest)
            
            # Copiar módulo
            shutil.copytree(source, dest)
            print(f"✅ Copiado: {module_path}")
        
        # Copiar __init__.py del shared
        source_init = source_base / 'shared' / '__init__.py'
        dest_init = dest_base / 'shared' / '__init__.py'
        
        if source_init.exists():
            dest_init.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_init, dest_init)
            print(f"✅ Copiado: shared/__init__.py")
        
        print("✅ Sincronización a PanelGenerador completada\n")
        return True
    
    @classmethod
    def sync_to_generated_app(cls, app_name):
        """
        Sincroniza módulos compartidos a una app generada
        
        Args:
            app_name: Nombre de la app generada
        """
        print(f"🔄 Sincronizando módulos compartidos a {app_name}...")
        
        source_base = cls.OPTICAAPP_PATH
        dest_base = cls.APPS_BASE_PATH / app_name
        
        if not dest_base.exists():
            print(f"❌ App {app_name} no encontrada en {dest_base}")
            return False
        
        for module_path in cls.SHARED_MODULES:
            source = source_base / module_path
            dest = dest_base / module_path
            
            if not source.exists():
                print(f"⚠️  Fuente no existe: {source}")
                continue
            
            # Eliminar destino si existe
            if dest.exists():
                shutil.rmtree(dest)
            
            # Copiar módulo
            shutil.copytree(source, dest)
            print(f"✅ Copiado a {app_name}: {module_path}")
        
        # Copiar __init__.py del shared
        source_init = source_base / 'shared' / '__init__.py'
        dest_init = dest_base / 'shared' / '__init__.py'
        
        if source_init.exists():
            dest_init.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(source_init, dest_init)
            print(f"✅ Copiado a {app_name}: shared/__init__.py")
        
        print(f"✅ Sincronización a {app_name} completada\n")
        return True
    
    @classmethod
    def sync_to_all_generated_apps(cls):
        """Sincroniza a todas las apps generadas"""
        print("🔄 Buscando apps generadas...")
        
        synced = 0
        failed = 0
        
        # Buscar apps en el directorio base
        for item in cls.APPS_BASE_PATH.iterdir():
            if not item.is_dir():
                continue
            
            # Saltar OpticaApp y PanelGenerador
            if item.name in ['OpticaApp', 'PanelGenerador']:
                continue
            
            # Verificar si tiene manage.py (es una app Django)
            if (item / 'manage.py').exists():
                if cls.sync_to_generated_app(item.name):
                    synced += 1
                else:
                    failed += 1
        
        print(f"\n📊 Resumen:")
        print(f"  ✅ Apps sincronizadas: {synced}")
        print(f"  ❌ Apps fallidas: {failed}")
        
        return synced, failed
    
    @classmethod
    def list_shared_modules(cls):
        """Lista todos los módulos compartidos disponibles"""
        print("📦 Módulos compartidos disponibles:\n")
        
        source_base = cls.OPTICAAPP_PATH / 'shared'
        
        if not source_base.exists():
            print("❌ Carpeta shared/ no existe")
            return
        
        for category in ['core', 'utils', 'services']:
            category_path = source_base / category
            if not category_path.exists():
                continue
            
            print(f"\n🔹 {category.upper()}:")
            for file in category_path.glob('*.py'):
                if file.name == '__init__.py':
                    continue
                
                # Leer primera línea de docstring
                try:
                    with open(file, 'r', encoding='utf-8') as f:
                        lines = f.readlines()
                        docstring = None
                        for line in lines:
                            if '"""' in line or "'''" in line:
                                docstring = line.strip().strip('"""').strip("'''")
                                break
                        
                        if docstring:
                            print(f"  • {file.stem}.py - {docstring}")
                        else:
                            print(f"  • {file.stem}.py")
                except:
                    print(f"  • {file.stem}.py")
    
    @classmethod
    def check_sync_status(cls):
        """Verifica el estado de sincronización"""
        print("🔍 Verificando estado de sincronización...\n")
        
        # Verificar PanelGenerador
        print("📍 PanelGenerador:")
        panel_shared = cls.PANEL_GENERADOR_PATH / 'shared'
        if panel_shared.exists():
            print("  ✅ Carpeta shared/ existe")
            for category in ['core', 'utils', 'services']:
                if (panel_shared / category).exists():
                    print(f"  ✅ {category}/ sincronizado")
                else:
                    print(f"  ❌ {category}/ NO sincronizado")
        else:
            print("  ❌ Carpeta shared/ NO existe")
        
        # Verificar apps generadas
        print("\n📍 Apps generadas:")
        found_apps = 0
        for item in cls.APPS_BASE_PATH.iterdir():
            if not item.is_dir() or item.name in ['OpticaApp', 'PanelGenerador']:
                continue
            
            if (item / 'manage.py').exists():
                found_apps += 1
                app_shared = item / 'shared'
                status = "✅" if app_shared.exists() else "❌"
                print(f"  {status} {item.name}")
        
        if found_apps == 0:
            print("  ℹ️  No hay apps generadas aún")


def main():
    """Función principal"""
    import sys
    
    syncer = SharedModulesSyncer()
    
    if len(sys.argv) < 2:
        print("=" * 60)
        print("  SINCRONIZADOR DE MÓDULOS COMPARTIDOS")
        print("=" * 60)
        print("\nUso:")
        print("  python sync_shared_modules.py <comando> [opciones]")
        print("\nComandos disponibles:")
        print("  list         - Listar módulos compartidos")
        print("  status       - Verificar estado de sincronización")
        print("  panel        - Sincronizar a PanelGenerador")
        print("  app <nombre> - Sincronizar a app específica")
        print("  all          - Sincronizar a todas las apps")
        print("\nEjemplos:")
        print("  python sync_shared_modules.py list")
        print("  python sync_shared_modules.py panel")
        print("  python sync_shared_modules.py app DentalApp")
        print("  python sync_shared_modules.py all")
        print("=" * 60)
        return
    
    command = sys.argv[1].lower()
    
    if command == 'list':
        syncer.list_shared_modules()
    
    elif command == 'status':
        syncer.check_sync_status()
    
    elif command == 'panel':
        syncer.sync_to_panel_generador()
    
    elif command == 'app':
        if len(sys.argv) < 3:
            print("❌ Error: Especifica el nombre de la app")
            print("Uso: python sync_shared_modules.py app <nombre>")
            return
        
        app_name = sys.argv[2]
        syncer.sync_to_generated_app(app_name)
    
    elif command == 'all':
        print("🚀 Sincronizando a TODAS las apps...\n")
        syncer.sync_to_panel_generador()
        syncer.sync_to_all_generated_apps()
    
    else:
        print(f"❌ Comando desconocido: {command}")
        print("Usa: python sync_shared_modules.py (sin argumentos) para ver ayuda")


if __name__ == '__main__':
    main()
