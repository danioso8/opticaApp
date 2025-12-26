"""
Modelos para Historia Clínica Oftalmológica
"""
from django.db import models
from apps.organizations.base_models import TenantModel


class ClinicalHistory(TenantModel):
    """Historia Clínica Oftalmológica completa"""
    
    patient = models.ForeignKey(
        'patients.Patient', 
        on_delete=models.CASCADE, 
        related_name='clinical_histories',
        verbose_name='Paciente'
    )
    
    date = models.DateField(verbose_name='Fecha del Examen')
    last_eye_checkup = models.CharField(
        max_length=200,
        verbose_name='Tiempo del Último Control de Ojos',
        blank=True,
        help_text='Ej: Hace 1 año, Hace 6 meses, Primera vez, etc.'
    )
    doctor = models.ForeignKey(
        'patients.Doctor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clinical_histories',
        verbose_name='Médico/Optómetra'
    )
    
    # ==================== ANAMNESIS ====================
    # Motivo de Consulta (MC)
    chief_complaint = models.TextField(verbose_name='Motivo de Consulta (MC)', blank=True)
    
    # Enfermedad Actual (EA)
    current_illness = models.TextField(verbose_name='Enfermedad Actual (EA)', blank=True)
    
    # Condición Clínica Actual
    current_clinical_condition = models.TextField(verbose_name='Condición Clínica Actual', blank=True)
    
    # ==================== ANTECEDENTES GENERALES ====================
    pathological_history = models.TextField(verbose_name='Patológicos', blank=True, help_text='Enfermedades crónicas, patologías')
    pharmacological_history = models.TextField(verbose_name='Farmacológicos', blank=True, help_text='Medicamentos actuales')
    surgical_history = models.TextField(verbose_name='Quirúrgicos', blank=True, help_text='Cirugías previas generales')
    allergic_history = models.TextField(verbose_name='Alérgicos', blank=True, help_text='Alergias conocidas')
    trauma_history = models.TextField(verbose_name='Traumatológicos', blank=True, help_text='Traumatismos previos')
    other_general_history = models.TextField(verbose_name='Otros Generales', blank=True)
    
    # Backward compatibility
    medical_history = models.TextField(verbose_name='Antecedentes Médicos (Legacy)', blank=True, help_text='Campo antiguo - usar los específicos')
    
    # ==================== ANTECEDENTES OCULARES ====================
    ocular_pathological_history = models.TextField(verbose_name='Patológicos Oculares', blank=True)
    ocular_pharmacological_history = models.TextField(verbose_name='Farmacológicos Oculares', blank=True)
    ocular_surgical_history = models.TextField(verbose_name='Quirúrgicos Oculares', blank=True)
    ocular_trauma_history = models.TextField(verbose_name='Traumatológicos Oculares', blank=True)
    
    # Lensometría - Medición de lentes actuales
    lensometry_lens_type = models.ForeignKey(
        'patients.ClinicalParameter',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='lensometry_histories',
        verbose_name='Tipo de Lente (Lensometría)',
        limit_choices_to={'parameter_type': 'lens_type', 'is_active': True}
    )
    lensometry_notes = models.TextField(verbose_name='Notas de Lensometría', blank=True, help_text='Mediciones de lentes actuales del paciente')
    
    # Fórmula de Lentes Actuales - OD
    current_rx_od_sphere = models.CharField(max_length=20, blank=True, null=True, verbose_name='Fórmula Actual OD Esfera', help_text='Ej: +2.00, -1.50, N, NLP')
    current_rx_od_cylinder = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Fórmula Actual OD Cilindro')
    current_rx_od_axis = models.IntegerField(null=True, blank=True, verbose_name='Fórmula Actual OD Eje')
    current_rx_od_add = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Fórmula Actual OD ADD')
    
    # Fórmula de Lentes Actuales - OS
    current_rx_os_sphere = models.CharField(max_length=20, blank=True, null=True, verbose_name='Fórmula Actual OS Esfera', help_text='Ej: +2.00, -1.50, N, NLP')
    current_rx_os_cylinder = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Fórmula Actual OS Cilindro')
    current_rx_os_axis = models.IntegerField(null=True, blank=True, verbose_name='Fórmula Actual OS Eje')
    current_rx_os_add = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Fórmula Actual OS ADD')
    
    # Backward compatibility
    ocular_therapeutic_history = models.TextField(verbose_name='Terapéuticos Oculares (Legacy)', blank=True, help_text='Campo antiguo - usar lensometría')
    
    # Signos y Síntomas (Semiología Clínica)
    blurred_vision = models.BooleanField(default=False, verbose_name='Visión Borrosa')
    eye_pain = models.BooleanField(default=False, verbose_name='Dolor Ocular')
    headaches = models.BooleanField(default=False, verbose_name='Cefaleas')
    photophobia = models.BooleanField(default=False, verbose_name='Fotofobia')
    diplopia = models.BooleanField(default=False, verbose_name='Diplopía (Visión Doble)')
    tearing = models.BooleanField(default=False, verbose_name='Lagrimeo')
    redness = models.BooleanField(default=False, verbose_name='Enrojecimiento')
    itching = models.BooleanField(default=False, verbose_name='Picazón')
    floaters = models.BooleanField(default=False, verbose_name='Moscas Volantes')
    halos = models.BooleanField(default=False, verbose_name='Halos de Luz')
    
    symptoms_notes = models.TextField(verbose_name='Notas de Síntomas', blank=True)
    
    # Antecedentes Oftalmológicos
    previous_eye_surgery = models.BooleanField(default=False, verbose_name='Cirugía Ocular Previa')
    surgery_details = models.TextField(verbose_name='Detalles de Cirugías', blank=True)
    previous_glasses = models.BooleanField(default=False, verbose_name='Usa Lentes Previos')
    glasses_since = models.CharField(max_length=50, verbose_name='Usa Lentes Desde', blank=True)
    previous_contact_lenses = models.BooleanField(default=False, verbose_name='Uso de Lentes de Contacto')
    
    # ==================== ANTECEDENTES FAMILIARES ====================
    # Generales
    family_diabetes = models.BooleanField(default=False, verbose_name='Diabetes (Familiar)')
    family_hypertension = models.BooleanField(default=False, verbose_name='Hipertensión (Familiar)')
    family_heart_disease = models.BooleanField(default=False, verbose_name='Cardiopatías (Familiar)')
    family_cancer = models.BooleanField(default=False, verbose_name='Cáncer (Familiar)')
    family_general_notes = models.TextField(verbose_name='Notas Familiares Generales', blank=True)
    
    # Oculares
    family_glaucoma = models.BooleanField(default=False, verbose_name='Glaucoma (Familiar)')
    family_cataracts = models.BooleanField(default=False, verbose_name='Cataratas (Familiar)')
    family_macular_degeneration = models.BooleanField(default=False, verbose_name='Degeneración Macular (Familiar)')
    family_retinal_detachment = models.BooleanField(default=False, verbose_name='Desprendimiento de Retina (Familiar)')
    family_myopia = models.BooleanField(default=False, verbose_name='Miopía (Familiar)')
    family_strabismus = models.BooleanField(default=False, verbose_name='Estrabismo (Familiar)')
    family_ocular_notes = models.TextField(verbose_name='Notas Familiares Oculares', blank=True)
    
    # Backward compatibility
    family_history_notes = models.TextField(verbose_name='Notas Antecedentes Familiares (Legacy)', blank=True)
    
    # Hábitos
    occupation_visual_demand = models.CharField(
        max_length=50,
        choices=[
            ('high', 'Alta (Computadora, lectura)'),
            ('medium', 'Media'),
            ('low', 'Baja')
        ],
        verbose_name='Demanda Visual Ocupacional',
        blank=True
    )
    screen_hours_daily = models.IntegerField(verbose_name='Horas Diarias de Pantalla', null=True, blank=True)
    reading_hours_daily = models.IntegerField(verbose_name='Horas Diarias de Lectura', null=True, blank=True)
    
    # ==================== AGUDEZA VISUAL ====================
    
    # Cartillas utilizadas
    distance_chart = models.CharField(
        max_length=50, 
        verbose_name='Cartilla Visión Lejana', 
        blank=True,
        help_text='Cartilla utilizada para medir visión de lejos (ETDRS, Snellen, etc.)'
    )
    near_chart = models.CharField(
        max_length=50, 
        verbose_name='Cartilla Visión Próxima', 
        blank=True,
        help_text='Cartilla utilizada para medir visión de cerca (Jaeger, Rosenbaum, etc.)'
    )
    
    # Ojo Derecho (OD) - Sin Corrección
    va_od_sc_distance = models.CharField(max_length=20, verbose_name='AV OD SC Lejos', blank=True, help_text='Ej: 20/20, 20/40, 6/6')
    va_od_sc_near = models.CharField(max_length=20, verbose_name='AV OD SC Cerca', blank=True, help_text='Ej: J1, N5, a 40cm')
    
    # Ojo Derecho (OD) - Con Corrección
    va_od_cc_distance = models.CharField(max_length=20, verbose_name='AV OD CC Lejos', blank=True, help_text='Ej: 20/20, 20/40, 6/6')
    va_od_cc_near = models.CharField(max_length=20, verbose_name='AV OD CC Cerca', blank=True, help_text='Ej: J1, N5, a 40cm')
    
    # Ojo Izquierdo (OS) - Sin Corrección
    va_os_sc_distance = models.CharField(max_length=20, verbose_name='AV OS SC Lejos', blank=True, help_text='Ej: 20/20, 20/40, 6/6')
    va_os_sc_near = models.CharField(max_length=20, verbose_name='AV OS SC Cerca', blank=True, help_text='Ej: J1, N5, a 40cm')
    
    # Ojo Izquierdo (OS) - Con Corrección
    va_os_cc_distance = models.CharField(max_length=20, verbose_name='AV OS CC Lejos', blank=True, help_text='Ej: 20/20, 20/40, 6/6')
    va_os_cc_near = models.CharField(max_length=20, verbose_name='AV OS CC Cerca', blank=True, help_text='Ej: J1, N5, a 40cm')
    
    # Ambos Ojos (OU)
    va_ou_distance = models.CharField(max_length=20, verbose_name='AV OU Lejos', blank=True, help_text='Ej: 20/20, 6/6')
    va_ou_near = models.CharField(max_length=20, verbose_name='AV OU Cerca', blank=True, help_text='Ej: J1, a 40cm')
    
    # ==================== REFRACCIÓN ====================
    
    # Ojo Derecho (OD)
    refraction_od_sphere = models.CharField(max_length=10, verbose_name='OD Esfera', blank=True, help_text='Ej: +2.50, -1.25, N/A')
    refraction_od_cylinder = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='OD Cilindro', null=True, blank=True)
    refraction_od_axis = models.IntegerField(verbose_name='OD Eje', null=True, blank=True, help_text='0-180°')
    refraction_od_add = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='OD Adición', null=True, blank=True)
    refraction_od_prism = models.CharField(max_length=20, verbose_name='OD Prisma', blank=True)
    
    # Ojo Izquierdo (OS)
    refraction_os_sphere = models.CharField(max_length=10, verbose_name='OS Esfera', blank=True, help_text='Ej: +2.50, -1.25, N/A')
    refraction_os_cylinder = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='OS Cilindro', null=True, blank=True)
    refraction_os_axis = models.IntegerField(verbose_name='OS Eje', null=True, blank=True, help_text='0-180°')
    refraction_os_add = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='OS Adición', null=True, blank=True)
    refraction_os_prism = models.CharField(max_length=20, verbose_name='OS Prisma', blank=True)
    
    # DNP en refracción (Distance Nasale-Pupilar)
    refraction_od_dnp = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='OD DNP (mm)', null=True, blank=True, help_text='Distancia Nasal-Pupilar OD')
    refraction_os_dnp = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='OS DNP (mm)', null=True, blank=True, help_text='Distancia Nasal-Pupilar OS')
    
    # Distancia Pupilar
    pd_distance = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='DP Lejos (mm)', null=True, blank=True)
    pd_near = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='DP Cerca (mm)', null=True, blank=True)
    pd_od = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='DP OD', null=True, blank=True)
    pd_os = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='DP OS', null=True, blank=True)
    
    # ==================== EXÁMENES REFRACTIVOS ADICIONALES ====================
    
    # Checkboxes para indicar qué exámenes se realizaron
    exam_retinoscopy_done = models.BooleanField(default=False, verbose_name='Retinoscopia Realizada')
    exam_subjective_done = models.BooleanField(default=False, verbose_name='Subjetivo Realizado')
    exam_refinement_done = models.BooleanField(default=False, verbose_name='Afinación Realizada')
    exam_cycloplegic_done = models.BooleanField(default=False, verbose_name='Subjetivo bajo Cicloplejia Realizado')
    exam_final_rx_done = models.BooleanField(default=False, verbose_name='RX Final Realizado')
    
    # RETINOSCOPIA
    retinoscopy_od_sphere = models.CharField(max_length=20, blank=True, null=True, verbose_name='Retinoscopia OD Esfera')
    retinoscopy_od_cylinder = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Retinoscopia OD Cilindro')
    retinoscopy_od_axis = models.IntegerField(null=True, blank=True, verbose_name='Retinoscopia OD Eje')
    retinoscopy_od_add = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Retinoscopia OD ADD')
    retinoscopy_os_sphere = models.CharField(max_length=20, blank=True, null=True, verbose_name='Retinoscopia OS Esfera')
    retinoscopy_os_cylinder = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Retinoscopia OS Cilindro')
    retinoscopy_os_axis = models.IntegerField(null=True, blank=True, verbose_name='Retinoscopia OS Eje')
    retinoscopy_os_add = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Retinoscopia OS ADD')
    
    # SUBJETIVO
    subjective_od_sphere = models.CharField(max_length=20, blank=True, null=True, verbose_name='Subjetivo OD Esfera')
    subjective_od_cylinder = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Subjetivo OD Cilindro')
    subjective_od_axis = models.IntegerField(null=True, blank=True, verbose_name='Subjetivo OD Eje')
    subjective_od_add = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Subjetivo OD ADD')
    subjective_os_sphere = models.CharField(max_length=20, blank=True, null=True, verbose_name='Subjetivo OS Esfera')
    subjective_os_cylinder = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Subjetivo OS Cilindro')
    subjective_os_axis = models.IntegerField(null=True, blank=True, verbose_name='Subjetivo OS Eje')
    subjective_os_add = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Subjetivo OS ADD')
    
    # AFINACIÓN
    refinement_od_sphere = models.CharField(max_length=20, blank=True, null=True, verbose_name='Afinación OD Esfera')
    refinement_od_cylinder = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Afinación OD Cilindro')
    refinement_od_axis = models.IntegerField(null=True, blank=True, verbose_name='Afinación OD Eje')
    refinement_od_add = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Afinación OD ADD')
    refinement_os_sphere = models.CharField(max_length=20, blank=True, null=True, verbose_name='Afinación OS Esfera')
    refinement_os_cylinder = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Afinación OS Cilindro')
    refinement_os_axis = models.IntegerField(null=True, blank=True, verbose_name='Afinación OS Eje')
    refinement_os_add = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Afinación OS ADD')
    
    # SUBJETIVO BAJO CICLOPLEJIA
    cycloplegic_od_sphere = models.CharField(max_length=20, blank=True, null=True, verbose_name='Ciclopléjico OD Esfera')
    cycloplegic_od_cylinder = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Ciclopléjico OD Cilindro')
    cycloplegic_od_axis = models.IntegerField(null=True, blank=True, verbose_name='Ciclopléjico OD Eje')
    cycloplegic_od_add = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Ciclopléjico OD ADD')
    cycloplegic_os_sphere = models.CharField(max_length=20, blank=True, null=True, verbose_name='Ciclopléjico OS Esfera')
    cycloplegic_os_cylinder = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Ciclopléjico OS Cilindro')
    cycloplegic_os_axis = models.IntegerField(null=True, blank=True, verbose_name='Ciclopléjico OS Eje')
    cycloplegic_os_add = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='Ciclopléjico OS ADD')
    
    # RX FINAL
    final_rx_od_sphere = models.CharField(max_length=20, blank=True, null=True, verbose_name='RX Final OD Esfera')
    final_rx_od_cylinder = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='RX Final OD Cilindro')
    final_rx_od_axis = models.IntegerField(null=True, blank=True, verbose_name='RX Final OD Eje')
    final_rx_od_add = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='RX Final OD ADD')
    final_rx_os_sphere = models.CharField(max_length=20, blank=True, null=True, verbose_name='RX Final OS Esfera')
    final_rx_os_cylinder = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='RX Final OS Cilindro')
    final_rx_os_axis = models.IntegerField(null=True, blank=True, verbose_name='RX Final OS Eje')
    final_rx_os_add = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, verbose_name='RX Final OS ADD')
    
    # ==================== QUERATOMETRÍA ====================
    
    # Ojo Derecho
    keratometry_od_k1 = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='OD K1', null=True, blank=True)
    keratometry_od_k1_axis = models.IntegerField(verbose_name='OD K1 Eje', null=True, blank=True)
    keratometry_od_k2 = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='OD K2', null=True, blank=True)
    keratometry_od_k2_axis = models.IntegerField(verbose_name='OD K2 Eje', null=True, blank=True)
    
    # Ojo Izquierdo
    keratometry_os_k1 = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='OS K1', null=True, blank=True)
    keratometry_os_k1_axis = models.IntegerField(verbose_name='OS K1 Eje', null=True, blank=True)
    keratometry_os_k2 = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='OS K2', null=True, blank=True)
    keratometry_os_k2_axis = models.IntegerField(verbose_name='OS K2 Eje', null=True, blank=True)
    
    # ==================== TONOMETRÍA (Presión Intraocular) ====================
    
    iop_od = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='PIO OD (mmHg)', null=True, blank=True)
    iop_os = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='PIO OS (mmHg)', null=True, blank=True)
    iop_method = models.CharField(
        max_length=50,
        choices=[
            ('goldman', 'Goldman'),
            ('air_puff', 'Aire (Soplo)'),
            ('tonopen', 'Tonopen'),
            ('other', 'Otro')
        ],
        verbose_name='Método de Tonometría',
        blank=True
    )
    
    # ==================== EXAMEN OCULAR (BIOMICROSCOPÍA) ====================
    
    # Segmento Anterior OD
    biomicroscopy_od_lids = models.TextField(verbose_name='OD Párpados', blank=True)
    biomicroscopy_od_conjunctiva = models.TextField(verbose_name='OD Conjuntiva', blank=True)
    biomicroscopy_od_cornea = models.TextField(verbose_name='OD Córnea', blank=True)
    biomicroscopy_od_anterior_chamber = models.TextField(verbose_name='OD Cámara Anterior', blank=True)
    biomicroscopy_od_iris = models.TextField(verbose_name='OD Iris', blank=True)
    biomicroscopy_od_lens = models.TextField(verbose_name='OD Cristalino', blank=True)
    biomicroscopy_od_pupil = models.TextField(verbose_name='OD Pupila', blank=True, help_text='Tamaño, forma, reactividad')
    
    # Segmento Anterior OS
    biomicroscopy_os_lids = models.TextField(verbose_name='OS Párpados', blank=True)
    biomicroscopy_os_conjunctiva = models.TextField(verbose_name='OS Conjuntiva', blank=True)
    biomicroscopy_os_cornea = models.TextField(verbose_name='OS Córnea', blank=True)
    biomicroscopy_os_anterior_chamber = models.TextField(verbose_name='OS Cámara Anterior', blank=True)
    biomicroscopy_os_iris = models.TextField(verbose_name='OS Iris', blank=True)
    biomicroscopy_os_lens = models.TextField(verbose_name='OS Cristalino', blank=True)
    biomicroscopy_os_pupil = models.TextField(verbose_name='OS Pupila', blank=True, help_text='Tamaño, forma, reactividad')
    
    # ==================== EXAMEN EXTERNO ====================
    external_exam_od = models.TextField(verbose_name='Examen Externo OD', blank=True, help_text='Anexos oculares, órbita, etc.')
    external_exam_os = models.TextField(verbose_name='Examen Externo OS', blank=True)
    
    # ==================== EXAMEN OFTALMOSCÓPICO (FONDO DE OJO) ====================
    
    # Ojo Derecho
    fundoscopy_od_vitreous = models.TextField(verbose_name='OD Vítreo', blank=True)
    fundoscopy_od_optic_disc = models.TextField(verbose_name='OD Disco Óptico', blank=True)
    fundoscopy_od_cup_disc_ratio = models.CharField(max_length=10, verbose_name='OD Relación Copa/Disco', blank=True, help_text='Ej: 0.3')
    fundoscopy_od_macula = models.TextField(verbose_name='OD Mácula', blank=True)
    fundoscopy_od_vessels = models.TextField(verbose_name='OD Vasos', blank=True)
    fundoscopy_od_periphery = models.TextField(verbose_name='OD Periferia', blank=True)
    fundoscopy_od_retina = models.TextField(verbose_name='OD Retina', blank=True)
    
    # Ojo Izquierdo
    fundoscopy_os_vitreous = models.TextField(verbose_name='OS Vítreo', blank=True)
    fundoscopy_os_optic_disc = models.TextField(verbose_name='OS Disco Óptico', blank=True)
    fundoscopy_os_cup_disc_ratio = models.CharField(max_length=10, verbose_name='OS Relación Copa/Disco', blank=True, help_text='Ej: 0.3')
    fundoscopy_os_macula = models.TextField(verbose_name='OS Mácula', blank=True)
    fundoscopy_os_vessels = models.TextField(verbose_name='OS Vasos', blank=True)
    fundoscopy_os_periphery = models.TextField(verbose_name='OS Periferia', blank=True)
    fundoscopy_os_retina = models.TextField(verbose_name='OS Retina', blank=True)
    
    # ==================== MOTILIDAD OCULAR ====================
    
    motility_od = models.TextField(verbose_name='Motilidad OD', blank=True, help_text='Movimientos extraoculares')
    motility_os = models.TextField(verbose_name='Motilidad OS', blank=True)
    cover_test = models.TextField(verbose_name='Test de Cover', blank=True)
    convergence = models.CharField(max_length=100, verbose_name='Convergencia', blank=True)
    
    # ==================== VISIÓN DE COLORES ====================
    
    color_vision_od = models.CharField(
        max_length=50,
        choices=[
            ('normal', 'Normal'),
            ('abnormal', 'Anormal'),
            ('not_tested', 'No Evaluado')
        ],
        verbose_name='Visión de Colores OD',
        blank=True
    )
    color_vision_os = models.CharField(
        max_length=50,
        choices=[
            ('normal', 'Normal'),
            ('abnormal', 'Anormal'),
            ('not_tested', 'No Evaluado')
        ],
        verbose_name='Visión de Colores OS',
        blank=True
    )
    color_vision_test = models.CharField(max_length=50, verbose_name='Test Utilizado', blank=True, help_text='Ej: Ishihara')
    
    # ==================== EXÁMENES COMPLEMENTARIOS ====================
    complementary_exams = models.TextField(verbose_name='Exámenes Complementarios', blank=True, help_text='OCT, Campo Visual, Topografía, etc.')
    
    # ==================== DIAGNÓSTICO ====================
    
    diagnosis = models.TextField(verbose_name='Diagnóstico', blank=True)
    differential_diagnosis = models.TextField(verbose_name='Diagnóstico Diferencial', blank=True)
    
    # Diagnósticos comunes (checkboxes)
    dx_myopia = models.BooleanField(default=False, verbose_name='Miopía')
    dx_hyperopia = models.BooleanField(default=False, verbose_name='Hipermetropía')
    dx_astigmatism = models.BooleanField(default=False, verbose_name='Astigmatismo')
    dx_presbyopia = models.BooleanField(default=False, verbose_name='Presbicia')
    dx_amblyopia = models.BooleanField(default=False, verbose_name='Ambliopía')
    dx_strabismus = models.BooleanField(default=False, verbose_name='Estrabismo')
    dx_cataracts = models.BooleanField(default=False, verbose_name='Cataratas')
    dx_glaucoma = models.BooleanField(default=False, verbose_name='Glaucoma')
    dx_dry_eye = models.BooleanField(default=False, verbose_name='Ojo Seco')
    dx_conjunctivitis = models.BooleanField(default=False, verbose_name='Conjuntivitis')
    dx_keratoconus = models.BooleanField(default=False, verbose_name='Queratocono')
    
    # ==================== PRONÓSTICO ====================
    prognosis = models.TextField(verbose_name='Pronóstico', blank=True)
    
    # ==================== DISPOSICIÓN (Plan de Manejo) ====================
    disposition = models.TextField(verbose_name='Disposición', blank=True, help_text='Plan inmediato y manejo')
    
    # Plan de Tratamiento
    treatment_plan = models.TextField(verbose_name='Plan de Tratamiento', blank=True)
    
    # ==================== PRESCRIPCIÓN FARMACÉUTICA ====================
    pharmaceutical_prescription = models.TextField(
        verbose_name='Prescripción Farmacéutica', 
        blank=True,
        help_text='Medicamentos recetados: nombre, dosis, vía, frecuencia, duración'
    )
    
    # Protocolo de prescripción de fármacos tópicos oftálmicos
    topical_medication_protocol = models.TextField(
        verbose_name='Protocolo Fármacos Tópicos Oftálmicos',
        blank=True,
        help_text='Gotas, ungüentos, lubricantes oculares'
    )
    
    # Terapias coadyuvantes
    adjuvant_therapies = models.TextField(
        verbose_name='Terapias Coadyuvantes',
        blank=True,
        help_text='Terapias complementarias, ejercicios visuales, etc.'
    )
    
    prescription_glasses = models.BooleanField(default=False, verbose_name='Prescripción de Lentes')
    prescription_contact_lenses = models.BooleanField(default=False, verbose_name='Prescripción de LC')
    prescription_medication = models.BooleanField(default=False, verbose_name='Prescripción de Medicamentos')
    medication_details = models.TextField(verbose_name='Detalles de Medicación', blank=True)
    
    # ==================== PRESCRIPCIÓN ÓPTICA ====================
    optical_prescription_notes = models.TextField(
        verbose_name='Notas de Prescripción Óptica',
        blank=True,
        help_text='Detalles adicionales sobre la prescripción óptica'
    )
    
    # Tipo de Lentes Recomendados
    lens_type = models.CharField(
        max_length=50,
        choices=[
            ('single', 'Monofocales'),
            ('bifocal', 'Bifocales'),
            ('progressive', 'Progresivos'),
            ('occupational', 'Ocupacionales'),
            ('reading', 'Lectura'),
        ],
        verbose_name='Tipo de Lentes',
        blank=True
    )
    
    lens_material = models.CharField(
        max_length=100,
        verbose_name='Material de Lentes',
        blank=True,
        help_text='Ej: CR-39, Policarbonato, Alto Índice'
    )
    
    lens_coating = models.CharField(
        max_length=200,
        verbose_name='Tratamientos/Recubrimientos',
        blank=True,
        help_text='Ej: Antireflejo, Blue Block, Fotocromático'
    )
    
    lens_brand = models.CharField(max_length=100, verbose_name='Marca de Lentes', blank=True)
    frame_type = models.CharField(max_length=100, verbose_name='Tipo de Montura', blank=True)
    
    # ==================== LENTES DE CONTACTO ====================
    contact_lens_type = models.CharField(max_length=100, verbose_name='Tipo de Lentes de Contacto', blank=True)
    contact_lens_brand = models.CharField(max_length=100, verbose_name='Marca de LC', blank=True)
    contact_lens_material = models.CharField(max_length=100, verbose_name='Material de LC', blank=True)
    contact_lens_wearing = models.CharField(max_length=100, verbose_name='Régimen de Uso LC', blank=True)
    
    # ==================== TERAPIAS ====================
    therapy = models.TextField(verbose_name='Terapias Coadyuvantes', blank=True)
    visual_therapy = models.TextField(verbose_name='Terapias Visuales', blank=True)
    
    # ==================== EXÁMENES Y SEGUIMIENTO ====================
    complementary_exam = models.TextField(verbose_name='Exámenes Complementarios Solicitados', blank=True)
    lab_test = models.TextField(verbose_name='Exámenes de Laboratorio', blank=True)
    recommendation = models.TextField(verbose_name='Recomendaciones Específicas', blank=True)
    follow_up_reason = models.CharField(max_length=200, verbose_name='Motivo de Seguimiento', blank=True)
    referral_specialty = models.CharField(max_length=200, verbose_name='Remisión a Especialidad', blank=True)
    
    # Campos adicionales de texto
    recommendations_text = models.TextField(verbose_name='Texto de Recomendaciones', blank=True)
    additional_notes = models.TextField(verbose_name='Notas Adicionales', blank=True)
    diagnosis_text = models.TextField(verbose_name='Texto de Diagnóstico Detallado', blank=True)
    
    # ==================== EVOLUCIÓN Y CONTROL ====================
    
    evolution_notes = models.TextField(verbose_name='Evolución', blank=True, help_text='Notas de evolución del paciente')
    follow_up_date = models.DateField(verbose_name='Fecha de Seguimiento', null=True, blank=True)
    follow_up_notes = models.TextField(verbose_name='Notas de Seguimiento', blank=True)
    
    # Remisión y Contrarremisión
    referral_to = models.CharField(max_length=200, verbose_name='Remisión a', blank=True, help_text='Especialista o institución')
    referral_reason = models.TextField(verbose_name='Motivo de Remisión', blank=True)
    counter_referral = models.TextField(verbose_name='Contrarremisión', blank=True, help_text='Respuesta de especialista')
    
    # ==================== RESUMEN DE HISTORIA CLÍNICA ====================
    clinical_summary = models.TextField(verbose_name='Resumen de Historia Clínica', blank=True, help_text='Resumen ejecutivo del caso')
    
    # ==================== OBSERVACIONES ====================
    
    observations = models.TextField(verbose_name='Observaciones Generales', blank=True)
    recommendations = models.TextField(verbose_name='Recomendaciones', blank=True)
    
    # ==================== PROCESOS DOCUMENTALES ====================
    
    # Consentimientos
    surgical_consent = models.BooleanField(default=False, verbose_name='Consentimiento Quirúrgico Firmado')
    surgical_consent_date = models.DateField(null=True, blank=True, verbose_name='Fecha Consentimiento Quirúrgico')
    cycloplegia_consent = models.BooleanField(default=False, verbose_name='Consentimiento Cicloplejia Firmado')
    cycloplegia_consent_date = models.DateField(null=True, blank=True, verbose_name='Fecha Consentimiento Cicloplejia')
    
    # Órdenes y Certificaciones
    lab_orders = models.TextField(verbose_name='Órdenes de Laboratorio', blank=True)
    specialized_exam_orders = models.TextField(verbose_name='Órdenes de Exámenes Especializados', blank=True, help_text='OCT, Campo Visual, etc.')
    medical_certificate = models.TextField(verbose_name='Certificaciones Médicas', blank=True)
    remission_document = models.TextField(verbose_name='Documento de Remisión', blank=True)
    
    # ==================== METADATA ====================
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    
    class Meta:
        verbose_name = 'Historia Clínica'
        verbose_name_plural = 'Historias Clínicas'
        ordering = ['-date', '-created_at']
        indexes = [
            models.Index(fields=['organization', 'patient', '-date']),
            models.Index(fields=['organization', '-date']),
        ]
    
    def __str__(self):
        return f"Historia Clínica - {self.patient.full_name} - {self.date}"
    
    @property
    def age_at_exam(self):
        """Edad del paciente al momento del examen"""
        if self.patient.date_of_birth:
            return (self.date - self.patient.date_of_birth).days // 365
        return None


class ClinicalHistoryAttachment(TenantModel):
    """Archivos adjuntos a la historia clínica"""
    
    clinical_history = models.ForeignKey(
        ClinicalHistory,
        on_delete=models.CASCADE,
        related_name='attachments',
        verbose_name='Historia Clínica'
    )
    
    file = models.FileField(
        upload_to='clinical_histories/%Y/%m/',
        verbose_name='Archivo'
    )
    
    file_type = models.CharField(
        max_length=50,
        choices=[
            ('retinography', 'Retinografía'),
            ('oct', 'OCT (Tomografía)'),
            ('topography', 'Topografía Corneal'),
            ('visual_field', 'Campo Visual'),
            ('prescription', 'Fórmula/Prescripción'),
            ('lab_result', 'Resultado de Laboratorio'),
            ('other', 'Otro')
        ],
        verbose_name='Tipo de Archivo'
    )
    
    description = models.CharField(max_length=200, verbose_name='Descripción', blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    
    class Meta:
        verbose_name = 'Archivo Adjunto'
        verbose_name_plural = 'Archivos Adjuntos'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_file_type_display()} - {self.clinical_history.patient.full_name}"
