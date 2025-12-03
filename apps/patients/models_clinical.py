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
    doctor = models.ForeignKey(
        'patients.Doctor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='clinical_histories',
        verbose_name='Médico/Optómetra'
    )
    
    # ==================== ANAMNESIS ====================
    chief_complaint = models.TextField(verbose_name='Motivo de Consulta', blank=True)
    current_illness = models.TextField(verbose_name='Enfermedad Actual', blank=True)
    
    # Síntomas
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
    
    # Antecedentes Familiares
    family_glaucoma = models.BooleanField(default=False, verbose_name='Glaucoma (Familiar)')
    family_cataracts = models.BooleanField(default=False, verbose_name='Cataratas (Familiar)')
    family_macular_degeneration = models.BooleanField(default=False, verbose_name='Degeneración Macular (Familiar)')
    family_diabetes = models.BooleanField(default=False, verbose_name='Diabetes (Familiar)')
    family_hypertension = models.BooleanField(default=False, verbose_name='Hipertensión (Familiar)')
    family_history_notes = models.TextField(verbose_name='Notas Antecedentes Familiares', blank=True)
    
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
    
    # Ojo Derecho (OD) - Sin Corrección
    va_od_sc_distance = models.CharField(max_length=20, verbose_name='AV OD SC Lejos', blank=True, help_text='Ej: 20/20, 20/40')
    va_od_sc_near = models.CharField(max_length=20, verbose_name='AV OD SC Cerca', blank=True)
    
    # Ojo Derecho (OD) - Con Corrección
    va_od_cc_distance = models.CharField(max_length=20, verbose_name='AV OD CC Lejos', blank=True)
    va_od_cc_near = models.CharField(max_length=20, verbose_name='AV OD CC Cerca', blank=True)
    
    # Ojo Izquierdo (OS) - Sin Corrección
    va_os_sc_distance = models.CharField(max_length=20, verbose_name='AV OS SC Lejos', blank=True)
    va_os_sc_near = models.CharField(max_length=20, verbose_name='AV OS SC Cerca', blank=True)
    
    # Ojo Izquierdo (OS) - Con Corrección
    va_os_cc_distance = models.CharField(max_length=20, verbose_name='AV OS CC Lejos', blank=True)
    va_os_cc_near = models.CharField(max_length=20, verbose_name='AV OS CC Cerca', blank=True)
    
    # Ambos Ojos (OU)
    va_ou_distance = models.CharField(max_length=20, verbose_name='AV OU Lejos', blank=True)
    va_ou_near = models.CharField(max_length=20, verbose_name='AV OU Cerca', blank=True)
    
    # ==================== REFRACCIÓN ====================
    
    # Ojo Derecho (OD)
    refraction_od_sphere = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='OD Esfera', null=True, blank=True)
    refraction_od_cylinder = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='OD Cilindro', null=True, blank=True)
    refraction_od_axis = models.IntegerField(verbose_name='OD Eje', null=True, blank=True, help_text='0-180°')
    refraction_od_add = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='OD Adición', null=True, blank=True)
    refraction_od_prism = models.CharField(max_length=20, verbose_name='OD Prisma', blank=True)
    
    # Ojo Izquierdo (OS)
    refraction_os_sphere = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='OS Esfera', null=True, blank=True)
    refraction_os_cylinder = models.DecimalField(max_digits=5, decimal_places=2, verbose_name='OS Cilindro', null=True, blank=True)
    refraction_os_axis = models.IntegerField(verbose_name='OS Eje', null=True, blank=True, help_text='0-180°')
    refraction_os_add = models.DecimalField(max_digits=4, decimal_places=2, verbose_name='OS Adición', null=True, blank=True)
    refraction_os_prism = models.CharField(max_length=20, verbose_name='OS Prisma', blank=True)
    
    # Distancia Pupilar
    pd_distance = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='DP Lejos (mm)', null=True, blank=True)
    pd_near = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='DP Cerca (mm)', null=True, blank=True)
    pd_od = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='DP OD', null=True, blank=True)
    pd_os = models.DecimalField(max_digits=4, decimal_places=1, verbose_name='DP OS', null=True, blank=True)
    
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
    
    # ==================== BIOMICROSCOPÍA ====================
    
    # Segmento Anterior OD
    biomicroscopy_od_lids = models.TextField(verbose_name='OD Párpados', blank=True)
    biomicroscopy_od_conjunctiva = models.TextField(verbose_name='OD Conjuntiva', blank=True)
    biomicroscopy_od_cornea = models.TextField(verbose_name='OD Córnea', blank=True)
    biomicroscopy_od_anterior_chamber = models.TextField(verbose_name='OD Cámara Anterior', blank=True)
    biomicroscopy_od_iris = models.TextField(verbose_name='OD Iris', blank=True)
    biomicroscopy_od_lens = models.TextField(verbose_name='OD Cristalino', blank=True)
    
    # Segmento Anterior OS
    biomicroscopy_os_lids = models.TextField(verbose_name='OS Párpados', blank=True)
    biomicroscopy_os_conjunctiva = models.TextField(verbose_name='OS Conjuntiva', blank=True)
    biomicroscopy_os_cornea = models.TextField(verbose_name='OS Córnea', blank=True)
    biomicroscopy_os_anterior_chamber = models.TextField(verbose_name='OS Cámara Anterior', blank=True)
    biomicroscopy_os_iris = models.TextField(verbose_name='OS Iris', blank=True)
    biomicroscopy_os_lens = models.TextField(verbose_name='OS Cristalino', blank=True)
    
    # ==================== FONDO DE OJO ====================
    
    # Ojo Derecho
    fundoscopy_od_vitreous = models.TextField(verbose_name='OD Vítreo', blank=True)
    fundoscopy_od_optic_disc = models.TextField(verbose_name='OD Disco Óptico', blank=True)
    fundoscopy_od_macula = models.TextField(verbose_name='OD Mácula', blank=True)
    fundoscopy_od_vessels = models.TextField(verbose_name='OD Vasos', blank=True)
    fundoscopy_od_periphery = models.TextField(verbose_name='OD Periferia', blank=True)
    
    # Ojo Izquierdo
    fundoscopy_os_vitreous = models.TextField(verbose_name='OS Vítreo', blank=True)
    fundoscopy_os_optic_disc = models.TextField(verbose_name='OS Disco Óptico', blank=True)
    fundoscopy_os_macula = models.TextField(verbose_name='OS Mácula', blank=True)
    fundoscopy_os_vessels = models.TextField(verbose_name='OS Vasos', blank=True)
    fundoscopy_os_periphery = models.TextField(verbose_name='OS Periferia', blank=True)
    
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
    
    # ==================== DIAGNÓSTICO Y TRATAMIENTO ====================
    
    diagnosis = models.TextField(verbose_name='Diagnóstico', blank=True)
    
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
    
    # Plan de Tratamiento
    treatment_plan = models.TextField(verbose_name='Plan de Tratamiento', blank=True)
    prescription_glasses = models.BooleanField(default=False, verbose_name='Prescripción de Lentes')
    prescription_contact_lenses = models.BooleanField(default=False, verbose_name='Prescripción de LC')
    prescription_medication = models.BooleanField(default=False, verbose_name='Prescripción de Medicamentos')
    medication_details = models.TextField(verbose_name='Detalles de Medicación', blank=True)
    
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
    
    # ==================== SEGUIMIENTO ====================
    
    follow_up_date = models.DateField(verbose_name='Fecha de Seguimiento', null=True, blank=True)
    follow_up_notes = models.TextField(verbose_name='Notas de Seguimiento', blank=True)
    
    # ==================== OBSERVACIONES ====================
    
    observations = models.TextField(verbose_name='Observaciones Generales', blank=True)
    recommendations = models.TextField(verbose_name='Recomendaciones', blank=True)
    
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
