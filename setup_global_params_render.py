"""
Script para ejecutar en Render - Configuración de parámetros clínicos globales

INSTRUCCIONES PARA RENDER:
1. Abre el shell de Render
2. Copia y pega este archivo completo
3. Ejecuta: python setup_global_params_render.py

IMPORTANTE: Este script eliminará TODOS los parámetros clínicos existentes
y creará los parámetros globales estándar
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models_clinical_config import ClinicalParameter
from django.db.models import Q

def setup_global_params_render():
    """Setup completo para Render"""
    
    print("🚀 CONFIGURACIÓN DE PARÁMETROS CLÍNICOS GLOBALES - RENDER")
    print("=" * 70)
    
    # 1. Eliminar parámetros existentes
    print("\n🗑️  PASO 1: Eliminando parámetros existentes...")
    count = ClinicalParameter.objects.all().count()
    print(f"   Parámetros actuales: {count}")
    
    if count > 0:
        ClinicalParameter.objects.all().delete()
        print(f"   ✅ Eliminados {count} parámetros")
    else:
        print("   ℹ️  No había parámetros para eliminar")
    
    # 2. Crear parámetros globales
    print("\n📦 PASO 2: Creando parámetros clínicos globales...")
    print("-" * 70)
    
    # Materiales de Lentes
    lens_materials = [
        {'name': 'CR-39 (Resina Estándar)', 'code': 'CR39', 'description': 'Plástico orgánico estándar, índice 1.498', 'category': 'Estándar', 'display_order': 1},
        {'name': 'Policarbonato', 'code': 'PC', 'description': 'Material resistente a impactos, índice 1.586', 'category': 'Resistente', 'display_order': 2},
        {'name': 'Trivex', 'code': 'TRX', 'description': 'Material ligero y resistente, índice 1.53', 'category': 'Resistente', 'display_order': 3},
        {'name': 'Alto Índice 1.60', 'code': 'HI160', 'description': 'Lente delgado, índice 1.60', 'category': 'Alto Índice', 'display_order': 4},
        {'name': 'Alto Índice 1.67', 'code': 'HI167', 'description': 'Lente muy delgado, índice 1.67', 'category': 'Alto Índice', 'display_order': 5},
        {'name': 'Alto Índice 1.74', 'code': 'HI174', 'description': 'Lente ultra delgado, índice 1.74', 'category': 'Alto Índice', 'display_order': 6},
        {'name': 'Vidrio Crown', 'code': 'GLASS', 'description': 'Cristal mineral', 'category': 'Mineral', 'display_order': 7},
    ]
    
    for material in lens_materials:
        ClinicalParameter.objects.create(organization=None, parameter_type='lens_material', is_active=True, **material)
    print(f"   ✅ Materiales de Lentes: {len(lens_materials)}")
    
    # Tratamientos
    treatments = [
        {'name': 'Antireflejo', 'code': 'AR', 'description': 'Reduce reflejos y brillos', 'category': 'Antireflejo', 'display_order': 1},
        {'name': 'Antireflejo Premium', 'code': 'AR-PRO', 'description': 'Antireflejo avanzado', 'category': 'Antireflejo', 'display_order': 2},
        {'name': 'Blue Light (Luz Azul)', 'code': 'BL', 'description': 'Filtra luz azul de pantallas', 'category': 'Filtro', 'display_order': 3},
        {'name': 'Fotocromático', 'code': 'PHOTO', 'description': 'Se oscurece con luz solar', 'category': 'Transición', 'display_order': 4},
        {'name': 'Transitions Signature', 'code': 'TRANS-SIG', 'description': 'Fotocromático Transitions', 'category': 'Transición', 'display_order': 5},
        {'name': 'Transitions XTRActive', 'code': 'TRANS-XTR', 'description': 'Fotocromático avanzado', 'category': 'Transición', 'display_order': 6},
        {'name': 'Polarizado', 'code': 'POL', 'description': 'Elimina reflejos', 'category': 'Filtro', 'display_order': 7},
        {'name': 'Espejo', 'code': 'MIRROR', 'description': 'Recubrimiento reflectante', 'category': 'Estético', 'display_order': 8},
        {'name': 'Endurecido', 'code': 'HARD', 'description': 'Protección contra rayaduras', 'category': 'Endurecimiento', 'display_order': 9},
        {'name': 'Hidrofóbico', 'code': 'HYDRO', 'description': 'Repele agua', 'category': 'Protección', 'display_order': 10},
        {'name': 'UV 400', 'code': 'UV400', 'description': 'Protección 100% UV', 'category': 'Protección', 'display_order': 11},
        {'name': 'Antivaho', 'code': 'ANTIFOG', 'description': 'Previene empañamiento', 'category': 'Protección', 'display_order': 12},
    ]
    
    for treatment in treatments:
        ClinicalParameter.objects.create(organization=None, parameter_type='treatment', is_active=True, **treatment)
    print(f"   ✅ Tratamientos: {len(treatments)}")
    
    # Tipos de Lentes
    lens_types = [
        {'name': 'Monofocales', 'code': 'MONO', 'description': 'Una sola graduación', 'category': 'Estándar', 'display_order': 1},
        {'name': 'Bifocales', 'code': 'BIF', 'description': 'Dos graduaciones', 'category': 'Multifocal', 'display_order': 2},
        {'name': 'Trifocales', 'code': 'TRIF', 'description': 'Tres graduaciones', 'category': 'Multifocal', 'display_order': 3},
        {'name': 'Progresivos', 'code': 'PROG', 'description': 'Transición gradual', 'category': 'Multifocal', 'display_order': 4},
        {'name': 'Progresivos Premium', 'code': 'PROG-PRO', 'description': 'Progresivos de alta gama', 'category': 'Multifocal', 'display_order': 5},
        {'name': 'Ocupacionales', 'code': 'OCC', 'description': 'Para oficina', 'category': 'Especializado', 'display_order': 6},
        {'name': 'Deportivos', 'code': 'SPORT', 'description': 'Para deportes', 'category': 'Especializado', 'display_order': 7},
        {'name': 'Drive (Conducción)', 'code': 'DRIVE', 'description': 'Para conducción', 'category': 'Especializado', 'display_order': 8},
    ]
    
    for lens_type in lens_types:
        ClinicalParameter.objects.create(organization=None, parameter_type='lens_type', is_active=True, **lens_type)
    print(f"   ✅ Tipos de Lentes: {len(lens_types)}")
    
    # Marcas de Lentes
    lens_brands = [
        {'name': 'Essilor', 'code': 'ESS', 'description': 'Marca líder francesa', 'display_order': 1},
        {'name': 'Zeiss', 'code': 'ZEISS', 'description': 'Óptica alemana', 'display_order': 2},
        {'name': 'Hoya', 'code': 'HOYA', 'description': 'Tecnología japonesa', 'display_order': 3},
        {'name': 'Transitions', 'code': 'TRANS', 'description': 'Líderes en fotocromáticos', 'display_order': 4},
        {'name': 'Varilux', 'code': 'VAR', 'description': 'Progresivos de Essilor', 'display_order': 5},
        {'name': 'Crizal', 'code': 'CRIZ', 'description': 'Tratamientos de Essilor', 'display_order': 6},
        {'name': 'Kodak', 'code': 'KOD', 'description': 'Lentes de calidad', 'display_order': 7},
        {'name': 'Rodenstock', 'code': 'ROD', 'description': 'Marca alemana premium', 'display_order': 8},
    ]
    
    for brand in lens_brands:
        ClinicalParameter.objects.create(organization=None, parameter_type='lens_brand', is_active=True, **brand)
    print(f"   ✅ Marcas de Lentes: {len(lens_brands)}")
    
    # Tipos de Monturas
    frame_types = [
        {'name': 'Completa (Full Rim)', 'code': 'FULL', 'description': 'Montura completa', 'display_order': 1},
        {'name': 'Semi al Aire (Semi Rimless)', 'code': 'SEMI', 'description': 'Montura parcial', 'display_order': 2},
        {'name': 'Al Aire (Rimless)', 'code': 'RIMLESS', 'description': 'Sin montura', 'display_order': 3},
        {'name': 'Deportiva', 'code': 'SPORT', 'description': 'Diseño deportivo', 'display_order': 4},
        {'name': 'Aviador', 'code': 'AVIATOR', 'description': 'Estilo aviador', 'display_order': 5},
        {'name': 'Wayfarer', 'code': 'WAYFARER', 'description': 'Estilo rectangular', 'display_order': 6},
        {'name': 'Redonda', 'code': 'ROUND', 'description': 'Forma circular', 'display_order': 7},
        {'name': 'Cat Eye', 'code': 'CATEYE', 'description': 'Estilo ojo de gato', 'display_order': 8},
    ]
    
    for frame in frame_types:
        ClinicalParameter.objects.create(organization=None, parameter_type='frame_type', is_active=True, **frame)
    print(f"   ✅ Tipos de Monturas: {len(frame_types)}")
    
    # Diagnósticos principales
    diagnoses = [
        {'name': 'Miopía', 'code': 'MYOPIA', 'icd_10_code': 'H52.1', 'description': 'Dificultad para ver de lejos', 'category': 'Defecto Refractivo', 'display_order': 1},
        {'name': 'Hipermetropía', 'code': 'HYPER', 'icd_10_code': 'H52.0', 'description': 'Dificultad para ver de cerca', 'category': 'Defecto Refractivo', 'display_order': 2},
        {'name': 'Astigmatismo', 'code': 'ASTIG', 'icd_10_code': 'H52.2', 'description': 'Visión distorsionada', 'category': 'Defecto Refractivo', 'display_order': 3},
        {'name': 'Presbicia', 'code': 'PRESB', 'icd_10_code': 'H52.4', 'description': 'Pérdida de acomodación', 'category': 'Defecto Refractivo', 'display_order': 4},
        {'name': 'Ojo Seco', 'code': 'DRY', 'icd_10_code': 'H04.12', 'description': 'Deficiencia de lágrima', 'category': 'Superficie Ocular', 'display_order': 5},
        {'name': 'Conjuntivitis', 'code': 'CONJ', 'icd_10_code': 'H10.9', 'description': 'Inflamación conjuntiva', 'category': 'Inflamatorio', 'display_order': 6},
        {'name': 'Catarata', 'code': 'CAT', 'icd_10_code': 'H26.9', 'description': 'Opacidad del cristalino', 'category': 'Cristalino', 'display_order': 7},
        {'name': 'Glaucoma', 'code': 'GLAUC', 'icd_10_code': 'H40.9', 'description': 'Presión intraocular elevada', 'category': 'Glaucoma', 'display_order': 8},
    ]
    
    for diagnosis in diagnoses:
        ClinicalParameter.objects.create(organization=None, parameter_type='diagnosis', is_active=True, **diagnosis)
    print(f"   ✅ Diagnósticos: {len(diagnoses)}")
    
    # Medicamentos básicos
    medications = [
        {'name': 'Lágrimas Artificiales', 'code': 'LAG-ART', 'dosage': '1-2 gotas', 'frequency': 'Según necesidad', 'administration_route': 'ophthalmic', 'category': 'Lubricante', 'display_order': 1},
        {'name': 'Systane', 'code': 'SYST', 'dosage': '1-2 gotas', 'frequency': '3-4 veces al día', 'administration_route': 'ophthalmic', 'category': 'Lubricante', 'display_order': 2},
        {'name': 'Tobramicina', 'code': 'TOBRA', 'dosage': '1 gota', 'frequency': 'Cada 4-6 horas', 'duration': '7 días', 'administration_route': 'ophthalmic', 'category': 'Antibiótico', 'display_order': 3},
    ]
    
    for med in medications:
        ClinicalParameter.objects.create(organization=None, parameter_type='topical_medication', is_active=True, **med)
    print(f"   ✅ Medicamentos: {len(medications)}")
    
    # 3. Verificar
    print("\n✅ PASO 3: Verificación...")
    total = ClinicalParameter.objects.filter(organization__isnull=True).count()
    print(f"   Total de parámetros globales creados: {total}")
    
    print("\n" + "=" * 70)
    print("🎉 CONFIGURACIÓN COMPLETADA EXITOSAMENTE")
    print("=" * 70)
    print("\n💡 Los parámetros globales están disponibles para todas las organizaciones")
    print("💡 Cada organización puede agregar sus propios parámetros personalizados")

if __name__ == '__main__':
    setup_global_params_render()
