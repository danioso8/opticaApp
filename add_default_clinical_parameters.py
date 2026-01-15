#!/usr/bin/env python
"""
Script para agregar parámetros clínicos predeterminados
Estos parámetros estarán disponibles para todas las organizaciones
"""
import os
import sys
import django

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models_clinical_config import ClinicalParameter
from apps.organizations.models import Organization

# Parámetros clínicos predeterminados
DEFAULT_PARAMETERS = {
    'lens_type': [
        {'name': 'Monofocal', 'code': 'MONO', 'description': 'Lente de visión simple'},
        {'name': 'Bifocal', 'code': 'BIFF', 'description': 'Lente con dos zonas de graduación'},
        {'name': 'Progresivo', 'code': 'PROG', 'description': 'Lente multifocal sin línea divisoria'},
        {'name': 'Ocupacional', 'code': 'OCUP', 'description': 'Lente para trabajo en distancias intermedias y cercanas'},
        {'name': 'Deportivo', 'code': 'DEPO', 'description': 'Lente especializado para actividades deportivas'},
        {'name': 'Filtro Luz Azul', 'code': 'BLUE', 'description': 'Lente con filtro para luz azul'},
    ],
    
    'lens_material': [
        {'name': 'CR-39 (Orgánico)', 'code': 'CR39', 'description': 'Material plástico estándar'},
        {'name': 'Policarbonato', 'code': 'POLI', 'description': 'Material resistente a impactos'},
        {'name': 'Trivex', 'code': 'TRVX', 'description': 'Material ligero y resistente'},
        {'name': 'Alto Índice 1.67', 'code': 'HI67', 'description': 'Material delgado para graduaciones altas'},
        {'name': 'Alto Índice 1.74', 'code': 'HI74', 'description': 'Material ultra delgado'},
        {'name': 'Cristal (Mineral)', 'code': 'CRIS', 'description': 'Material mineral tradicional'},
    ],
    
    'lens_coating': [
        {'name': 'Antirreflejante', 'code': 'AR', 'description': 'Reduce reflejos y deslumbramientos'},
        {'name': 'Transitions', 'code': 'TRAN', 'description': 'Fotocromático que se oscurece con la luz'},
        {'name': 'UV400', 'code': 'UV', 'description': 'Protección ultravioleta completa'},
        {'name': 'Antirraya (Hard Coat)', 'code': 'HC', 'description': 'Protección contra rayones'},
        {'name': 'Hidrofóbico', 'code': 'HIDR', 'description': 'Repele agua y grasa'},
        {'name': 'Espejo', 'code': 'ESPE', 'description': 'Recubrimiento reflectante'},
        {'name': 'Crizal', 'code': 'CRIZ', 'description': 'Antirreflejante premium'},
        {'name': 'Polarizado', 'code': 'POLA', 'description': 'Reduce reflejos de superficies'},
    ],
    
    'lens_brand': [
        {'name': 'Essilor', 'code': 'ESSI', 'description': 'Marca premium francesa'},
        {'name': 'Zeiss', 'code': 'ZEIS', 'description': 'Marca premium alemana'},
        {'name': 'Hoya', 'code': 'HOYA', 'description': 'Marca japonesa de alta calidad'},
        {'name': 'Varilux', 'code': 'VARI', 'description': 'Línea progresiva de Essilor'},
        {'name': 'Shamir', 'code': 'SHAM', 'description': 'Marca israelí especializada en progresivos'},
        {'name': 'Rodenstock', 'code': 'RODE', 'description': 'Marca alemana'},
    ],
    
    'contact_lens_type': [
        {'name': 'Blandos Diarios', 'code': 'SOFT_D', 'description': 'Lentes blandos de uso diario'},
        {'name': 'Blandos Quincenales', 'code': 'SOFT_Q', 'description': 'Lentes blandos de reemplazo quincenal'},
        {'name': 'Blandos Mensuales', 'code': 'SOFT_M', 'description': 'Lentes blandos de reemplazo mensual'},
        {'name': 'Rígidos Gas Permeable (RGP)', 'code': 'RGP', 'description': 'Lentes rígidos permeables al gas'},
        {'name': 'Tóricos', 'code': 'TORI', 'description': 'Para corrección de astigmatismo'},
        {'name': 'Multifocales', 'code': 'MULT', 'description': 'Para presbicia'},
        {'name': 'Esclerales', 'code': 'ESCL', 'description': 'Lentes de gran diámetro'},
        {'name': 'Orto-K', 'code': 'ORTK', 'description': 'Ortoqueratología nocturna'},
    ],
    
    'contact_lens_brand': [
        {'name': 'Acuvue', 'code': 'ACUV', 'description': 'Johnson & Johnson'},
        {'name': 'Air Optix', 'code': 'AIRO', 'description': 'Alcon'},
        {'name': 'Biofinity', 'code': 'BIOF', 'description': 'CooperVision'},
        {'name': 'Proclear', 'code': 'PROC', 'description': 'CooperVision'},
        {'name': 'Dailies', 'code': 'DAIL', 'description': 'Alcon'},
        {'name': 'Biomedics', 'code': 'BIOM', 'description': 'CooperVision'},
    ],
    
    'frame_type': [
        {'name': 'Completo (Full Rim)', 'code': 'FULL', 'description': 'Aro completo alrededor del lente'},
        {'name': 'Semi al Aire (Semi-Rimless)', 'code': 'SEMI', 'description': 'Aro parcial'},
        {'name': 'Al Aire (Rimless)', 'code': 'RIML', 'description': 'Sin aro, lente perforado'},
        {'name': 'Deportivo', 'code': 'DEPO', 'description': 'Diseño para deportes'},
        {'name': 'Infantil', 'code': 'INFA', 'description': 'Diseño para niños'},
        {'name': 'Alta Graduación', 'code': 'HIGH', 'description': 'Para graduaciones altas'},
    ],
    
    'topical_medication': [
        {'name': 'Timolol 0.5%', 'code': 'TIMO', 'description': 'Betabloqueador para glaucoma', 'dosage': '1 gota', 'frequency': 'Cada 12 horas'},
        {'name': 'Latanoprost 0.005%', 'code': 'LATA', 'description': 'Análogo de prostaglandina', 'dosage': '1 gota', 'frequency': 'Una vez al día (noche)'},
        {'name': 'Brimonidina 0.2%', 'code': 'BRIM', 'description': 'Agonista alfa-2', 'dosage': '1 gota', 'frequency': 'Cada 8-12 horas'},
        {'name': 'Dorzolamida 2%', 'code': 'DORZ', 'description': 'Inhibidor de anhidrasa carbónica', 'dosage': '1 gota', 'frequency': 'Cada 8-12 horas'},
        {'name': 'Lágrimas Artificiales', 'code': 'LAGR', 'description': 'Lubricante ocular', 'dosage': '1-2 gotas', 'frequency': 'Según necesidad'},
        {'name': 'Tobramicina 0.3%', 'code': 'TOBR', 'description': 'Antibiótico', 'dosage': '1 gota', 'frequency': 'Cada 4-6 horas'},
        {'name': 'Dexametasona 0.1%', 'code': 'DEXA', 'description': 'Corticoide', 'dosage': '1 gota', 'frequency': 'Cada 4-6 horas'},
        {'name': 'Tropicamida 1%', 'code': 'TROP', 'description': 'Midriático', 'dosage': '1 gota', 'frequency': 'Según indicación'},
    ],
    
    'diagnosis': [
        {'name': 'Miopía', 'code': 'H52.1', 'description': 'Defecto refractivo - visión lejana borrosa'},
        {'name': 'Hipermetropía', 'code': 'H52.0', 'description': 'Defecto refractivo - dificultad visión cercana'},
        {'name': 'Astigmatismo', 'code': 'H52.2', 'description': 'Defecto refractivo - córnea irregular'},
        {'name': 'Presbicia', 'code': 'H52.4', 'description': 'Pérdida de acomodación relacionada con edad'},
        {'name': 'Ojo Seco', 'code': 'H04.1', 'description': 'Síndrome de ojo seco'},
        {'name': 'Conjuntivitis', 'code': 'H10', 'description': 'Inflamación conjuntival'},
        {'name': 'Blefaritis', 'code': 'H01.0', 'description': 'Inflamación del borde palpebral'},
        {'name': 'Glaucoma', 'code': 'H40', 'description': 'Neuropatía óptica'},
        {'name': 'Catarata', 'code': 'H25', 'description': 'Opacidad del cristalino'},
    ],
    
    'treatment': [
        {'name': 'Corrección Óptica', 'code': 'CORR', 'description': 'Uso de lentes correctivos'},
        {'name': 'Terapia Visual', 'code': 'THER', 'description': 'Ejercicios de rehabilitación visual'},
        {'name': 'Higiene Palpebral', 'code': 'HYGI', 'description': 'Limpieza de párpados'},
        {'name': 'Compresas Tibias', 'code': 'COMP', 'description': 'Aplicación de calor húmedo'},
        {'name': 'Control Periódico', 'code': 'CONT', 'description': 'Seguimiento regular'},
    ],
}


