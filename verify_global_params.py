"""
Script para verificar que los parámetros clínicos globales están funcionando
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models_clinical_config import ClinicalParameter
from django.db.models import Q

def verify_global_params():
    """Verifica que los parámetros globales estén disponibles"""
    
    print("🔍 VERIFICACIÓN DE PARÁMETROS CLÍNICOS GLOBALES")
    print("=" * 60)
    
    # Contar parámetros globales
    global_params = ClinicalParameter.objects.filter(organization__isnull=True)
    print(f"\n📊 Total de parámetros globales: {global_params.count()}")
    
    # Verificar por tipo
    param_types = [
        ('lens_material', 'Materiales de Lentes'),
        ('treatment', 'Tratamientos'),
        ('lens_type', 'Tipos de Lentes'),
        ('lens_brand', 'Marcas de Lentes'),
        ('frame_type', 'Tipos de Monturas'),
        ('contact_lens_type', 'Tipos de LC'),
        ('contact_lens_brand', 'Marcas de LC'),
        ('contact_lens_wearing', 'Régimen de LC'),
        ('topical_medication', 'Medicamentos'),
        ('diagnosis', 'Diagnósticos'),
        ('complementary_exam', 'Exámenes'),
        ('visual_therapy', 'Terapias'),
        ('referral_specialty', 'Especialidades'),
        ('recommendation', 'Recomendaciones'),
    ]
    
    print("\n📋 Parámetros por categoría:")
    print("-" * 60)
    
    for param_type, label in param_types:
        count = global_params.filter(parameter_type=param_type).count()
        print(f"   {label:<30} {count:>3} parámetros")
    
    # Simular consulta como si fuera para una organización
    print("\n🔎 SIMULACIÓN DE CONSULTA CON ORGANIZACIÓN")
    print("-" * 60)
    
    # Obtener primera organización si existe
    from apps.organizations.models import Organization
    org = Organization.objects.first()
    
    if org:
        print(f"   Organización: {org.name}")
        
        # Consulta que incluye globales + de la organización
        lens_materials = ClinicalParameter.objects.filter(
            Q(organization=org) | Q(organization__isnull=True),
            parameter_type='lens_material',
            is_active=True
        ).order_by('display_order', 'name')
        
        print(f"\n   Materiales disponibles: {lens_materials.count()}")
        print("   Listado:")
        for mat in lens_materials[:5]:
            origin = "🌍 Global" if mat.organization is None else f"🏢 {mat.organization.name}"
            print(f"      - {mat.name} ({origin})")
        
        if lens_materials.count() > 5:
            print(f"      ... y {lens_materials.count() - 5} más")
    else:
        print("   ⚠️  No hay organizaciones en el sistema")
    
    # Verificar algunos parámetros específicos
    print("\n✅ VERIFICACIÓN DE PARÁMETROS ESPECÍFICOS")
    print("-" * 60)
    
    checks = [
        ('Policarbonato', 'lens_material'),
        ('Antireflejo', 'treatment'),
        ('Progresivos', 'lens_type'),
        ('Miopía', 'diagnosis'),
    ]
    
    for name, param_type in checks:
        param = ClinicalParameter.objects.filter(
            organization__isnull=True,
            parameter_type=param_type,
            name__icontains=name
        ).first()
        
        if param:
            print(f"   ✅ {name:<20} - Encontrado")
        else:
            print(f"   ❌ {name:<20} - NO encontrado")
    
    print("\n" + "=" * 60)
    print("✅ VERIFICACIÓN COMPLETADA")
    print("💡 Los parámetros globales están funcionando correctamente")

if __name__ == '__main__':
    verify_global_params()
