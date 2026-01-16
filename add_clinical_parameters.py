#!/usr/bin/env python
"""
Script para agregar parámetros clínicos estándar al sistema
Parámetros para exámenes visuales completos
"""
import os
import sys
import django

# Agregar el directorio raíz al path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models import ClinicalParameter

# Parámetros clínicos estándar para exámenes visuales
CLINICAL_PARAMETERS = [
    # AGUDEZA VISUAL
    {
        'name': 'Agudeza Visual OD SC Lejos',
        'code': 'VA_OD_SC_DISTANCE',
        'category': 'agudeza_visual',
        'data_type': 'text',
        'unit': '',
        'description': 'Agudeza visual ojo derecho sin corrección - distancia',
        'is_active': True,
    },
    {
        'name': 'Agudeza Visual OD SC Cerca',
        'code': 'VA_OD_SC_NEAR',
        'category': 'agudeza_visual',
        'data_type': 'text',
        'unit': '',
        'description': 'Agudeza visual ojo derecho sin corrección - cerca',
        'is_active': True,
    },
    {
        'name': 'Agudeza Visual OD CC Lejos',
        'code': 'VA_OD_CC_DISTANCE',
        'category': 'agudeza_visual',
        'data_type': 'text',
        'unit': '',
        'description': 'Agudeza visual ojo derecho con corrección - distancia',
        'is_active': True,
    },
    {
        'name': 'Agudeza Visual OD CC Cerca',
        'code': 'VA_OD_CC_NEAR',
        'category': 'agudeza_visual',
        'data_type': 'text',
        'unit': '',
        'description': 'Agudeza visual ojo derecho con corrección - cerca',
        'is_active': True,
    },
    {
        'name': 'Agudeza Visual OS SC Lejos',
        'code': 'VA_OS_SC_DISTANCE',
        'category': 'agudeza_visual',
        'data_type': 'text',
        'unit': '',
        'description': 'Agudeza visual ojo izquierdo sin corrección - distancia',
        'is_active': True,
    },
    {
        'name': 'Agudeza Visual OS SC Cerca',
        'code': 'VA_OS_SC_NEAR',
        'category': 'agudeza_visual',
        'data_type': 'text',
        'unit': '',
        'description': 'Agudeza visual ojo izquierdo sin corrección - cerca',
        'is_active': True,
    },
    {
        'name': 'Agudeza Visual OS CC Lejos',
        'code': 'VA_OS_CC_DISTANCE',
        'category': 'agudeza_visual',
        'data_type': 'text',
        'unit': '',
        'description': 'Agudeza visual ojo izquierdo con corrección - distancia',
        'is_active': True,
    },
    {
        'name': 'Agudeza Visual OS CC Cerca',
        'code': 'VA_OS_CC_NEAR',
        'category': 'agudeza_visual',
        'data_type': 'text',
        'unit': '',
        'description': 'Agudeza visual ojo izquierdo con corrección - cerca',
        'is_active': True,
    },
    
    # REFRACCIÓN
    {
        'name': 'Refracción OD Esfera',
        'code': 'RX_OD_SPHERE',
        'category': 'refraccion',
        'data_type': 'decimal',
        'unit': 'D',
        'description': 'Refracción ojo derecho - esfera',
        'is_active': True,
    },
    {
        'name': 'Refracción OD Cilindro',
        'code': 'RX_OD_CYLINDER',
        'category': 'refraccion',
        'data_type': 'decimal',
        'unit': 'D',
        'description': 'Refracción ojo derecho - cilindro',
        'is_active': True,
    },
    {
        'name': 'Refracción OD Eje',
        'code': 'RX_OD_AXIS',
        'category': 'refraccion',
        'data_type': 'integer',
        'unit': '°',
        'description': 'Refracción ojo derecho - eje',
        'is_active': True,
    },
    {
        'name': 'Refracción OD ADD',
        'code': 'RX_OD_ADD',
        'category': 'refraccion',
        'data_type': 'decimal',
        'unit': 'D',
        'description': 'Refracción ojo derecho - adición',
        'is_active': True,
    },
    {
        'name': 'Refracción OS Esfera',
        'code': 'RX_OS_SPHERE',
        'category': 'refraccion',
        'data_type': 'decimal',
        'unit': 'D',
        'description': 'Refracción ojo izquierdo - esfera',
        'is_active': True,
    },
    {
        'name': 'Refracción OS Cilindro',
        'code': 'RX_OS_CYLINDER',
        'category': 'refraccion',
        'data_type': 'decimal',
        'unit': 'D',
        'description': 'Refracción ojo izquierdo - cilindro',
        'is_active': True,
    },
    {
        'name': 'Refracción OS Eje',
        'code': 'RX_OS_AXIS',
        'category': 'refraccion',
        'data_type': 'integer',
        'unit': '°',
        'description': 'Refracción ojo izquierdo - eje',
        'is_active': True,
    },
    {
        'name': 'Refracción OS ADD',
        'code': 'RX_OS_ADD',
        'category': 'refraccion',
        'data_type': 'decimal',
        'unit': 'D',
        'description': 'Refracción ojo izquierdo - adición',
        'is_active': True,
    },
    
    # PRESIÓN INTRAOCULAR
    {
        'name': 'Presión Intraocular OD',
        'code': 'IOP_OD',
        'category': 'presion_intraocular',
        'data_type': 'decimal',
        'unit': 'mmHg',
        'description': 'Presión intraocular ojo derecho',
        'is_active': True,
        'normal_min': 10.0,
        'normal_max': 21.0,
    },
    {
        'name': 'Presión Intraocular OS',
        'code': 'IOP_OS',
        'category': 'presion_intraocular',
        'data_type': 'decimal',
        'unit': 'mmHg',
        'description': 'Presión intraocular ojo izquierdo',
        'is_active': True,
        'normal_min': 10.0,
        'normal_max': 21.0,
    },
    
    # QUERATOMETRÍA
    {
        'name': 'Queratometría OD K1',
        'code': 'KERAT_OD_K1',
        'category': 'queratometria',
        'data_type': 'decimal',
        'unit': 'D',
        'description': 'Queratometría ojo derecho - meridiano plano',
        'is_active': True,
    },
    {
        'name': 'Queratometría OD K2',
        'code': 'KERAT_OD_K2',
        'category': 'queratometria',
        'data_type': 'decimal',
        'unit': 'D',
        'description': 'Queratometría ojo derecho - meridiano curvo',
        'is_active': True,
    },
    {
        'name': 'Queratometría OD Eje',
        'code': 'KERAT_OD_AXIS',
        'category': 'queratometria',
        'data_type': 'integer',
        'unit': '°',
        'description': 'Queratometría ojo derecho - eje',
        'is_active': True,
    },
    {
        'name': 'Queratometría OS K1',
        'code': 'KERAT_OS_K1',
        'category': 'queratometria',
        'data_type': 'decimal',
        'unit': 'D',
        'description': 'Queratometría ojo izquierdo - meridiano plano',
        'is_active': True,
    },
    {
        'name': 'Queratometría OS K2',
        'code': 'KERAT_OS_K2',
        'category': 'queratometria',
        'data_type': 'decimal',
        'unit': 'D',
        'description': 'Queratometría ojo izquierdo - meridiano curvo',
        'is_active': True,
    },
    {
        'name': 'Queratometría OS Eje',
        'code': 'KERAT_OS_AXIS',
        'category': 'queratometria',
        'data_type': 'integer',
        'unit': '°',
        'description': 'Queratometría ojo izquierdo - eje',
        'is_active': True,
    },
    
    # MOTILIDAD OCULAR
    {
        'name': 'Ducciones',
        'code': 'DUCTIONS',
        'category': 'motilidad',
        'data_type': 'text',
        'unit': '',
        'description': 'Evaluación de ducciones oculares',
        'is_active': True,
    },
    {
        'name': 'Versiones',
        'code': 'VERSIONS',
        'category': 'motilidad',
        'data_type': 'text',
        'unit': '',
        'description': 'Evaluación de versiones oculares',
        'is_active': True,
    },
    {
        'name': 'Cover Test Lejos',
        'code': 'COVER_TEST_DISTANCE',
        'category': 'motilidad',
        'data_type': 'text',
        'unit': '',
        'description': 'Cover test a distancia',
        'is_active': True,
    },
    {
        'name': 'Cover Test Cerca',
        'code': 'COVER_TEST_NEAR',
        'category': 'motilidad',
        'data_type': 'text',
        'unit': '',
        'description': 'Cover test cerca',
        'is_active': True,
    },
    
    # DISTANCIA PUPILAR
    {
        'name': 'Distancia Pupilar Lejos',
        'code': 'PD_DISTANCE',
        'category': 'biometria',
        'data_type': 'decimal',
        'unit': 'mm',
        'description': 'Distancia pupilar para lejos',
        'is_active': True,
    },
    {
        'name': 'Distancia Pupilar Cerca',
        'code': 'PD_NEAR',
        'category': 'biometria',
        'data_type': 'decimal',
        'unit': 'mm',
        'description': 'Distancia pupilar para cerca',
        'is_active': True,
    },
    {
        'name': 'DP Monocular OD',
        'code': 'PD_OD',
        'category': 'biometria',
        'data_type': 'decimal',
        'unit': 'mm',
        'description': 'Distancia pupilar monocular ojo derecho',
        'is_active': True,
    },
    {
        'name': 'DP Monocular OS',
        'code': 'PD_OS',
        'category': 'biometria',
        'data_type': 'decimal',
        'unit': 'mm',
        'description': 'Distancia pupilar monocular ojo izquierdo',
        'is_active': True,
    },
    
    # BIOMICROSCOPÍA
    {
        'name': 'Biomicroscopía OD',
        'code': 'BIOMICROSCOPY_OD',
        'category': 'biomicroscopia',
        'data_type': 'text',
        'unit': '',
        'description': 'Hallazgos biomicroscopía ojo derecho',
        'is_active': True,
    },
    {
        'name': 'Biomicroscopía OS',
        'code': 'BIOMICROSCOPY_OS',
        'category': 'biomicroscopia',
        'data_type': 'text',
        'unit': '',
        'description': 'Hallazgos biomicroscopía ojo izquierdo',
        'is_active': True,
    },
    
    # FONDO DE OJO
    {
        'name': 'Fondo de Ojo OD',
        'code': 'FUNDOSCOPY_OD',
        'category': 'fondo_ojo',
        'data_type': 'text',
        'unit': '',
        'description': 'Hallazgos fondo de ojo derecho',
        'is_active': True,
    },
    {
        'name': 'Fondo de Ojo OS',
        'code': 'FUNDOSCOPY_OS',
        'category': 'fondo_ojo',
        'data_type': 'text',
        'unit': '',
        'description': 'Hallazgos fondo de ojo izquierdo',
        'is_active': True,
    },
    
    # VISIÓN DE COLORES
    {
        'name': 'Test Ishihara',
        'code': 'ISHIHARA_TEST',
        'category': 'vision_colores',
        'data_type': 'text',
        'unit': '',
        'description': 'Resultado test Ishihara',
        'is_active': True,
    },
    
    # PRUEBAS ADICIONALES
    {
        'name': 'Estereopsis',
        'code': 'STEREOPSIS',
        'category': 'vision_binocular',
        'data_type': 'text',
        'unit': 'arcsec',
        'description': 'Medición de estereopsis',
        'is_active': True,
    },
    {
        'name': 'Acomodación',
        'code': 'ACCOMMODATION',
        'category': 'vision_binocular',
        'data_type': 'text',
        'unit': '',
        'description': 'Evaluación de acomodación',
        'is_active': True,
    },
    {
        'name': 'Convergencia',
        'code': 'CONVERGENCE',
        'category': 'vision_binocular',
        'data_type': 'text',
        'unit': 'cm',
        'description': 'Punto próximo de convergencia',
        'is_active': True,
    },
]


def main():
    print("🔧 AGREGANDO PARÁMETROS CLÍNICOS")
    print("=" * 50)
    
    added_count = 0
    updated_count = 0
    skipped_count = 0
    
    for param_data in CLINICAL_PARAMETERS:
        code = param_data['code']
        
        # Verificar si ya existe
        existing = ClinicalParameter.objects.filter(code=code).first()
        
        if existing:
            # Actualizar parámetro existente
            for key, value in param_data.items():
                setattr(existing, key, value)
            existing.save()
            updated_count += 1
            print(f"✏️  Actualizado: {param_data['name']}")
        else:
            # Crear nuevo parámetro
            ClinicalParameter.objects.create(**param_data)
            added_count += 1
            print(f"✅ Agregado: {param_data['name']}")
    
    print("\n" + "=" * 50)
    print(f"📊 RESUMEN:")
    print(f"   ✅ Agregados: {added_count}")
    print(f"   ✏️  Actualizados: {updated_count}")
    print(f"   📋 Total de parámetros: {len(CLINICAL_PARAMETERS)}")
    print("\n✨ Parámetros clínicos configurados correctamente")


if __name__ == '__main__':
    main()
