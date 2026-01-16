"""
Modelos para AR Virtual Try-On (Prueba Virtual de Monturas)
"""
from django.db import models
from django.utils import timezone
from apps.organizations.base_models import TenantModel
from apps.core.storage_utils import OrganizationUploadPath


class FrameCategory(TenantModel):
    """Categorías de monturas"""
    
    name = models.CharField(max_length=100, verbose_name='Nombre')
    description = models.TextField(blank=True, verbose_name='Descripción')
    icon = models.CharField(max_length=50, blank=True, verbose_name='Icono Font Awesome')
    order = models.IntegerField(default=0, verbose_name='Orden')
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Categoría de Montura'
        verbose_name_plural = 'Categorías de Monturas'
        ordering = ['order', 'name']
    
    def __str__(self):
        return self.name


class Frame(TenantModel):
    """Monturas disponibles para prueba virtual"""
    
    GENDER_CHOICES = [
        ('unisex', 'Unisex'),
        ('male', 'Hombre'),
        ('female', 'Mujer'),
        ('kids', 'Niños'),
    ]
    
    FACE_SHAPE_CHOICES = [
        ('oval', 'Óvalo'),
        ('round', 'Redondo'),
        ('square', 'Cuadrado'),
        ('heart', 'Corazón'),
        ('triangle', 'Triángulo'),
        ('diamond', 'Diamante'),
    ]
    
    MATERIAL_CHOICES = [
        ('metal', 'Metal'),
        ('acetate', 'Acetato'),
        ('titanium', 'Titanio'),
        ('plastic', 'Plástico'),
        ('mixed', 'Mixto'),
    ]
    
    # Información básica
    code = models.CharField(max_length=50, verbose_name='Código', unique=True)
    name = models.CharField(max_length=200, verbose_name='Nombre')
    category = models.ForeignKey(FrameCategory, on_delete=models.PROTECT, related_name='frames', verbose_name='Categoría')
    brand = models.CharField(max_length=100, blank=True, verbose_name='Marca')
    
    # Características
    description = models.TextField(blank=True, verbose_name='Descripción')
    color = models.CharField(max_length=50, verbose_name='Color')
    material = models.CharField(max_length=50, choices=MATERIAL_CHOICES, verbose_name='Material')
    gender = models.CharField(max_length=20, choices=GENDER_CHOICES, default='unisex', verbose_name='Género')
    
    # Dimensiones (en mm)
    lens_width = models.IntegerField(verbose_name='Ancho de lente', help_text='En milímetros')
    bridge_width = models.IntegerField(verbose_name='Ancho de puente', help_text='En milímetros')
    temple_length = models.IntegerField(verbose_name='Largo de patilla', help_text='En milímetros')
    
    # Recomendaciones
    recommended_face_shapes = models.CharField(
        max_length=200,
        blank=True,
        verbose_name='Formas de rostro recomendadas',
        help_text='Separadas por comas: oval,round,square'
    )
    
    # Imágenes para AR
    front_image = models.ImageField(upload_to=OrganizationUploadPath('ar_frames/front'), verbose_name='Imagen Frontal')
    side_image = models.ImageField(upload_to=OrganizationUploadPath('ar_frames/side'), blank=True, verbose_name='Imagen Lateral')
    overlay_image = models.ImageField(
        upload_to='ar_frames/overlay/',
        blank=True,
        verbose_name='Imagen para Overlay AR',
        help_text='PNG transparente con la montura para superponer en rostro'
    )
    
    # Puntos de anclaje para AR (formato JSON)
    anchor_points = models.TextField(
        blank=True,
        verbose_name='Puntos de Anclaje JSON',
        help_text='Coordenadas de referencia para posicionar la montura: {left_eye: {x, y}, right_eye: {x, y}, bridge: {x, y}}'
    )
    
    # Inventario y precio
    stock = models.IntegerField(default=0, verbose_name='Stock')
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio')
    
    # Estado
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    is_featured = models.BooleanField(default=False, verbose_name='Destacado')
    
    # Analytics
    try_on_count = models.IntegerField(default=0, verbose_name='Veces Probado')
    favorite_count = models.IntegerField(default=0, verbose_name='Favoritos')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Montura'
        verbose_name_plural = 'Monturas'
        ordering = ['-is_featured', '-created_at']
        indexes = [
            models.Index(fields=['organization', 'is_active', '-is_featured']),
            models.Index(fields=['organization', 'category', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.code} - {self.name}"
    
    @property
    def total_width(self):
        """Ancho total de la montura"""
        return self.lens_width * 2 + self.bridge_width
    
    def increment_try_on(self):
        """Incrementa el contador de pruebas"""
        self.try_on_count += 1
        self.save(update_fields=['try_on_count'])


class VirtualTryOnSession(TenantModel):
    """Sesiones de prueba virtual"""
    
    patient = models.ForeignKey(
        'patients.Patient',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='tryon_sessions',
        verbose_name='Paciente'
    )
    
    # Detección facial
    face_shape_detected = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Forma de Rostro Detectada'
    )
    
    face_measurements = models.TextField(
        blank=True,
        verbose_name='Medidas Faciales JSON',
        help_text='Distancia entre ojos, ancho de cara, etc.'
    )
    
    # Sesión
    frames_tried = models.ManyToManyField(
        Frame,
        through='FrameTryOnRecord',
        related_name='sessions',
        verbose_name='Monturas Probadas'
    )
    
    session_duration = models.IntegerField(default=0, verbose_name='Duración (segundos)')
    device_info = models.CharField(max_length=200, blank=True, verbose_name='Info del Dispositivo')
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Sesión de Prueba Virtual'
        verbose_name_plural = 'Sesiones de Prueba Virtual'
        ordering = ['-created_at']
    
    def __str__(self):
        patient_name = self.patient.full_name if self.patient else 'Anónimo'
        return f"Sesión {self.id} - {patient_name} - {self.created_at.date()}"


class FrameTryOnRecord(models.Model):
    """Registro de cada montura probada en una sesión"""
    
    session = models.ForeignKey(
        VirtualTryOnSession,
        on_delete=models.CASCADE,
        related_name='try_records'
    )
    
    frame = models.ForeignKey(
        Frame,
        on_delete=models.CASCADE,
        related_name='try_records'
    )
    
    # Foto capturada
    photo = models.ImageField(
        upload_to='ar_tryon_photos/%Y/%m/%d/',
        blank=True,
        verbose_name='Foto Capturada'
    )
    
    # Rating
    rating = models.IntegerField(
        null=True,
        blank=True,
        verbose_name='Calificación (1-5)'
    )
    
    is_favorite = models.BooleanField(default=False, verbose_name='Favorito')
    
    # Tiempo de visualización
    view_duration = models.IntegerField(default=0, verbose_name='Tiempo de Visualización (segundos)')
    
    tried_at = models.DateTimeField(default=timezone.now)
    
    class Meta:
        verbose_name = 'Registro de Prueba'
        verbose_name_plural = 'Registros de Pruebas'
        ordering = ['-tried_at']
    
    def __str__(self):
        return f"{self.frame.name} - {self.tried_at}"


class FaceShapeRecommendation(models.Model):
    """Recomendaciones de monturas según forma de rostro"""
    
    FACE_SHAPES = [
        ('oval', 'Óvalo'),
        ('round', 'Redondo'),
        ('square', 'Cuadrado'),
        ('heart', 'Corazón'),
        ('triangle', 'Triángulo'),
        ('diamond', 'Diamante'),
    ]
    
    face_shape = models.CharField(max_length=50, choices=FACE_SHAPES, unique=True)
    
    # Recomendaciones
    recommended_styles = models.TextField(verbose_name='Estilos Recomendados')
    avoid_styles = models.TextField(verbose_name='Estilos a Evitar')
    tips = models.TextField(verbose_name='Consejos')
    
    # Características ideales
    ideal_frame_width = models.CharField(max_length=100, blank=True, verbose_name='Ancho Ideal')
    ideal_frame_shapes = models.CharField(max_length=200, blank=True, verbose_name='Formas Ideales')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Recomendación por Forma de Rostro'
        verbose_name_plural = 'Recomendaciones por Forma de Rostro'
    
    def __str__(self):
        return f"Recomendaciones para rostro {self.get_face_shape_display()}"
