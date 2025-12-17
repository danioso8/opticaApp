"""
Script para poblar parámetros clínicos globales estándar
Estos parámetros estarán disponibles para todas las organizaciones
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from apps.patients.models_clinical_config import ClinicalParameter

def create_global_params():
    """Crea parámetros clínicos globales estándar"""
    
    print("🔧 Creando parámetros clínicos globales...")
    print("=" * 60)
    
    # ========== MATERIALES DE LENTES ==========
    print("\n📦 Materiales de Lentes...")
    lens_materials = [
        {
            'name': 'CR-39 (Resina Estándar)',
            'code': 'CR39',
            'description': 'Plástico orgánico estándar, índice de refracción 1.498',
            'category': 'Estándar',
            'display_order': 1
        },
        {
            'name': 'Policarbonato',
            'code': 'PC',
            'description': 'Material resistente a impactos, índice 1.586, ideal para niños y deportes',
            'category': 'Resistente',
            'display_order': 2
        },
        {
            'name': 'Trivex',
            'code': 'TRX',
            'description': 'Material ligero y resistente, índice 1.53, excelente óptica',
            'category': 'Resistente',
            'display_order': 3
        },
        {
            'name': 'Alto Índice 1.60',
            'code': 'HI160',
            'description': 'Lente delgado, índice 1.60, para graduaciones medias',
            'category': 'Alto Índice',
            'display_order': 4
        },
        {
            'name': 'Alto Índice 1.67',
            'code': 'HI167',
            'description': 'Lente muy delgado, índice 1.67, para graduaciones altas',
            'category': 'Alto Índice',
            'display_order': 5
        },
        {
            'name': 'Alto Índice 1.74',
            'code': 'HI174',
            'description': 'Lente ultra delgado, índice 1.74, para graduaciones muy altas',
            'category': 'Alto Índice',
            'display_order': 6
        },
        {
            'name': 'Vidrio Crown',
            'code': 'GLASS',
            'description': 'Cristal mineral, excelente óptica pero pesado',
            'category': 'Mineral',
            'display_order': 7
        },
    ]
    
    for material in lens_materials:
        ClinicalParameter.objects.create(
            organization=None,  # Global
            parameter_type='lens_material',
            is_active=True,
            **material
        )
    print(f"   ✅ {len(lens_materials)} materiales creados")
    
    # ========== TRATAMIENTOS/RECUBRIMIENTOS ==========
    print("\n🛡️  Tratamientos y Recubrimientos...")
    treatments = [
        {
            'name': 'Antireflejo',
            'code': 'AR',
            'description': 'Reduce reflejos y brillos, mejora la visión nocturna',
            'category': 'Antireflejo',
            'display_order': 1
        },
        {
            'name': 'Antireflejo Premium',
            'code': 'AR-PRO',
            'description': 'Antireflejo avanzado con repelente al agua y polvo',
            'category': 'Antireflejo',
            'display_order': 2
        },
        {
            'name': 'Blue Light (Luz Azul)',
            'code': 'BL',
            'description': 'Filtra luz azul de pantallas digitales',
            'category': 'Filtro',
            'display_order': 3
        },
        {
            'name': 'Fotocromático',
            'code': 'PHOTO',
            'description': 'Se oscurece con la luz solar',
            'category': 'Transición',
            'display_order': 4
        },
        {
            'name': 'Transitions Signature',
            'code': 'TRANS-SIG',
            'description': 'Fotocromático Transitions estándar',
            'category': 'Transición',
            'display_order': 5
        },
        {
            'name': 'Transitions XTRActive',
            'code': 'TRANS-XTR',
            'description': 'Fotocromático que oscurece también en el auto',
            'category': 'Transición',
            'display_order': 6
        },
        {
            'name': 'Polarizado',
            'code': 'POL',
            'description': 'Elimina reflejos de superficies horizontales',
            'category': 'Filtro',
            'display_order': 7
        },
        {
            'name': 'Espejo',
            'code': 'MIRROR',
            'description': 'Recubrimiento reflectante decorativo',
            'category': 'Estético',
            'display_order': 8
        },
        {
            'name': 'Endurecido',
            'code': 'HARD',
            'description': 'Protección contra rayaduras',
            'category': 'Endurecimiento',
            'display_order': 9
        },
        {
            'name': 'Hidrofóbico',
            'code': 'HYDRO',
            'description': 'Repele agua y facilita limpieza',
            'category': 'Protección',
            'display_order': 10
        },
        {
            'name': 'UV 400',
            'code': 'UV400',
            'description': 'Protección 100% contra rayos UV',
            'category': 'Protección',
            'display_order': 11
        },
        {
            'name': 'Antivaho',
            'code': 'ANTIFOG',
            'description': 'Previene empañamiento',
            'category': 'Protección',
            'display_order': 12
        },
    ]
    
    for treatment in treatments:
        ClinicalParameter.objects.create(
            organization=None,
            parameter_type='treatment',
            is_active=True,
            **treatment
        )
    print(f"   ✅ {len(treatments)} tratamientos creados")
    
    # ========== TIPOS DE LENTES ==========
    print("\n👓 Tipos de Lentes...")
    lens_types = [
        {
            'name': 'Monofocales',
            'code': 'MONO',
            'description': 'Una sola graduación, lejos o cerca',
            'category': 'Estándar',
            'display_order': 1
        },
        {
            'name': 'Bifocales',
            'code': 'BIF',
            'description': 'Dos graduaciones, lejos y cerca con línea visible',
            'category': 'Multifocal',
            'display_order': 2
        },
        {
            'name': 'Trifocales',
            'code': 'TRIF',
            'description': 'Tres graduaciones, lejos, intermedia y cerca',
            'category': 'Multifocal',
            'display_order': 3
        },
        {
            'name': 'Progresivos',
            'code': 'PROG',
            'description': 'Transición gradual sin líneas, todas las distancias',
            'category': 'Multifocal',
            'display_order': 4
        },
        {
            'name': 'Progresivos Premium',
            'code': 'PROG-PRO',
            'description': 'Progresivos de alta gama con campos visuales amplios',
            'category': 'Multifocal',
            'display_order': 5
        },
        {
            'name': 'Ocupacionales',
            'code': 'OCC',
            'description': 'Optimizados para distancias intermedias y cerca',
            'category': 'Especializado',
            'display_order': 6
        },
        {
            'name': 'Deportivos',
            'code': 'SPORT',
            'description': 'Diseñados para actividades deportivas',
            'category': 'Especializado',
            'display_order': 7
        },
        {
            'name': 'Drive (Conducción)',
            'code': 'DRIVE',
            'description': 'Optimizados para conducción',
            'category': 'Especializado',
            'display_order': 8
        },
    ]
    
    for lens_type in lens_types:
        ClinicalParameter.objects.create(
            organization=None,
            parameter_type='lens_type',
            is_active=True,
            **lens_type
        )
    print(f"   ✅ {len(lens_types)} tipos de lentes creados")
    
    # ========== MARCAS DE LENTES ==========
    print("\n🏷️  Marcas de Lentes...")
    lens_brands = [
        {'name': 'Essilor', 'code': 'ESS', 'description': 'Marca líder francesa', 'display_order': 1},
        {'name': 'Zeiss', 'code': 'ZEISS', 'description': 'Óptica alemana de precisión', 'display_order': 2},
        {'name': 'Hoya', 'code': 'HOYA', 'description': 'Tecnología japonesa', 'display_order': 3},
        {'name': 'Transitions', 'code': 'TRANS', 'description': 'Líderes en fotocromáticos', 'display_order': 4},
        {'name': 'Varilux', 'code': 'VAR', 'description': 'Progresivos de Essilor', 'display_order': 5},
        {'name': 'Crizal', 'code': 'CRIZ', 'description': 'Tratamientos de Essilor', 'display_order': 6},
        {'name': 'Kodak', 'code': 'KOD', 'description': 'Lentes de calidad', 'display_order': 7},
        {'name': 'Rodenstock', 'code': 'ROD', 'description': 'Marca alemana premium', 'display_order': 8},
    ]
    
    for brand in lens_brands:
        ClinicalParameter.objects.create(
            organization=None,
            parameter_type='lens_brand',
            is_active=True,
            **brand
        )
    print(f"   ✅ {len(lens_brands)} marcas creadas")
    
    # ========== TIPOS DE MONTURAS ==========
    print("\n🕶️  Tipos de Monturas...")
    frame_types = [
        {'name': 'Completa (Full Rim)', 'code': 'FULL', 'description': 'Montura rodea completamente el lente', 'display_order': 1},
        {'name': 'Semi al Aire (Semi Rimless)', 'code': 'SEMI', 'description': 'Montura solo en la parte superior', 'display_order': 2},
        {'name': 'Al Aire (Rimless)', 'code': 'RIMLESS', 'description': 'Sin montura, lentes perforados', 'display_order': 3},
        {'name': 'Deportiva', 'code': 'SPORT', 'description': 'Diseño envolvente para deportes', 'display_order': 4},
        {'name': 'Aviador', 'code': 'AVIATOR', 'description': 'Estilo aviador clásico', 'display_order': 5},
        {'name': 'Wayfarer', 'code': 'WAYFARER', 'description': 'Estilo rectangular clásico', 'display_order': 6},
        {'name': 'Redonda', 'code': 'ROUND', 'description': 'Forma circular vintage', 'display_order': 7},
        {'name': 'Cat Eye', 'code': 'CATEYE', 'description': 'Estilo ojo de gato', 'display_order': 8},
    ]
    
    for frame in frame_types:
        ClinicalParameter.objects.create(
            organization=None,
            parameter_type='frame_type',
            is_active=True,
            **frame
        )
    print(f"   ✅ {len(frame_types)} tipos de monturas creados")
    
    # ========== LENTES DE CONTACTO - TIPOS ==========
    print("\n👁️  Lentes de Contacto - Tipos...")
    contact_types = [
        {'name': 'Blandos', 'code': 'SOFT', 'description': 'Lentes hidrofílicos flexibles', 'display_order': 1},
        {'name': 'Rígidos Permeables (RGP)', 'code': 'RGP', 'description': 'Lentes duros permeables al oxígeno', 'display_order': 2},
        {'name': 'Esféricos', 'code': 'SPH', 'description': 'Para miopía o hipermetropía', 'display_order': 3},
        {'name': 'Tóricos', 'code': 'TOR', 'description': 'Para astigmatismo', 'display_order': 4},
        {'name': 'Multifocales', 'code': 'MULTI', 'description': 'Para presbicia', 'display_order': 5},
        {'name': 'Cosméticos', 'code': 'COLOR', 'description': 'Con color o efecto', 'display_order': 6},
    ]
    
    for contact_type in contact_types:
        ClinicalParameter.objects.create(
            organization=None,
            parameter_type='contact_lens_type',
            is_active=True,
            **contact_type
        )
    print(f"   ✅ {len(contact_types)} tipos de LC creados")
    
    # ========== LENTES DE CONTACTO - MARCAS ==========
    print("\n🏷️  Lentes de Contacto - Marcas...")
    contact_brands = [
        {'name': 'Acuvue (Johnson & Johnson)', 'code': 'ACUVUE', 'display_order': 1},
        {'name': 'Biofinity (CooperVision)', 'code': 'BIO', 'display_order': 2},
        {'name': 'Air Optix (Alcon)', 'code': 'AIROPT', 'display_order': 3},
        {'name': 'Bausch + Lomb', 'code': 'BL', 'display_order': 4},
        {'name': 'Dailies (Alcon)', 'code': 'DAILY', 'display_order': 5},
        {'name': 'Proclear (CooperVision)', 'code': 'PROCLEAR', 'display_order': 6},
    ]
    
    for brand in contact_brands:
        ClinicalParameter.objects.create(
            organization=None,
            parameter_type='contact_lens_brand',
            is_active=True,
            **brand
        )
    print(f"   ✅ {len(contact_brands)} marcas de LC creadas")
    
    # ========== LENTES DE CONTACTO - RÉGIMEN ==========
    print("\n📅 Lentes de Contacto - Régimen de Uso...")
    wearing_schedules = [
        {'name': 'Diario Desechable', 'code': 'DAILY', 'description': 'Uso 1 día y desecha', 'display_order': 1},
        {'name': 'Quincenal', 'code': '2WEEK', 'description': 'Reemplazo cada 2 semanas', 'display_order': 2},
        {'name': 'Mensual', 'code': 'MONTH', 'description': 'Reemplazo cada mes', 'display_order': 3},
        {'name': 'Trimestral', 'code': '3MONTH', 'description': 'Reemplazo cada 3 meses', 'display_order': 4},
        {'name': 'Anual', 'code': 'YEAR', 'description': 'Reemplazo anual', 'display_order': 5},
        {'name': 'Uso Extendido', 'code': 'EXT', 'description': 'Se puede dormir con ellos', 'display_order': 6},
    ]
    
    for schedule in wearing_schedules:
        ClinicalParameter.objects.create(
            organization=None,
            parameter_type='contact_lens_wearing',
            is_active=True,
            **schedule
        )
    print(f"   ✅ {len(wearing_schedules)} regímenes creados")
    
    # ========== MEDICAMENTOS OFTÁLMICOS ==========
    print("\n💊 Medicamentos Oftálmicos Comunes...")
    medications = [
        {
            'name': 'Lágrimas Artificiales',
            'code': 'LAG-ART',
            'description': 'Lubricación ocular',
            'dosage': '1-2 gotas',
            'frequency': 'Según necesidad',
            'administration_route': 'ophthalmic',
            'category': 'Lubricante',
            'display_order': 1
        },
        {
            'name': 'Systane',
            'code': 'SYST',
            'description': 'Lágrimas artificiales premium',
            'dosage': '1-2 gotas',
            'frequency': '3-4 veces al día',
            'administration_route': 'ophthalmic',
            'category': 'Lubricante',
            'display_order': 2
        },
        {
            'name': 'Refresh',
            'code': 'REFR',
            'description': 'Lágrimas artificiales sin conservantes',
            'dosage': '1-2 gotas',
            'frequency': 'Según necesidad',
            'administration_route': 'ophthalmic',
            'category': 'Lubricante',
            'display_order': 3
        },
        {
            'name': 'Tobramicina',
            'code': 'TOBRA',
            'description': 'Antibiótico oftálmico',
            'dosage': '1 gota',
            'frequency': 'Cada 4-6 horas',
            'duration': '7-10 días',
            'administration_route': 'ophthalmic',
            'category': 'Antibiótico',
            'display_order': 4
        },
        {
            'name': 'Moxifloxacino',
            'code': 'MOXI',
            'description': 'Antibiótico de amplio espectro',
            'dosage': '1 gota',
            'frequency': 'Cada 8 horas',
            'duration': '7 días',
            'administration_route': 'ophthalmic',
            'category': 'Antibiótico',
            'display_order': 5
        },
        {
            'name': 'Prednisolona',
            'code': 'PRED',
            'description': 'Corticoide antiinflamatorio',
            'dosage': '1 gota',
            'frequency': 'Según indicación médica',
            'administration_route': 'ophthalmic',
            'category': 'Antiinflamatorio',
            'display_order': 6
        },
        {
            'name': 'Ketotifeno',
            'code': 'KETO',
            'description': 'Antihistamínico para alergias',
            'dosage': '1 gota',
            'frequency': 'Cada 8-12 horas',
            'administration_route': 'ophthalmic',
            'category': 'Antihistamínico',
            'display_order': 7
        },
        {
            'name': 'Timolol',
            'code': 'TIMOL',
            'description': 'Reduce presión intraocular',
            'dosage': '1 gota',
            'frequency': 'Cada 12 horas',
            'administration_route': 'ophthalmic',
            'category': 'Antiglaucoma',
            'display_order': 8
        },
        {
            'name': 'Latanoprost',
            'code': 'LATAN',
            'description': 'Reduce presión intraocular',
            'dosage': '1 gota',
            'frequency': 'Una vez al día (noche)',
            'administration_route': 'ophthalmic',
            'category': 'Antiglaucoma',
            'display_order': 9
        },
        {
            'name': 'Ciclopentolato',
            'code': 'CICLO',
            'description': 'Midriático ciclopléjico',
            'dosage': '1-2 gotas',
            'frequency': 'Según procedimiento',
            'administration_route': 'ophthalmic',
            'category': 'Midriático',
            'display_order': 10
        },
        {
            'name': 'Tropicamida',
            'code': 'TROPI',
            'description': 'Midriático de acción corta',
            'dosage': '1-2 gotas',
            'frequency': 'Antes del examen',
            'administration_route': 'ophthalmic',
            'category': 'Midriático',
            'display_order': 11
        },
    ]
    
    for med in medications:
        ClinicalParameter.objects.create(
            organization=None,
            parameter_type='topical_medication',
            is_active=True,
            **med
        )
    print(f"   ✅ {len(medications)} medicamentos creados")
    
    # ========== DIAGNÓSTICOS COMUNES ==========
    print("\n🩺 Diagnósticos Oftálmológicos Comunes...")
    diagnoses = [
        {
            'name': 'Miopía',
            'code': 'MYOPIA',
            'icd_10_code': 'H52.1',
            'description': 'Dificultad para ver de lejos',
            'category': 'Defecto Refractivo',
            'display_order': 1
        },
        {
            'name': 'Hipermetropía',
            'code': 'HYPER',
            'icd_10_code': 'H52.0',
            'description': 'Dificultad para ver de cerca',
            'category': 'Defecto Refractivo',
            'display_order': 2
        },
        {
            'name': 'Astigmatismo',
            'code': 'ASTIG',
            'icd_10_code': 'H52.2',
            'description': 'Visión distorsionada por córnea irregular',
            'category': 'Defecto Refractivo',
            'display_order': 3
        },
        {
            'name': 'Presbicia',
            'code': 'PRESB',
            'icd_10_code': 'H52.4',
            'description': 'Pérdida de acomodación por edad',
            'category': 'Defecto Refractivo',
            'display_order': 4
        },
        {
            'name': 'Ojo Seco',
            'code': 'DRY',
            'icd_10_code': 'H04.12',
            'description': 'Deficiencia de lágrima',
            'category': 'Superficie Ocular',
            'display_order': 5
        },
        {
            'name': 'Conjuntivitis',
            'code': 'CONJ',
            'icd_10_code': 'H10.9',
            'description': 'Inflamación de la conjuntiva',
            'category': 'Inflamatorio',
            'display_order': 6
        },
        {
            'name': 'Blefaritis',
            'code': 'BLEF',
            'icd_10_code': 'H01.0',
            'description': 'Inflamación de párpados',
            'category': 'Inflamatorio',
            'display_order': 7
        },
        {
            'name': 'Catarata',
            'code': 'CAT',
            'icd_10_code': 'H26.9',
            'description': 'Opacidad del cristalino',
            'category': 'Cristalino',
            'display_order': 8
        },
        {
            'name': 'Glaucoma',
            'code': 'GLAUC',
            'icd_10_code': 'H40.9',
            'description': 'Presión intraocular elevada',
            'category': 'Glaucoma',
            'display_order': 9
        },
        {
            'name': 'Retinopatía Diabética',
            'code': 'RET-DIAB',
            'icd_10_code': 'H36.0',
            'description': 'Daño retiniano por diabetes',
            'category': 'Retina',
            'display_order': 10
        },
        {
            'name': 'Degeneración Macular',
            'code': 'DMAE',
            'icd_10_code': 'H35.3',
            'description': 'Deterioro de la mácula',
            'category': 'Retina',
            'display_order': 11
        },
        {
            'name': 'Pterigión',
            'code': 'PTER',
            'icd_10_code': 'H11.0',
            'description': 'Crecimiento de tejido sobre córnea',
            'category': 'Superficie Ocular',
            'display_order': 12
        },
        {
            'name': 'Queratocono',
            'code': 'KERAT',
            'icd_10_code': 'H18.6',
            'description': 'Deformación cónica de la córnea',
            'category': 'Córnea',
            'display_order': 13
        },
    ]
    
    for diagnosis in diagnoses:
        ClinicalParameter.objects.create(
            organization=None,
            parameter_type='diagnosis',
            is_active=True,
            **diagnosis
        )
    print(f"   ✅ {len(diagnoses)} diagnósticos creados")
    
    # ========== EXÁMENES COMPLEMENTARIOS ==========
    print("\n🔬 Exámenes Complementarios...")
    exams = [
        {'name': 'Campimetría Visual', 'code': 'CAMPO', 'description': 'Mapa del campo visual', 'display_order': 1},
        {'name': 'Topografía Corneal', 'code': 'TOPO', 'description': 'Mapeo de la córnea', 'display_order': 2},
        {'name': 'OCT (Tomografía Óptica)', 'code': 'OCT', 'description': 'Imagen de retina y nervio óptico', 'display_order': 3},
        {'name': 'Paquimetría', 'code': 'PAQUI', 'description': 'Medición del espesor corneal', 'display_order': 4},
        {'name': 'Tonometría', 'code': 'TONO', 'description': 'Medición de presión intraocular', 'display_order': 5},
        {'name': 'Gonioscopia', 'code': 'GONIO', 'description': 'Examen del ángulo de la cámara anterior', 'display_order': 6},
        {'name': 'Fondo de Ojo', 'code': 'FONDO', 'description': 'Examen de retina con dilatación', 'display_order': 7},
        {'name': 'Retinografía', 'code': 'RETINO', 'description': 'Fotografía de la retina', 'display_order': 8},
        {'name': 'Angiografía Fluoresceínica', 'code': 'AGF', 'description': 'Estudio de vasos retinianos', 'display_order': 9},
        {'name': 'Ecografía Ocular', 'code': 'ECO', 'description': 'Ultrasonido del globo ocular', 'display_order': 10},
        {'name': 'Biometría', 'code': 'BIO', 'description': 'Medición para cirugía de catarata', 'display_order': 11},
    ]
    
    for exam in exams:
        ClinicalParameter.objects.create(
            organization=None,
            parameter_type='complementary_exam',
            is_active=True,
            **exam
        )
    print(f"   ✅ {len(exams)} exámenes complementarios creados")
    
    # ========== TRATAMIENTOS NO FARMACOLÓGICOS ==========
    print("\n🔧 Tratamientos y Terapias...")
    therapies = [
        {'name': 'Terapia Visual', 'code': 'TV', 'description': 'Ejercicios para mejorar función visual', 'display_order': 1},
        {'name': 'Ortóptica', 'code': 'ORTOP', 'description': 'Tratamiento de desviaciones oculares', 'display_order': 2},
        {'name': 'Higiene Palpebral', 'code': 'HIG-PALP', 'description': 'Limpieza de párpados', 'display_order': 3},
        {'name': 'Oclusión Ocular', 'code': 'OCLUS', 'description': 'Parche para ambliopía', 'display_order': 4},
        {'name': 'Compresás Calientes', 'code': 'COMP-CAL', 'description': 'Para blefaritis y orzuelo', 'display_order': 5},
    ]
    
    for therapy in therapies:
        ClinicalParameter.objects.create(
            organization=None,
            parameter_type='visual_therapy',
            is_active=True,
            **therapy
        )
    print(f"   ✅ {len(therapies)} terapias creadas")
    
    # ========== ESPECIALIDADES PARA REMISIÓN ==========
    print("\n👨‍⚕️ Especialidades para Remisión...")
    specialties = [
        {'name': 'Oftalmólogo', 'description': 'Médico especialista en ojos', 'display_order': 1},
        {'name': 'Retinólogo', 'description': 'Especialista en retina', 'display_order': 2},
        {'name': 'Glaucomatólogo', 'description': 'Especialista en glaucoma', 'display_order': 3},
        {'name': 'Córnea y Segmento Anterior', 'description': 'Especialista en córnea', 'display_order': 4},
        {'name': 'Oculoplastia', 'description': 'Cirugía plástica ocular', 'display_order': 5},
        {'name': 'Estrabismo y Pediatría', 'description': 'Especialista en niños', 'display_order': 6},
        {'name': 'Neuro-oftalmología', 'description': 'Especialista en nervio óptico', 'display_order': 7},
        {'name': 'Uveítis', 'description': 'Especialista en inflamaciones', 'display_order': 8},
        {'name': 'Endocrinólogo', 'description': 'Para diabetes y tiroides', 'display_order': 9},
        {'name': 'Neurólogo', 'description': 'Para problemas neurológicos', 'display_order': 10},
    ]
    
    for specialty in specialties:
        ClinicalParameter.objects.create(
            organization=None,
            parameter_type='referral_specialty',
            is_active=True,
            **specialty
        )
    print(f"   ✅ {len(specialties)} especialidades creadas")
    
    # ========== RECOMENDACIONES COMUNES ==========
    print("\n💡 Recomendaciones Comunes...")
    recommendations = [
        {'name': 'Uso constante de lentes', 'description': 'Usar lentes todo el tiempo', 'display_order': 1},
        {'name': 'Uso de lentes para lejos', 'description': 'Solo para visión lejana', 'display_order': 2},
        {'name': 'Uso de lentes para cerca', 'description': 'Solo para lectura y cerca', 'display_order': 3},
        {'name': 'Protección solar', 'description': 'Usar lentes con UV400', 'display_order': 4},
        {'name': 'Descansos visuales', 'description': 'Regla 20-20-20: cada 20 min, mirar 20 seg a 20 pies', 'display_order': 5},
        {'name': 'Lubricación frecuente', 'description': 'Usar lágrimas artificiales', 'display_order': 6},
        {'name': 'Higiene de lentes de contacto', 'description': 'Limpieza y cuidado adecuado', 'display_order': 7},
        {'name': 'Control glicémico', 'description': 'Mantener diabetes controlada', 'display_order': 8},
        {'name': 'Control de presión arterial', 'description': 'Mantener tensión controlada', 'display_order': 9},
        {'name': 'Dieta rica en antioxidantes', 'description': 'Omega 3, luteína, zeaxantina', 'display_order': 10},
    ]
    
    for rec in recommendations:
        ClinicalParameter.objects.create(
            organization=None,
            parameter_type='recommendation',
            is_active=True,
            **rec
        )
    print(f"   ✅ {len(recommendations)} recomendaciones creadas")
    
    # ========== RESUMEN FINAL ==========
    print("\n" + "=" * 60)
    print("✅ PROCESO COMPLETADO")
    print("=" * 60)
    
    total = ClinicalParameter.objects.filter(organization__isnull=True).count()
    print(f"\n📊 Total de parámetros globales creados: {total}")
    print("\n💡 Estos parámetros estarán disponibles para todas las organizaciones")
    print("💡 Cada organización puede agregar sus propios parámetros personalizados")
    print("\n🚀 ¡El sistema está listo para usar!")

if __name__ == '__main__':
    create_global_params()
