"""
Script para crear parámetros clínicos básicos en la base de datos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models import ClinicalParameter

print("=" * 80)
print("CREANDO PARÁMETROS CLÍNICOS GLOBALES")
print("=" * 80)

# Función para crear parámetros si no existen
def create_params(param_type, names, descriptions=None):
    created = 0
    for i, name in enumerate(names):
        desc = descriptions[i] if descriptions and i < len(descriptions) else ''
        param, created_now = ClinicalParameter.objects.get_or_create(
            name=name,
            parameter_type=param_type,
            organization=None,  # Global
            defaults={
                'description': desc,
                'is_active': True,
                'display_order': i + 1
            }
        )
        if created_now:
            created += 1
            print(f"   ✅ Creado: {name}")
    return created

total_created = 0

# 1. TIPOS DE LENTES
print("\n📐 Tipos de Lentes")
total_created += create_params('lens_type', [
    'Monofocales',
    'Bifocales',
    'Progresivos',
    'Ocupacionales',
    'Lectura',
    'Antifatiga',
    'Deportivos'
])

# 2. MATERIALES DE LENTES
print("\n🔬 Materiales de Lentes")
total_created += create_params('lens_material', [
    'CR-39 (Resina)',
    'Policarbonato',
    'Trivex',
    'High Index 1.60',
    'High Index 1.67',
    'High Index 1.74',
    'Cristal/Mineral',
    'Orgánico Estándar'
])

# 3. TRATAMIENTOS/COATINGS
print("\n✨ Tratamientos para Lentes")
total_created += create_params('lens_coating', [
    'Antirreflejo',
    'Antirayado',
    'Hidrofóbico',
    'Oleofóbico',
    'UV 400',
    'Filtro Luz Azul',
    'Fotocromático',
    'Polarizado',
    'Espejado',
    'Antiestático'
])

# 4. MARCAS DE LENTES
print("\n🏷️ Marcas de Lentes")
total_created += create_params('lens_brand', [
    'Essilor',
    'Zeiss',
    'Hoya',
    'Rodenstock',
    'Nikon',
    'Transitions',
    'Crizal',
    'BBGr',
    'Otro'
])

# 5. TIPOS DE MONTURA
print("\n👓 Tipos de Montura")
total_created += create_params('frame_type', [
    'Completa/Full Rim',
    'Semi al Aire/Semi Rimless',
    'Al Aire/Rimless',
    'Deportiva',
    'Infantil',
    'Seguridad Industrial'
])

# 6. MEDICAMENTOS TÓPICOS
print("\n💊 Medicamentos Tópicos")
total_created += create_params('topical_medication', [
    'Lágrimas Artificiales',
    'Lubricante Ocular',
    'Antibiótico (Tobramicina)',
    'Antibiótico (Moxifloxacino)',
    'Antiinflamatorio (Dexametasona)',
    'Antiinflamatorio (Ketorolaco)',
    'Antihistamínico (Olopatadina)',
    'Ciclopléjico (Tropicamida)',
    'Ciclopléjico (Ciclopentolato)',
    'Midriático (Fenilefrina)',
    'Antiglaucoma (Timolol)',
    'Antiglaucoma (Latanoprost)',
    'Antiglaucoma (Dorzolamida)'
])

# 7. LENTES DE CONTACTO - TIPOS
print("\n👁️ Tipos de Lentes de Contacto")
total_created += create_params('contact_lens_type', [
    'Blandos Esféricos',
    'Blandos Tóricos',
    'Blandos Multifocales',
    'Rígidos Gas Permeable (RGP)',
    'Híbridos',
    'Esclerales',
    'Ortoqueratología (Orto-K)',
    'Cosméticos/Color'
])

# 8. LENTES DE CONTACTO - MARCAS
print("\n🏷️ Marcas de Lentes de Contacto")
total_created += create_params('contact_lens_brand', [
    'Acuvue (Johnson & Johnson)',
    'Air Optix (Alcon)',
    'Biomedics (CooperVision)',
    'Biofinity (CooperVision)',
    'Clariti (CooperVision)',
    'Dailies (Alcon)',
    'Freshlook (Alcon)',
    'MyDay (CooperVision)',
    'Proclear (CooperVision)',
    'PureVision (Bausch + Lomb)',
    'SofLens (Bausch + Lomb)',
    'Ultra (Bausch + Lomb)'
])

# 9. LENTES DE CONTACTO - MATERIALES
print("\n🔬 Materiales de Lentes de Contacto")
total_created += create_params('contact_lens_material', [
    'Hidrogel',
    'Hidrogel de Silicona',
    'PMMA',
    'Fluorsilicona Acrilato',
    'Híbrido'
])

# 10. RÉGIMEN DE USO
print("\n📅 Régimen de Uso de LC")
total_created += create_params('contact_lens_wearing', [
    'Uso Diario (Daily)',
    'Reemplazo Quincenal',
    'Reemplazo Mensual',
    'Uso Prolongado',
    'Uso Continuo',
    'Uso Extendido'
])

# 11. TERAPIAS
print("\n🎯 Terapias")
total_created += create_params('therapy', [
    'Terapia Visual',
    'Oclusión',
    'Prismas',
    'Filtros Selectivos',
    'Ejercicios Oculomotores',
    'Control de Miopía'
])

# 12. TERAPIAS VISUALES ESPECÍFICAS
print("\n👁️‍🗨️ Terapias Visuales Específicas")
total_created += create_params('visual_therapy', [
    'Entrenamiento Acomodativo',
    'Terapia de Convergencia',
    'Terapia de Seguimientos',
    'Terapia Binocular',
    'Entrenamiento Perceptual',
    'Terapia de Ambliopía'
])

# 13. EXÁMENES COMPLEMENTARIOS
print("\n🔬 Exámenes Complementarios")
total_created += create_params('complementary_exam', [
    'Topografía Corneal',
    'Paquimetría',
    'OCT (Tomografía de Coherencia Óptica)',
    'OCT Mácula',
    'OCT Nervio Óptico',
    'Angiografía',
    'Campo Visual',
    'Biometría',
    'Microscopía Especular',
    'Aberrometría',
    'Retinografía',
    'Ecografía Ocular',
    'Gonioscopia',
    'Curva Tensional'
])

# 14. EXÁMENES DE LABORATORIO
print("\n🧪 Exámenes de Laboratorio")
total_created += create_params('lab_test', [
    'Hemograma',
    'Glicemia',
    'Perfil Lipídico',
    'TSH',
    'Hemoglobina Glicosilada',
    'Pruebas Autoinmunes',
    'VDRL',
    'Toxoplasmosis'
])

# 15. RECOMENDACIONES
print("\n💡 Recomendaciones")
total_created += create_params('recommendation', [
    'Descanso Visual (Regla 20-20-20)',
    'Higiene de Párpados',
    'Uso de Gafas de Sol',
    'Iluminación Adecuada',
    'Distancia de Lectura',
    'Postura Correcta',
    'Dieta Rica en Vitamina A',
    'Hidratación Ocular',
    'Limitar Tiempo de Pantallas',
    'Ejercicio Regular'
])

# 16. MOTIVOS DE SEGUIMIENTO
print("\n📅 Motivos de Seguimiento")
total_created += create_params('follow_up_reason', [
    'Control Post-Cirugía',
    'Adaptación de Lentes',
    'Control de Glaucoma',
    'Control de Miopía',
    'Evaluación de Tratamiento',
    'Control de Diabetes',
    'Reevaluación Visual',
    'Control Anual',
    'Urgencia/Sintomatología'
])

# 17. ESPECIALIDADES PARA REMISIÓN
print("\n🏥 Especialidades para Remisión")
total_created += create_params('referral_specialty', [
    'Oftalmología General',
    'Retinología',
    'Glaucoma',
    'Córnea',
    'Cirugía Refractiva',
    'Estrabismo',
    'Neuro-oftalmología',
    'Oculoplastia',
    'Uveítis',
    'Oncología Ocular',
    'Pediatría Oftálmica',
    'Baja Visión'
])

print("\n" + "=" * 80)
print(f"✅ TOTAL DE PARÁMETROS CREADOS: {total_created}")
print("=" * 80)

# Verificar totales
from django.db.models import Count
totals = ClinicalParameter.objects.filter(is_active=True).values('parameter_type').annotate(count=Count('id'))
print("\n📊 RESUMEN POR TIPO:")
for t in totals:
    print(f"   - {t['parameter_type']}: {t['count']} parámetros")

print("\n✅ PARÁMETROS CLÍNICOS CREADOS EXITOSAMENTE")
print("Ahora recarga el formulario de examen visual para verlos")
