"""
Modelos de Configuración de Parámetros Clínicos
Permite personalizar opciones de tratamientos, prescripciones y diagnósticos
"""
from django.db import models
from apps.organizations.base_models import TenantModel


class ClinicalParameter(TenantModel):
    """Parámetros clínicos personalizables por organización"""
    
    PARAMETER_TYPES = [
        # Medicamentos y Tratamientos
        ('medication', 'Medicamento'),
        ('topical_medication', 'Medicamento Tópico Oftálmico'),
        ('systemic_medication', 'Medicamento Sistémico'),
        
        # Prescripciones Ópticas
        ('lens_type', 'Tipo de Lentes'),
        ('lens_material', 'Material de Lentes'),
        ('lens_coating', 'Tratamiento/Recubrimiento'),
        ('lens_brand', 'Marca de Lentes'),
        ('frame_type', 'Tipo de Montura'),
        
        # Lentes de Contacto
        ('contact_lens_type', 'Tipo de Lentes de Contacto'),
        ('contact_lens_brand', 'Marca de Lentes de Contacto'),
        ('contact_lens_material', 'Material de LC'),
        ('contact_lens_wearing', 'Régimen de Uso LC'),
        
        # Diagnósticos
        ('diagnosis', 'Diagnóstico'),
        ('diagnosis_category', 'Categoría de Diagnóstico'),
        
        # Tratamientos
        ('treatment', 'Tratamiento'),
        ('therapy', 'Terapia Coadyuvante'),
        ('visual_therapy', 'Terapia Visual'),
        
        # Exámenes
        ('complementary_exam', 'Examen Complementario'),
        ('lab_test', 'Examen de Laboratorio'),
        
        # Otros
        ('recommendation', 'Recomendación'),
        ('referral_specialty', 'Especialidad para Remisión'),
        ('follow_up_reason', 'Motivo de Seguimiento'),
    ]
    
    parameter_type = models.CharField(
        max_length=50,
        choices=PARAMETER_TYPES,
        verbose_name='Tipo de Parámetro',
        db_index=True
    )
    
    name = models.CharField(
        max_length=200,
        verbose_name='Nombre',
        help_text='Nombre del parámetro'
    )
    
    code = models.CharField(
        max_length=50,
        verbose_name='Código',
        blank=True,
        help_text='Código o abreviatura (opcional)'
    )
    
    description = models.TextField(
        verbose_name='Descripción',
        blank=True,
        help_text='Descripción detallada o instrucciones'
    )
    
    # Para medicamentos
    dosage = models.CharField(
        max_length=200,
        verbose_name='Dosis',
        blank=True,
        help_text='Dosis estándar (ej: 1 gota cada 8 horas)'
    )
    
    administration_route = models.CharField(
        max_length=50,
        choices=[
            ('topical', 'Tópico'),
            ('oral', 'Oral'),
            ('parenteral', 'Parenteral'),
            ('sublingual', 'Sublingual'),
            ('other', 'Otro')
        ],
        verbose_name='Vía de Administración',
        blank=True
    )
    
    frequency = models.CharField(
        max_length=200,
        verbose_name='Frecuencia',
        blank=True,
        help_text='Frecuencia de uso (ej: cada 8 horas, 3 veces al día)'
    )
    
    duration = models.CharField(
        max_length=100,
        verbose_name='Duración',
        blank=True,
        help_text='Duración del tratamiento (ej: 7 días, 2 semanas)'
    )
    
    # Para diagnósticos
    icd_10_code = models.CharField(
        max_length=20,
        verbose_name='Código CIE-10',
        blank=True,
        help_text='Código internacional de enfermedades'
    )
    
    category = models.CharField(
        max_length=100,
        verbose_name='Categoría',
        blank=True,
        help_text='Categoría o especialidad'
    )
    
    # Configuración
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo',
        help_text='Si está activo aparecerá en los selectores'
    )
    
    is_default = models.BooleanField(
        default=False,
        verbose_name='Predeterminado',
        help_text='Marcar como opción predeterminada'
    )
    
    display_order = models.IntegerField(
        default=0,
        verbose_name='Orden de Visualización',
        help_text='Orden en listas (menor número = primero)'
    )
    
    # Metadata
    usage_count = models.IntegerField(
        default=0,
        verbose_name='Veces Usado',
        help_text='Contador de veces que se ha usado'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_clinical_parameters',
        verbose_name='Creado por'
    )
    
    class Meta:
        verbose_name = 'Parámetro Clínico'
        verbose_name_plural = 'Parámetros Clínicos'
        ordering = ['parameter_type', 'display_order', 'name']
        unique_together = ['organization', 'parameter_type', 'name']
        indexes = [
            models.Index(fields=['organization', 'parameter_type', 'is_active']),
            models.Index(fields=['organization', 'is_active', 'display_order']),
        ]
    
    def __str__(self):
        return f"{self.get_parameter_type_display()}: {self.name}"
    
    def increment_usage(self):
        """Incrementa el contador de uso"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class MedicationTemplate(TenantModel):
    """Plantillas de medicación predefinidas"""
    
    name = models.CharField(
        max_length=200,
        verbose_name='Nombre de la Plantilla',
        help_text='Ej: Tratamiento Conjuntivitis Bacteriana'
    )
    
    description = models.TextField(
        verbose_name='Descripción',
        blank=True
    )
    
    # Condiciones de uso
    diagnosis = models.CharField(
        max_length=200,
        verbose_name='Diagnóstico Asociado',
        blank=True
    )
    
    # Plantilla de prescripción
    prescription_text = models.TextField(
        verbose_name='Texto de Prescripción',
        help_text='Texto completo de la prescripción'
    )
    
    # Medicamentos incluidos (JSON o relación)
    medications = models.ManyToManyField(
        ClinicalParameter,
        limit_choices_to={'parameter_type__in': ['medication', 'topical_medication', 'systemic_medication']},
        related_name='medication_templates',
        verbose_name='Medicamentos',
        blank=True
    )
    
    instructions = models.TextField(
        verbose_name='Instrucciones',
        blank=True,
        help_text='Instrucciones adicionales para el paciente'
    )
    
    duration_days = models.IntegerField(
        verbose_name='Duración (días)',
        null=True,
        blank=True
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    usage_count = models.IntegerField(
        default=0,
        verbose_name='Veces Usado'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_medication_templates',
        verbose_name='Creado por'
    )
    
    class Meta:
        verbose_name = 'Plantilla de Medicación'
        verbose_name_plural = 'Plantillas de Medicación'
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return self.name
    
    def increment_usage(self):
        """Incrementa el contador de uso"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class TreatmentProtocol(TenantModel):
    """Protocolos de tratamiento estandarizados"""
    
    name = models.CharField(
        max_length=200,
        verbose_name='Nombre del Protocolo'
    )
    
    protocol_type = models.CharField(
        max_length=50,
        choices=[
            ('medication', 'Farmacológico'),
            ('optical', 'Óptico'),
            ('surgical', 'Quirúrgico'),
            ('visual_therapy', 'Terapia Visual'),
            ('combined', 'Combinado'),
        ],
        verbose_name='Tipo de Protocolo'
    )
    
    diagnosis_indication = models.CharField(
        max_length=200,
        verbose_name='Indicación/Diagnóstico',
        help_text='Para qué diagnóstico está indicado'
    )
    
    description = models.TextField(
        verbose_name='Descripción',
        blank=True
    )
    
    # Fases del protocolo
    phase_1 = models.TextField(
        verbose_name='Fase 1',
        blank=True,
        help_text='Primera fase del tratamiento'
    )
    
    phase_2 = models.TextField(
        verbose_name='Fase 2',
        blank=True
    )
    
    phase_3 = models.TextField(
        verbose_name='Fase 3',
        blank=True
    )
    
    # Medicamentos y tratamientos
    medications = models.ManyToManyField(
        ClinicalParameter,
        limit_choices_to={'parameter_type__in': ['medication', 'topical_medication', 'systemic_medication', 'treatment']},
        related_name='treatment_protocols',
        verbose_name='Medicamentos/Tratamientos',
        blank=True
    )
    
    # Seguimiento
    follow_up_schedule = models.TextField(
        verbose_name='Cronograma de Seguimiento',
        blank=True,
        help_text='Cuándo y cómo hacer seguimiento'
    )
    
    expected_duration = models.CharField(
        max_length=100,
        verbose_name='Duración Esperada',
        blank=True
    )
    
    success_criteria = models.TextField(
        verbose_name='Criterios de Éxito',
        blank=True,
        help_text='Cómo evaluar el éxito del tratamiento'
    )
    
    contraindications = models.TextField(
        verbose_name='Contraindicaciones',
        blank=True
    )
    
    precautions = models.TextField(
        verbose_name='Precauciones',
        blank=True
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    usage_count = models.IntegerField(
        default=0,
        verbose_name='Veces Usado'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_treatment_protocols',
        verbose_name='Creado por'
    )
    
    class Meta:
        verbose_name = 'Protocolo de Tratamiento'
        verbose_name_plural = 'Protocolos de Tratamiento'
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return f"{self.name} - {self.diagnosis_indication}"
    
    def increment_usage(self):
        """Incrementa el contador de uso"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])


class OpticalPrescriptionTemplate(TenantModel):
    """Plantillas de prescripción óptica"""
    
    name = models.CharField(
        max_length=200,
        verbose_name='Nombre de la Plantilla',
        help_text='Ej: Miopía Baja, Hipermetropía + Presbicia'
    )
    
    description = models.TextField(
        verbose_name='Descripción',
        blank=True
    )
    
    # Tipo de prescripción
    lens_type = models.ForeignKey(
        ClinicalParameter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'parameter_type': 'lens_type'},
        related_name='optical_templates_by_type',
        verbose_name='Tipo de Lentes'
    )
    
    lens_material = models.ForeignKey(
        ClinicalParameter,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        limit_choices_to={'parameter_type': 'lens_material'},
        related_name='optical_templates_by_material',
        verbose_name='Material Recomendado'
    )
    
    lens_coatings = models.ManyToManyField(
        ClinicalParameter,
        limit_choices_to={'parameter_type': 'lens_coating'},
        related_name='optical_templates',
        verbose_name='Tratamientos Recomendados',
        blank=True
    )
    
    recommendations = models.TextField(
        verbose_name='Recomendaciones',
        blank=True,
        help_text='Recomendaciones específicas para este tipo de prescripción'
    )
    
    notes = models.TextField(
        verbose_name='Notas',
        blank=True
    )
    
    is_active = models.BooleanField(
        default=True,
        verbose_name='Activo'
    )
    
    usage_count = models.IntegerField(
        default=0,
        verbose_name='Veces Usado'
    )
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Creación')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='Última Actualización')
    created_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_optical_templates',
        verbose_name='Creado por'
    )
    
    class Meta:
        verbose_name = 'Plantilla de Prescripción Óptica'
        verbose_name_plural = 'Plantillas de Prescripción Óptica'
        ordering = ['-usage_count', 'name']
    
    def __str__(self):
        return self.name
    
    def increment_usage(self):
        """Incrementa el contador de uso"""
        self.usage_count += 1
        self.save(update_fields=['usage_count'])
