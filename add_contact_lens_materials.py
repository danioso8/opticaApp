"""
Script para agregar materiales de lentes de contacto
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models_clinical_config import ClinicalParameter

def add_contact_lens_materials():
    """Agregar materiales de lentes de contacto globales"""
    
    print("🔧 Agregando materiales de lentes de contacto...")
    print("=" * 60)
    
    # Verificar si ya existen
    existing = ClinicalParameter.objects.filter(
        organization__isnull=True,
        parameter_type='contact_lens_material'
    ).count()
    
    if existing > 0:
        print(f"⚠️  Ya existen {existing} materiales de LC. ¿Deseas reemplazarlos? (si/no): ", end='')
        response = input()
        if response.lower() == 'si':
            ClinicalParameter.objects.filter(
                organization__isnull=True,
                parameter_type='contact_lens_material'
            ).delete()
            print(f"   ✅ Eliminados {existing} materiales existentes")
        else:
            print("   ❌ Operación cancelada")
            return
    
    # Materiales de lentes de contacto
    contact_lens_materials = [
        {
            'name': 'Hidrogel',
            'code': 'HYDRO',
            'description': 'Material tradicional, contenido de agua 38-75%',
            'category': 'Hidrogel',
            'display_order': 1
        },
        {
            'name': 'Hidrogel de Silicona',
            'code': 'SIHYD',
            'description': 'Alta permeabilidad al oxígeno, uso prolongado',
            'category': 'Silicona',
            'display_order': 2
        },
        {
            'name': 'HEMA (Polihidroxietilmetacrilato)',
            'code': 'HEMA',
            'description': 'Material blando estándar, bajo contenido de agua',
            'category': 'Hidrogel',
            'display_order': 3
        },
        {
            'name': 'PMMA (Polimetilmetacrilato)',
            'code': 'PMMA',
            'description': 'Material rígido tradicional, no permeable al gas',
            'category': 'Rígido',
            'display_order': 4
        },
        {
            'name': 'RGP - Gas Permeable',
            'code': 'RGP',
            'description': 'Rígido permeable al oxígeno, mejor visión',
            'category': 'Rígido',
            'display_order': 5
        },
        {
            'name': 'Silicona Pura',
            'code': 'SILI',
            'description': 'Alta transmisibilidad al oxígeno',
            'category': 'Silicona',
            'display_order': 6
        },
        {
            'name': 'Lotrafilcon A',
            'code': 'LOTRA',
            'description': 'Silicona hidrogel, marca Air Optix',
            'category': 'Silicona',
            'display_order': 7
        },
        {
            'name': 'Lotrafilcon B',
            'code': 'LOTRB',
            'description': 'Silicona hidrogel, marca Air Optix Aqua',
            'category': 'Silicona',
            'display_order': 8
        },
        {
            'name': 'Comfilcon A',
            'code': 'COMF',
            'description': 'Silicona hidrogel, marca Biofinity',
            'category': 'Silicona',
            'display_order': 9
        },
        {
            'name': 'Etafilcon A',
            'code': 'ETAF',
            'description': 'Hidrogel, marca Acuvue 2',
            'category': 'Hidrogel',
            'display_order': 10
        },
        {
            'name': 'Narafilcon A',
            'code': 'NARA',
            'description': 'Silicona hidrogel, marca Acuvue Oasys',
            'category': 'Silicona',
            'display_order': 11
        },
        {
            'name': 'Senofilcon A',
            'code': 'SENO',
            'description': 'Silicona hidrogel, marca Acuvue Oasys 1-Day',
            'category': 'Silicona',
            'display_order': 12
        },
        {
            'name': 'Delefilcon A',
            'code': 'DELE',
            'description': 'Silicona hidrogel de agua gradiente, Dailies Total 1',
            'category': 'Silicona',
            'display_order': 13
        },
    ]
    
    for material in contact_lens_materials:
        ClinicalParameter.objects.create(
            organization=None,
            parameter_type='contact_lens_material',
            is_active=True,
            **material
        )
    
    print(f"✅ {len(contact_lens_materials)} materiales de LC creados")
    
    # Verificar
    total = ClinicalParameter.objects.filter(
        organization__isnull=True,
        parameter_type='contact_lens_material'
    ).count()
    
    print(f"\n📊 Total de materiales de LC globales: {total}")
    print("=" * 60)
    print("✅ PROCESO COMPLETADO")

if __name__ == '__main__':
    add_contact_lens_materials()
