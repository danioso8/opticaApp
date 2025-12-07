#!/usr/bin/env python
"""
Script para poblar parámetros clínicos en la base de datos
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models import ClinicalParameter
from apps.organizations.models import Organization

# Obtener la primera organización
org = Organization.objects.first()
if not org:
    print("❌ No hay organizaciones en la base de datos")
    exit(1)

print(f"✅ Organización: {org.name}")
print(f"ID: {org.id}")
print()

# Definición de parámetros clínicos por categoría
CLINICAL_PARAMETERS = {
    # LENTES OFTÁLMICOS
    'lens_type': [
        'Monofocal', 'Bifocal', 'Trifocal', 'Progresivo', 
        'Ocupacional', 'Deportivo', 'Fotocromático'
    ],
    'lens_material': [
        'CR-39 (Plástico)', 'Policarbonato', 'Trivex', 
        'Alto Índice 1.67', 'Alto Índice 1.74', 'Vidrio'
    ],
    'lens_coating': [
        'Anti-reflejo', 'Anti-rayado', 'Hidrofóbico', 
        'UV 400', 'Blue Light', 'Espejo'
    ],
    'lens_brand': [
        'Essilor', 'Zeiss', 'Hoya', 'Shamir', 
        'Rodenstock', 'Transitions', 'Crizal'
    ],
    'frame_type': [
        'Completo', 'Al aire (Rimless)', 'Semi al aire', 
        'Deportivo', 'Infantil', 'De seguridad'
    ],
    
    # LENTES DE CONTACTO
    'contact_lens_type': [
        'Blandos esféricos', 'Blandos tóricos', 'Blandos multifocales',
        'RGP esféricos', 'RGP tóricos', 'RGP multifocales',
        'Ortoqueratología', 'Esclerales', 'Cosméticos'
    ],
    'contact_lens_brand': [
        'Acuvue (J&J)', 'Air Optix (Alcon)', 'Biofinity (CooperVision)',
        'Proclear (CooperVision)', 'Dailies (Alcon)', 'Bausch + Lomb'
    ],
    'contact_lens_material': [
        'Hidrogel convencional', 'Hidrogel de silicona',
        'RGP (Gas permeable)', 'PMMA'
    ],
    'contact_lens_wearing': [
        'Uso diario (desechable)', 'Uso semanal', 'Uso quincenal',
        'Uso mensual', 'Uso prolongado', 'Uso continuo'
    ],
    
    # DIAGNÓSTICOS
    'diagnosis': [
        'Miopía', 'Hipermetropía', 'Astigmatismo', 'Presbicia',
        'Ambliopía', 'Estrabismo', 'Conjuntivitis', 'Ojo seco',
        'Cataratas', 'Glaucoma', 'Retinopatía diabética', 'DMAE',
        'Queratocono', 'Pterigion', 'Chalazión', 'Blefaritis'
    ],
    'diagnosis_category': [
        'Errores refractivos', 'Patologías del segmento anterior',
        'Patologías del segmento posterior', 'Neuroftalmología',
        'Estrabismo y motilidad ocular', 'Patologías palpebrales'
    ],
    
    # TRATAMIENTOS
    'treatment': [
        'Lentes oftálmicos', 'Lentes de contacto', 'Cirugía refractiva',
        'Terapia visual', 'Prismas', 'Oclusión', 'Farmacológico'
    ],
    'therapy': [
        'Terapia de acomodación', 'Terapia de convergencia',
        'Terapia de seguimientos', 'Terapia de sacádicos',
        'Terapia de estereopsis', 'Terapia de visión periférica'
    ],
    'visual_therapy': [
        'Ejercicios de fijación', 'Ejercicios de seguimiento',
        'Ejercicios de cambio de foco', 'Cordón de Brock',
        'Parches de Bangerter', 'Filtros selectivos'
    ],
    
    # EXÁMENES
    'complementary_exam': [
        'Topografía corneal', 'Tomografía de coherencia óptica (OCT)',
        'Paquimetría', 'Campimetría', 'Retinografía',
        'Angiografía fluoresceínica', 'Ecografía ocular',
        'Biometría', 'Gonioscopia', 'Microscopia especular'
    ],
    'lab_test': [
        'Glicemia', 'Hemoglobina glicosilada', 'Perfil lipídico',
        'Hemograma', 'VSG', 'PCR', 'Hormonas tiroideas'
    ],
    
    # MEDICAMENTOS
    'medication': [
        'Lágrimas artificiales', 'Antibiótico tópico', 
        'Antiinflamatorio tópico', 'Midriático', 'Ciclopléjico',
        'Hipotensor ocular', 'Antihistamínico', 'Lubricante gel'
    ],
    'topical_medication': [
        'Tobramicina 0.3%', 'Moxifloxacino 0.5%', 
        'Dexametasona 0.1%', 'Ketorolaco 0.5%',
        'Tropicamida 1%', 'Ciclopentolato 1%',
        'Timolol 0.5%', 'Latanoprost 0.005%',
        'Olopatadina 0.1%', 'Carmelosa sódica 0.5%'
    ],
    'systemic_medication': [
        'Acetazolamida 250mg', 'Ácido acetilsalicílico 100mg',
        'Vitamina A', 'Omega-3', 'Multivitamínico'
    ],
    
    # SEGUIMIENTO
    'recommendation': [
        'Control en 1 semana', 'Control en 1 mes', 'Control en 3 meses',
        'Control en 6 meses', 'Control anual', 'Limpieza palpebral diaria',
        'Uso de lágrimas artificiales', 'Evitar frotarse los ojos',
        'Descanso visual cada 20 minutos', 'Protección UV'
    ],
    'referral_specialty': [
        'Oftalmología general', 'Retina y vítreo', 'Córnea',
        'Glaucoma', 'Neuroftalmología', 'Oculoplastia',
        'Estrabismo', 'Oftalmología pediátrica', 'Medicina interna',
        'Endocrinología', 'Neurología'
    ],
    'follow_up_reason': [
        'Control de refracción', 'Evaluación de tratamiento',
        'Seguimiento de patología', 'Adaptación de lentes',
        'Revisión de terapia visual', 'Control post-quirúrgico',
        'Evaluación de presión intraocular', 'Revisión de fondo de ojo'
    ],
}

print("=" * 80)
print("POBLANDO BASE DE DATOS CON PARÁMETROS CLÍNICOS")
print("=" * 80)
print()

total_created = 0
total_existing = 0

for param_type, values in CLINICAL_PARAMETERS.items():
    print(f"\n📋 {param_type}")
    print("-" * 60)
    
    for idx, value in enumerate(values, start=1):
        param, created = ClinicalParameter.objects.get_or_create(
            organization=org,
            parameter_type=param_type,
            name=value,
            defaults={
                'description': f'{value} - {param_type}',
                'display_order': idx,
                'is_active': True
            }
        )
        
        if created:
            print(f"   ✅ Creado: {value}")
            total_created += 1
        else:
            print(f"   ⏭️  Ya existe: {value}")
            total_existing += 1

print()
print("=" * 80)
print(f"✅ PROCESO COMPLETADO")
print("=" * 80)
print(f"   Parámetros creados: {total_created}")
print(f"   Parámetros existentes: {total_existing}")
print(f"   Total: {total_created + total_existing}")
print()
print("💡 Ahora recarga la página del examen visual para ver los parámetros")
