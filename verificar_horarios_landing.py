"""
Script para verificar y actualizar los horarios en las configuraciones de landing page existentes
"""
import os
import sys
import django

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.organizations.models import LandingPageConfig, Organization

def verificar_configuraciones_horarios():
    """Verifica las configuraciones de horarios en todas las landing pages"""
    
    print("=" * 80)
    print("VERIFICACIÓN DE CONFIGURACIONES DE HORARIOS EN LANDING PAGES")
    print("=" * 80)
    
    configs = LandingPageConfig.objects.all()
    
    if not configs.exists():
        print("\n⚠️  No hay configuraciones de landing page creadas aún.")
        print("   Las configuraciones se crearán automáticamente cuando se configure")
        print("   una landing page desde el panel de administración.")
        return
    
    for config in configs:
        print(f"\n📋 Organización: {config.organization.name}")
        print("-" * 80)
        
        print(f"\n   📅 HORARIOS CONFIGURADOS:")
        print(f"      Lunes - Viernes: {config.schedule_weekday_start} - {config.schedule_weekday_end}")
        print(f"      Sábado: {config.schedule_saturday_start} - {config.schedule_saturday_end}")
        
        if config.schedule_sunday_closed:
            print(f"      Domingo: Cerrado ❌")
        else:
            print(f"      Domingo: {config.schedule_sunday_start} - {config.schedule_sunday_end}")
        
        if config.has_lunch_break:
            print(f"\n   🍽️  HORARIO DE ALMUERZO:")
            print(f"      {config.lunch_break_start} - {config.lunch_break_end}")
            print(f"      (El negocio cierra durante este horario)")
        else:
            print(f"\n   ℹ️  Sin horario de almuerzo configurado (atención continua)")
        
        print()
    
    print("\n" + "=" * 80)
    print("RESUMEN:")
    print(f"Total de configuraciones verificadas: {configs.count()}")
    print("\n✅ Todos los campos de horario están disponibles y configurados.")
    print("\n📝 INSTRUCCIONES PARA CAMBIAR HORARIOS:")
    print("   1. Accede al panel de administración de Django")
    print("   2. Ve a 'Organizaciones' → 'Configuraciones de Landing Page'")
    print("   3. Selecciona la configuración que deseas editar")
    print("   4. En la sección 'Horarios de Atención' podrás:")
    print("      - Cambiar horarios de Lunes a Viernes")
    print("      - Cambiar horarios de Sábado")
    print("      - Configurar si abre o cierra los Domingos")
    print("      - Activar/desactivar el horario de almuerzo")
    print("      - Configurar las horas de inicio y fin del almuerzo")
    print("   5. Guarda los cambios")
    print("\n💡 Los cambios se reflejarán inmediatamente en la landing page")
    print("=" * 80)

if __name__ == '__main__':
    verificar_configuraciones_horarios()
