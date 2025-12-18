"""
Modelos para Exámenes Especiales Oftalmológicos
Sistema completo de órdenes y resultados de exámenes
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from apps.organizations.base_models import TenantModel


class ExamOrder(TenantModel):
    """
    Orden Médica para Exámenes Especiales
    Se imprime para que el paciente realice el examen
    """
    
    EXAM_TYPES = [
        ('tonometry', 'Tonometría (Presión Intraocular)'),
        ('visual_field', 'Campo Visual / Campimetría'),
        ('retinography', 'Retinografía / Fondo de Ojo'),
        ('oct', 'OCT (Tomografía Coherencia Óptica)'),
        ('corneal_topography', 'Topografía Corneal'),
        ('pachymetry', 'Paquimetría'),
        ('keratometry', 'Queratometría'),
        ('color_vision', 'Test de Visión de Colores'),
        ('contrast_sensitivity', 'Test de Sensibilidad al Contraste'),
        ('motility', 'Estudio de Motilidad Ocular'),
        ('pupillometry', 'Pupilometría'),
        ('biometry', 'Biometría Ocular'),
        ('gonioscopy', 'Gonioscopia'),
        ('fluorescein_angiography', 'Angiografía Fluoresceínica'),
        ('other', 'Otro Examen'),
    ]
    
    PRIORITY_CHOICES = [
        ('routine', 'Rutina'),
        ('urgent', 'Urgente'),
        ('stat', 'STAT (Inmediato)'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pendiente'),
        ('scheduled', 'Agendado'),
        ('in_progress', 'En Proceso'),
        ('completed', 'Completado'),
        ('cancelled', 'Cancelado'),
    ]
    
    # Relación con Historia Clínica
    clinical_history = models.ForeignKey(
        'patients.ClinicalHistory',
        on_delete=models.CASCADE,
        related_name='exam_orders',
        verbose_name='Historia Clínica'
    )
    
    # Datos de la Orden
    exam_type = models.CharField(
        max_length=50,
        choices=EXAM_TYPES,
        verbose_name='Tipo de Examen'
    )
    
    order_date = models.DateField(
        verbose_name='Fecha de Orden'
    )
    
    ordered_by = models.ForeignKey(
        'patients.Doctor',
        on_delete=models.SET_NULL,
        null=True,
        related_name='exam_orders',
        verbose_name='Ordenado por'
    )
    
    priority = models.CharField(
        max_length=20,
        choices=PRIORITY_CHOICES,
        default='routine',
        verbose_name='Prioridad'
    )
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name='Estado'
    )
    
    # Indicaciones y Motivo
    clinical_indication = models.TextField(
        verbose_name='Indicación Clínica',
        help_text='Motivo por el cual se solicita el examen'
    )
    
    special_instructions = models.TextField(
        verbose_name='Instrucciones Especiales',
        blank=True,
        help_text='Indicaciones especiales para el técnico o paciente'
    )
    
    # Datos de Ejecución
    scheduled_date = models.DateField(
        verbose_name='Fecha Agendada',
        null=True,
        blank=True
    )
    
    performed_date = models.DateField(
        verbose_name='Fecha Realizada',
        null=True,
        blank=True
    )
    
    performed_by = models.ForeignKey(
        'patients.Doctor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='performed_exams',
        verbose_name='Realizado por'
    )
    
    # Observaciones
    observations = models.TextField(
        verbose_name='Observaciones',
        blank=True
    )
    
    cancellation_reason = models.TextField(
        verbose_name='Motivo de Cancelación',
        blank=True
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Orden de Examen'
        verbose_name_plural = 'Órdenes de Exámenes'
        ordering = ['-order_date', '-created_at']
        indexes = [
            models.Index(fields=['organization', 'clinical_history', '-order_date']),
            models.Index(fields=['organization', 'status', '-order_date']),
        ]
    
    def __str__(self):
        patient_name = self.clinical_history.patient.full_name
        return f"Orden {self.get_exam_type_display()} - {patient_name} - {self.order_date}"
    
    def mark_completed(self):
        """Marca la orden como completada"""
        self.status = 'completed'
        if not self.performed_date:
            from django.utils import timezone
            self.performed_date = timezone.now().date()
        self.save()


class SpecialExam(TenantModel):
    """
    Modelo base abstracto para todos los exámenes especiales
    """
    
    # Relación con Historia Clínica y Orden
    clinical_history = models.ForeignKey(
        'patients.ClinicalHistory',
        on_delete=models.CASCADE,
        verbose_name='Historia Clínica'
    )
    
    exam_order = models.OneToOneField(
        ExamOrder,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Orden Asociada',
        help_text='Orden médica que generó este examen'
    )
    
    # Datos del Examen
    exam_date = models.DateField(
        verbose_name='Fecha del Examen'
    )
    
    performed_by = models.ForeignKey(
        'patients.Doctor',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name='Realizado por'
    )
    
    equipment_used = models.CharField(
        max_length=200,
        verbose_name='Equipo Utilizado',
        blank=True,
        help_text='Marca y modelo del equipo'
    )
    
    # Resultados Generales
    findings = models.TextField(
        verbose_name='Hallazgos',
        blank=True,
        help_text='Descripción de hallazgos del examen'
    )
    
    interpretation = models.TextField(
        verbose_name='Interpretación',
        blank=True,
        help_text='Interpretación clínica de los resultados'
    )
    
    recommendations = models.TextField(
        verbose_name='Recomendaciones',
        blank=True,
        help_text='Recomendaciones basadas en los resultados'
    )
    
    requires_follow_up = models.BooleanField(
        default=False,
        verbose_name='Requiere Seguimiento'
    )
    
    follow_up_period = models.CharField(
        max_length=100,
        verbose_name='Período de Seguimiento',
        blank=True,
        help_text='Ej: 3 meses, 6 meses, 1 año'
    )
    
    # Archivos adjuntos (imágenes, PDFs, reportes)
    attachment = models.FileField(
        upload_to='clinical_exams/%Y/%m/',
        verbose_name='Archivo Adjunto',
        blank=True,
        null=True,
        help_text='Imagen o reporte del examen'
    )
    
    notes = models.TextField(
        verbose_name='Notas Adicionales',
        blank=True
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        abstract = True


class Tonometry(SpecialExam):
    """
    Tonometría - Medición de Presión Intraocular (PIO)
    """
    
    METHODS = [
        ('goldman', 'Goldman (Aplanación)'),
        ('air_puff', 'Aire (No Contacto)'),
        ('icare', 'iCare (Rebote)'),
        ('pascal', 'Pascal (Contorno Dinámico)'),
        ('schiotz', 'Schiötz (Indentación)'),
        ('tonopen', 'Tonopen'),
    ]
    
    method = models.CharField(
        max_length=20,
        choices=METHODS,
        verbose_name='Método de Medición'
    )
    
    time_measured = models.TimeField(
        verbose_name='Hora de Medición',
        help_text='Importante: la PIO varía durante el día'
    )
    
    # Ojo Derecho
    od_pressure = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        verbose_name='PIO OD (mmHg)',
        validators=[MinValueValidator(0), MaxValueValidator(80)],
        help_text='Presión intraocular ojo derecho'
    )
    
    od_notes = models.CharField(
        max_length=200,
        verbose_name='Notas OD',
        blank=True
    )
    
    # Ojo Izquierdo
    os_pressure = models.DecimalField(
        max_digits=4,
        decimal_places=1,
        verbose_name='PIO OS (mmHg)',
        validators=[MinValueValidator(0), MaxValueValidator(80)],
        help_text='Presión intraocular ojo izquierdo'
    )
    
    os_notes = models.CharField(
        max_length=200,
        verbose_name='Notas OS',
        blank=True
    )
    
    # Datos adicionales
    pachymetry_corrected = models.BooleanField(
        default=False,
        verbose_name='Corregido por Paquimetría',
        help_text='Si se aplicó corrección por grosor corneal'
    )
    
    class Meta:
        verbose_name = 'Tonometría'
        verbose_name_plural = 'Tonometrías'
        ordering = ['-exam_date']
    
    def __str__(self):
        return f"Tonometría - {self.clinical_history.patient.full_name} - {self.exam_date}"
    
    @property
    def is_abnormal(self):
        """Detecta si hay presiones anormales (>21 mmHg)"""
        return self.od_pressure > 21 or self.os_pressure > 21


class VisualFieldTest(SpecialExam):
    """
    Campo Visual / Campimetría
    """
    
    TEST_TYPES = [
        ('confrontation', 'Confrontación Manual'),
        ('goldman', 'Perímetro de Goldman'),
        ('humphrey', 'Humphrey (Computarizado)'),
        ('octopus', 'Octopus'),
        ('automated', 'Automatizado Genérico'),
    ]
    
    STRATEGIES = [
        ('24-2', 'SITA Standard 24-2'),
        ('30-2', 'SITA Standard 30-2'),
        ('10-2', 'SITA Standard 10-2'),
        ('fast', 'SITA Fast'),
        ('full_threshold', 'Full Threshold'),
    ]
    
    RESULTS = [
        ('normal', 'Normal'),
        ('borderline', 'Limítrofe'),
        ('mild_defect', 'Defecto Leve'),
        ('moderate_defect', 'Defecto Moderado'),
        ('severe_defect', 'Defecto Severo'),
    ]
    
    test_type = models.CharField(
        max_length=30,
        choices=TEST_TYPES,
        verbose_name='Tipo de Test'
    )
    
    strategy = models.CharField(
        max_length=30,
        choices=STRATEGIES,
        verbose_name='Estrategia',
        blank=True
    )
    
    # Resultados OD
    od_result = models.CharField(
        max_length=30,
        choices=RESULTS,
        verbose_name='Resultado OD'
    )
    
    od_mean_deviation = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='MD OD (dB)',
        null=True,
        blank=True,
        help_text='Mean Deviation'
    )
    
    od_pattern_std_deviation = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='PSD OD (dB)',
        null=True,
        blank=True,
        help_text='Pattern Standard Deviation'
    )
    
    od_visual_field_index = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='VFI OD (%)',
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text='Visual Field Index'
    )
    
    # Resultados OS
    os_result = models.CharField(
        max_length=30,
        choices=RESULTS,
        verbose_name='Resultado OS'
    )
    
    os_mean_deviation = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='MD OS (dB)',
        null=True,
        blank=True
    )
    
    os_pattern_std_deviation = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='PSD OS (dB)',
        null=True,
        blank=True
    )
    
    os_visual_field_index = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='VFI OS (%)',
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Calidad del examen
    reliability_fixation_losses = models.CharField(
        max_length=50,
        verbose_name='Pérdidas de Fijación',
        blank=True
    )
    
    reliability_false_positives = models.CharField(
        max_length=50,
        verbose_name='Falsos Positivos',
        blank=True
    )
    
    reliability_false_negatives = models.CharField(
        max_length=50,
        verbose_name='Falsos Negativos',
        blank=True
    )
    
    class Meta:
        verbose_name = 'Campo Visual'
        verbose_name_plural = 'Campos Visuales'
        ordering = ['-exam_date']
    
    def __str__(self):
        return f"Campo Visual - {self.clinical_history.patient.full_name} - {self.exam_date}"


class Retinography(SpecialExam):
    """
    Retinografía / Fotografía de Fondo de Ojo
    """
    
    VIEWS = [
        ('posterior_pole', 'Polo Posterior'),
        ('macula', 'Mácula'),
        ('optic_disc', 'Disco Óptico'),
        ('peripheral', 'Periférica'),
        ('widefield', 'Campo Amplio'),
    ]
    
    FINDINGS_CHOICES = [
        ('normal', 'Normal'),
        ('drusen', 'Drusas'),
        ('hemorrhages', 'Hemorragias'),
        ('exudates', 'Exudados'),
        ('microaneurysms', 'Microaneurismas'),
        ('cotton_wool', 'Exudados Algodonosos'),
        ('neovascularization', 'Neovascularización'),
        ('disc_edema', 'Edema de Disco'),
        ('cup_disc_abnormal', 'Relación C/D Anormal'),
        ('other', 'Otros Hallazgos'),
    ]
    
    # Configuración del examen
    dilated_pupil = models.BooleanField(
        default=True,
        verbose_name='Pupila Dilatada',
        help_text='Se realizó con midriasis'
    )
    
    dilation_drug = models.CharField(
        max_length=100,
        verbose_name='Medicamento para Dilatación',
        blank=True,
        help_text='Ej: Tropicamida 1%'
    )
    
    # OD
    od_view = models.CharField(
        max_length=30,
        choices=VIEWS,
        verbose_name='Vista OD'
    )
    
    od_findings = models.CharField(
        max_length=50,
        choices=FINDINGS_CHOICES,
        verbose_name='Hallazgos OD'
    )
    
    od_cup_disc_ratio = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        verbose_name='Relación C/D OD',
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)],
        help_text='Relación copa/disco óptico'
    )
    
    od_description = models.TextField(
        verbose_name='Descripción OD',
        blank=True
    )
    
    od_image = models.FileField(
        upload_to='retinography/%Y/%m/',
        verbose_name='Imagen OD',
        blank=True,
        null=True
    )
    
    # OS
    os_view = models.CharField(
        max_length=30,
        choices=VIEWS,
        verbose_name='Vista OS'
    )
    
    os_findings = models.CharField(
        max_length=50,
        choices=FINDINGS_CHOICES,
        verbose_name='Hallazgos OS'
    )
    
    os_cup_disc_ratio = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        verbose_name='Relación C/D OS',
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(1)]
    )
    
    os_description = models.TextField(
        verbose_name='Descripción OS',
        blank=True
    )
    
    os_image = models.FileField(
        upload_to='retinography/%Y/%m/',
        verbose_name='Imagen OS',
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = 'Retinografía'
        verbose_name_plural = 'Retinografías'
        ordering = ['-exam_date']
    
    def __str__(self):
        return f"Retinografía - {self.clinical_history.patient.full_name} - {self.exam_date}"


class OCTExam(SpecialExam):
    """
    OCT - Tomografía de Coherencia Óptica
    """
    
    SCAN_AREAS = [
        ('macula', 'Mácula'),
        ('optic_nerve', 'Nervio Óptico / RNFL'),
        ('anterior_segment', 'Segmento Anterior'),
        ('choroid', 'Coroides'),
    ]
    
    SCAN_PATTERNS = [
        ('macular_cube', 'Cubo Macular'),
        ('optic_disc_cube', 'Cubo Disco Óptico'),
        ('rnfl_circle', 'Círculo RNFL'),
        ('line_scan', 'Línea'),
        ('radial', 'Radial'),
    ]
    
    scan_area = models.CharField(
        max_length=30,
        choices=SCAN_AREAS,
        verbose_name='Área Escaneada'
    )
    
    scan_pattern = models.CharField(
        max_length=30,
        choices=SCAN_PATTERNS,
        verbose_name='Patrón de Escaneo'
    )
    
    # Grosor Retiniano (Mácula)
    od_central_thickness = models.IntegerField(
        verbose_name='Grosor Central OD (μm)',
        null=True,
        blank=True,
        help_text='Grosor foveal central'
    )
    
    os_central_thickness = models.IntegerField(
        verbose_name='Grosor Central OS (μm)',
        null=True,
        blank=True
    )
    
    # RNFL (Capa de Fibras Nerviosas)
    od_rnfl_average = models.IntegerField(
        verbose_name='RNFL Promedio OD (μm)',
        null=True,
        blank=True
    )
    
    od_rnfl_superior = models.IntegerField(
        verbose_name='RNFL Superior OD (μm)',
        null=True,
        blank=True
    )
    
    od_rnfl_inferior = models.IntegerField(
        verbose_name='RNFL Inferior OD (μm)',
        null=True,
        blank=True
    )
    
    od_rnfl_nasal = models.IntegerField(
        verbose_name='RNFL Nasal OD (μm)',
        null=True,
        blank=True
    )
    
    od_rnfl_temporal = models.IntegerField(
        verbose_name='RNFL Temporal OD (μm)',
        null=True,
        blank=True
    )
    
    os_rnfl_average = models.IntegerField(
        verbose_name='RNFL Promedio OS (μm)',
        null=True,
        blank=True
    )
    
    os_rnfl_superior = models.IntegerField(
        verbose_name='RNFL Superior OS (μm)',
        null=True,
        blank=True
    )
    
    os_rnfl_inferior = models.IntegerField(
        verbose_name='RNFL Inferior OS (μm)',
        null=True,
        blank=True
    )
    
    os_rnfl_nasal = models.IntegerField(
        verbose_name='RNFL Nasal OS (μm)',
        null=True,
        blank=True
    )
    
    os_rnfl_temporal = models.IntegerField(
        verbose_name='RNFL Temporal OS (μm)',
        null=True,
        blank=True
    )
    
    # Calidad del escaneo
    od_signal_strength = models.IntegerField(
        verbose_name='Fuerza de Señal OD',
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    
    os_signal_strength = models.IntegerField(
        verbose_name='Fuerza de Señal OS',
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(10)]
    )
    
    # Imágenes
    od_report = models.FileField(
        upload_to='oct/%Y/%m/',
        verbose_name='Reporte OD',
        blank=True,
        null=True
    )
    
    os_report = models.FileField(
        upload_to='oct/%Y/%m/',
        verbose_name='Reporte OS',
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = 'OCT'
        verbose_name_plural = 'OCTs'
        ordering = ['-exam_date']
    
    def __str__(self):
        return f"OCT - {self.clinical_history.patient.full_name} - {self.exam_date}"


class CornealTopography(SpecialExam):
    """
    Topografía Corneal
    """
    
    TOPOGRAPHY_TYPES = [
        ('placido', 'Placido (Disco)'),
        ('scheimpflug', 'Scheimpflug'),
        ('elevation', 'Elevación'),
        ('combined', 'Combinada'),
    ]
    
    PURPOSE_CHOICES = [
        ('contact_lens', 'Adaptación Lentes de Contacto'),
        ('refractive_surgery', 'Evaluación Cirugía Refractiva'),
        ('keratoconus', 'Sospecha Queratocono'),
        ('post_surgical', 'Post-quirúrgico'),
        ('routine', 'Control Rutinario'),
    ]
    
    topography_type = models.CharField(
        max_length=30,
        choices=TOPOGRAPHY_TYPES,
        verbose_name='Tipo de Topografía'
    )
    
    purpose = models.CharField(
        max_length=30,
        choices=PURPOSE_CHOICES,
        verbose_name='Propósito del Estudio'
    )
    
    # OD - Queratometría
    od_k1 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='K1 OD (D)',
        null=True,
        blank=True,
        help_text='Curvatura más plana'
    )
    
    od_k1_axis = models.IntegerField(
        verbose_name='Eje K1 OD (°)',
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(180)]
    )
    
    od_k2 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='K2 OD (D)',
        null=True,
        blank=True,
        help_text='Curvatura más curva'
    )
    
    od_k2_axis = models.IntegerField(
        verbose_name='Eje K2 OD (°)',
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(180)]
    )
    
    od_avg_k = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='K Promedio OD (D)',
        null=True,
        blank=True
    )
    
    od_corneal_astigmatism = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Astigmatismo Corneal OD (D)',
        null=True,
        blank=True
    )
    
    # OS - Queratometría
    os_k1 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='K1 OS (D)',
        null=True,
        blank=True
    )
    
    os_k1_axis = models.IntegerField(
        verbose_name='Eje K1 OS (°)',
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(180)]
    )
    
    os_k2 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='K2 OS (D)',
        null=True,
        blank=True
    )
    
    os_k2_axis = models.IntegerField(
        verbose_name='Eje K2 OS (°)',
        null=True,
        blank=True,
        validators=[MinValueValidator(0), MaxValueValidator(180)]
    )
    
    os_avg_k = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='K Promedio OS (D)',
        null=True,
        blank=True
    )
    
    os_corneal_astigmatism = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='Astigmatismo Corneal OS (D)',
        null=True,
        blank=True
    )
    
    # Sospecha de Queratocono
    od_keratoconus_suspect = models.BooleanField(
        default=False,
        verbose_name='Sospecha Queratocono OD'
    )
    
    os_keratoconus_suspect = models.BooleanField(
        default=False,
        verbose_name='Sospecha Queratocono OS'
    )
    
    # Imágenes
    od_map = models.FileField(
        upload_to='topography/%Y/%m/',
        verbose_name='Mapa OD',
        blank=True,
        null=True
    )
    
    os_map = models.FileField(
        upload_to='topography/%Y/%m/',
        verbose_name='Mapa OS',
        blank=True,
        null=True
    )
    
    class Meta:
        verbose_name = 'Topografía Corneal'
        verbose_name_plural = 'Topografías Corneales'
        ordering = ['-exam_date']
    
    def __str__(self):
        return f"Topografía - {self.clinical_history.patient.full_name} - {self.exam_date}"


class Pachymetry(SpecialExam):
    """
    Paquimetría - Medición de Grosor Corneal
    """
    
    METHOD_CHOICES = [
        ('ultrasound', 'Ultrasonido'),
        ('optical', 'Óptica (OCT/Scheimpflug)'),
    ]
    
    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        verbose_name='Método de Medición'
    )
    
    # Grosor Central
    od_central_thickness = models.IntegerField(
        verbose_name='Grosor Central OD (μm)',
        help_text='Grosor corneal central'
    )
    
    os_central_thickness = models.IntegerField(
        verbose_name='Grosor Central OS (μm)'
    )
    
    # Grosores Periféricos (opcional)
    od_superior = models.IntegerField(
        verbose_name='Superior OD (μm)',
        null=True,
        blank=True
    )
    
    od_inferior = models.IntegerField(
        verbose_name='Inferior OD (μm)',
        null=True,
        blank=True
    )
    
    od_nasal = models.IntegerField(
        verbose_name='Nasal OD (μm)',
        null=True,
        blank=True
    )
    
    od_temporal = models.IntegerField(
        verbose_name='Temporal OD (μm)',
        null=True,
        blank=True
    )
    
    os_superior = models.IntegerField(
        verbose_name='Superior OS (μm)',
        null=True,
        blank=True
    )
    
    os_inferior = models.IntegerField(
        verbose_name='Inferior OS (μm)',
        null=True,
        blank=True
    )
    
    os_nasal = models.IntegerField(
        verbose_name='Nasal OS (μm)',
        null=True,
        blank=True
    )
    
    os_temporal = models.IntegerField(
        verbose_name='Temporal OS (μm)',
        null=True,
        blank=True
    )
    
    class Meta:
        verbose_name = 'Paquimetría'
        verbose_name_plural = 'Paquimetrías'
        ordering = ['-exam_date']
    
    def __str__(self):
        return f"Paquimetría - {self.clinical_history.patient.full_name} - {self.exam_date}"
    
    @property
    def od_is_thin(self):
        """Detecta si la córnea es delgada (<500 μm)"""
        return self.od_central_thickness < 500
    
    @property
    def os_is_thin(self):
        """Detecta si la córnea es delgada (<500 μm)"""
        return self.os_central_thickness < 500


class Keratometry(SpecialExam):
    """
    Queratometría - Medición de Curvatura Corneal
    """
    
    METHOD_CHOICES = [
        ('manual', 'Manual'),
        ('automated', 'Automatizada'),
        ('topography', 'Por Topografía'),
    ]
    
    method = models.CharField(
        max_length=20,
        choices=METHOD_CHOICES,
        verbose_name='Método'
    )
    
    # OD
    od_k1 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='K1 OD (D)',
        help_text='Meridiano más plano'
    )
    
    od_k1_axis = models.IntegerField(
        verbose_name='Eje K1 OD (°)',
        validators=[MinValueValidator(0), MaxValueValidator(180)]
    )
    
    od_k2 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='K2 OD (D)',
        help_text='Meridiano más curvo'
    )
    
    od_k2_axis = models.IntegerField(
        verbose_name='Eje K2 OD (°)',
        validators=[MinValueValidator(0), MaxValueValidator(180)]
    )
    
    # OS
    os_k1 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='K1 OS (D)'
    )
    
    os_k1_axis = models.IntegerField(
        verbose_name='Eje K1 OS (°)',
        validators=[MinValueValidator(0), MaxValueValidator(180)]
    )
    
    os_k2 = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        verbose_name='K2 OS (D)'
    )
    
    os_k2_axis = models.IntegerField(
        verbose_name='Eje K2 OS (°)',
        validators=[MinValueValidator(0), MaxValueValidator(180)]
    )
    
    class Meta:
        verbose_name = 'Queratometría'
        verbose_name_plural = 'Queratometrías'
        ordering = ['-exam_date']
    
    def __str__(self):
        return f"Queratometría - {self.clinical_history.patient.full_name} - {self.exam_date}"
    
    @property
    def od_cylinder(self):
        """Calcula el cilindro corneal OD"""
        return abs(self.od_k2 - self.od_k1)
    
    @property
    def os_cylinder(self):
        """Calcula el cilindro corneal OS"""
        return abs(self.os_k2 - self.os_k1)


class ColorVisionTest(SpecialExam):
    """
    Test de Visión de Colores
    """
    
    TEST_TYPES = [
        ('ishihara', 'Ishihara (Placas)'),
        ('farnsworth_d15', 'Farnsworth D-15'),
        ('farnsworth_munsell', 'Farnsworth-Munsell 100'),
        ('hrd', 'HRR (Hardy-Rand-Ritter)'),
    ]
    
    RESULTS = [
        ('normal', 'Normal (Tricromático)'),
        ('protanomaly', 'Protanomalía (Débil rojo)'),
        ('protanopia', 'Protanopia (Ciego rojo)'),
        ('deuteranomaly', 'Deuteranomalía (Débil verde)'),
        ('deuteranopia', 'Deuteranopia (Ciego verde)'),
        ('tritanomaly', 'Tritanomalía (Débil azul)'),
        ('tritanopia', 'Tritanopia (Ciego azul)'),
        ('achromatopsia', 'Acromatopsia'),
    ]
    
    test_type = models.CharField(
        max_length=30,
        choices=TEST_TYPES,
        verbose_name='Tipo de Test'
    )
    
    od_result = models.CharField(
        max_length=30,
        choices=RESULTS,
        verbose_name='Resultado OD'
    )
    
    od_score = models.CharField(
        max_length=50,
        verbose_name='Puntuación OD',
        blank=True,
        help_text='Ej: 15/17 placas correctas'
    )
    
    os_result = models.CharField(
        max_length=30,
        choices=RESULTS,
        verbose_name='Resultado OS'
    )
    
    os_score = models.CharField(
        max_length=50,
        verbose_name='Puntuación OS',
        blank=True
    )
    
    class Meta:
        verbose_name = 'Test de Visión de Colores'
        verbose_name_plural = 'Tests de Visión de Colores'
        ordering = ['-exam_date']
    
    def __str__(self):
        return f"Visión Colores - {self.clinical_history.patient.full_name} - {self.exam_date}"


class MotilityExam(SpecialExam):
    """
    Examen de Motilidad Ocular
    """
    
    COVER_TEST_RESULTS = [
        ('ortophoria', 'Ortoforía (Normal)'),
        ('esophoria', 'Esoforía'),
        ('exophoria', 'Exoforía'),
        ('hyperphoria', 'Hiperforía'),
        ('esotropia', 'Esotropía'),
        ('exotropia', 'Exotropía'),
        ('hypertropia', 'Hipertropía'),
    ]
    
    # Cover Test
    cover_test_distance = models.CharField(
        max_length=30,
        choices=COVER_TEST_RESULTS,
        verbose_name='Cover Test Lejos',
        blank=True
    )
    
    cover_test_near = models.CharField(
        max_length=30,
        choices=COVER_TEST_RESULTS,
        verbose_name='Cover Test Cerca',
        blank=True
    )
    
    # Medición con prismas
    deviation_horizontal = models.CharField(
        max_length=50,
        verbose_name='Desviación Horizontal',
        blank=True,
        help_text='Ej: 10Δ eso, 15Δ exo'
    )
    
    deviation_vertical = models.CharField(
        max_length=50,
        verbose_name='Desviación Vertical',
        blank=True,
        help_text='Ej: 5Δ RHT, 3Δ LHT'
    )
    
    # Versiones (movimientos binoculares)
    versions_normal = models.BooleanField(
        default=True,
        verbose_name='Versiones Normales'
    )
    
    versions_notes = models.TextField(
        verbose_name='Notas Versiones',
        blank=True,
        help_text='Restricciones en alguna posición'
    )
    
    # Ducciones (movimientos monoculares)
    ductions_od_normal = models.BooleanField(
        default=True,
        verbose_name='Ducciones OD Normales'
    )
    
    ductions_os_normal = models.BooleanField(
        default=True,
        verbose_name='Ducciones OS Normales'
    )
    
    ductions_notes = models.TextField(
        verbose_name='Notas Ducciones',
        blank=True
    )
    
    # Convergencia
    near_point_convergence = models.CharField(
        max_length=50,
        verbose_name='Punto Próximo de Convergencia',
        blank=True,
        help_text='Ej: 8 cm, 10 cm'
    )
    
    convergence_recovery = models.CharField(
        max_length=50,
        verbose_name='Recuperación de Convergencia',
        blank=True
    )
    
    class Meta:
        verbose_name = 'Examen de Motilidad'
        verbose_name_plural = 'Exámenes de Motilidad'
        ordering = ['-exam_date']
    
    def __str__(self):
        return f"Motilidad - {self.clinical_history.patient.full_name} - {self.exam_date}"