def create_parameters_for_org(org):
    """Crear parámetros para una organización específica"""
    created = 0
    
    for param_type, parameters in DEFAULT_PARAMETERS.items():
        for param_data in parameters:
            # Verificar si ya existe
            exists = ClinicalParameter.objects.filter(
                organization=org,
                parameter_type=param_type,
                name=param_data['name']
            ).exists()
            
            if not exists:
                ClinicalParameter.objects.create(
                    organization=org,
                    parameter_type=param_type,
                    name=param_data['name'],
                    code=param_data.get('code', ''),
                    description=param_data.get('description', ''),
                    dosage=param_data.get('dosage', ''),
                    frequency=param_data.get('frequency', ''),
                    is_active=True,
                )
                created += 1
    
    return created


def main():
    print("🔧 AGREGANDO PARÁMETROS CLÍNICOS PREDETERMINADOS")
    print("=" * 60)
    
    total_created = 0
    total_orgs = 0
    
    # Obtener todas las organizaciones activas
    organizations = Organization.objects.filter(is_active=True)
    
    for org in organizations:
        print(f"\n📋 Procesando: {org.name}")
        created = create_parameters_for_org(org)
        total_created += created
        total_orgs += 1
        print(f"   ✅ Creados: {created} parámetros")
    
    print("\n" + "=" * 60)
    print(f"📊 RESUMEN:")
    print(f"   🏢 Organizaciones procesadas: {total_orgs}")
    print(f"   ✅ Total parámetros creados: {total_created}")
    print(f"   📋 Tipos de parámetros: {len(DEFAULT_PARAMETERS)}")
    
    # Mostrar desglose por tipo
    print(f"\n📦 Parámetros por tipo:")
    for param_type, params in DEFAULT_PARAMETERS.items():
        print(f"   - {param_type}: {len(params)} parámetros")
    
    print("\n✨ Parámetros clínicos predeterminados configurados correctamente")


if __name__ == '__main__':
    main()
