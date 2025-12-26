from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class PlanFeature(models.Model):
    """Módulos/Características disponibles en el sistema"""
    FEATURE_CATEGORIES = [
        ('integration', 'Integración'),
        ('analytics', 'Análisis'),
        ('customization', 'Personalización'),
        ('communication', 'Comunicación'),
        ('medical', 'Médico'),
        ('sales', 'Ventas'),
        ('other', 'Otro'),
    ]
    
    code = models.SlugField(unique=True, verbose_name='Código', help_text='Identificador único (ej: whatsapp_integration)')
    name = models.CharField(max_length=100, verbose_name='Nombre', help_text='Nombre visible del módulo')
    description = models.TextField(blank=True, verbose_name='Descripción')
    category = models.CharField(max_length=20, choices=FEATURE_CATEGORIES, default='other', verbose_name='Categoría')
    icon = models.CharField(max_length=50, blank=True, verbose_name='Ícono FontAwesome', help_text='ej: fa-whatsapp')
    
    # Precio para compra individual del módulo
    price_monthly = models.DecimalField(
        max_digits=10, 
        decimal_places=2, 
        default=0, 
        verbose_name='Precio Mensual',
        help_text='Precio si se compra individualmente (0 = no disponible para compra individual)'
    )
    
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    can_purchase_separately = models.BooleanField(
        default=False, 
        verbose_name='Compra Individual',
        help_text='¿Se puede comprar este módulo sin cambiar de plan?'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Módulo/Característica'
        verbose_name_plural = 'Módulos/Características'
        ordering = ['category', 'name']
    
    def __str__(self):
        return f"{self.name} ({self.code})"


class SubscriptionPlan(models.Model):
    """Planes de suscripción disponibles"""
    PLAN_TYPES = [
        ('free', 'Gratuito'),
        ('basic', 'Básico'),
        ('professional', 'Profesional'),
        ('premium', 'Premium'),
        ('enterprise', 'Empresarial'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nombre')
    slug = models.SlugField(unique=True)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, default='free')
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio Mensual')
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio Anual')
    
    # Límites del plan
    max_users = models.IntegerField(default=1, verbose_name='Máximo de Usuarios')
    max_organizations = models.IntegerField(default=1, verbose_name='Máximo de Organizaciones')
    max_appointments_month = models.IntegerField(default=50, verbose_name='Máximo de Citas/Mes')
    max_patients = models.IntegerField(default=100, verbose_name='Máximo de Pacientes')
    max_storage_mb = models.IntegerField(default=100, verbose_name='Almacenamiento (MB)')
    
    # Límites de Facturación Electrónica DIAN
    allow_electronic_invoicing = models.BooleanField(
        default=False,
        verbose_name='Permite Facturación Electrónica',
        help_text='¿Este plan incluye facturación electrónica DIAN?'
    )
    max_invoices_month = models.IntegerField(
        default=0,
        verbose_name='Máximo Facturas/Mes',
        help_text='0 = Ilimitado (solo para plan empresarial full), N = cantidad específica'
    )
    
    # Características (DEPRECATED - usar features M2M)
    whatsapp_integration = models.BooleanField(default=False, verbose_name='Integración WhatsApp')
    custom_branding = models.BooleanField(default=False, verbose_name='Marca Personalizada')
    api_access = models.BooleanField(default=False, verbose_name='Acceso API')
    priority_support = models.BooleanField(default=False, verbose_name='Soporte Prioritario')
    analytics = models.BooleanField(default=False, verbose_name='Análisis Avanzado')
    multi_location = models.BooleanField(default=False, verbose_name='Múltiples Ubicaciones')
    
    # Relación con módulos/características
    features = models.ManyToManyField(
        PlanFeature,
        blank=True,
        related_name='plans',
        verbose_name='Módulos/Características'
    )
    
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Plan de Suscripción'
        verbose_name_plural = 'Planes de Suscripción'
        ordering = ['price_monthly']
    
    def __str__(self):
        return f"{self.name} - ${self.price_monthly}/mes"
    
    def has_feature(self, feature_code):
        """Verifica si el plan tiene un módulo específico"""
        return self.features.filter(code=feature_code, is_active=True).exists()


class Organization(models.Model):
    """Representa una organización/tenant en el sistema SaaS"""
    name = models.CharField(max_length=200, verbose_name='Nombre de la Organización')
    slug = models.SlugField(unique=True, max_length=100)
    
    # Información legal
    legal_name = models.CharField(max_length=300, blank=True, verbose_name='Razón Social', help_text='Nombre legal registrado de la empresa')
    TAX_ID_TYPES = [
        ('RUC', 'RUC - Registro Único de Contribuyentes'),
        ('NIT', 'NIT - Número de Identificación Tributaria'),
        ('RFC', 'RFC - Registro Federal de Contribuyentes'),
        ('CUIT', 'CUIT - Clave Única de Identificación Tributaria'),
        ('RUT', 'RUT - Rol Único Tributario'),
        ('OTHER', 'Otro'),
    ]
    tax_id_type = models.CharField(max_length=10, choices=TAX_ID_TYPES, blank=True, verbose_name='Tipo de Documento Fiscal')
    tax_id = models.CharField(max_length=50, blank=True, verbose_name='Número Fiscal', help_text='Número de identificación fiscal')
    legal_representative = models.CharField(max_length=200, blank=True, verbose_name='Representante Legal')
    
    # Información de contacto
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    secondary_phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono Secundario')
    address = models.TextField(blank=True, verbose_name='Dirección')
    neighborhood = models.CharField(max_length=100, blank=True, verbose_name='Barrio')
    city = models.CharField(max_length=100, blank=True, verbose_name='Ciudad')
    state = models.CharField(max_length=100, blank=True, verbose_name='Estado/Provincia')
    country = models.CharField(max_length=100, blank=True, default='Colombia', verbose_name='País')
    postal_code = models.CharField(max_length=20, blank=True, verbose_name='Código Postal')
    website = models.URLField(blank=True, verbose_name='Sitio Web')
    
    # Configuración de marca
    logo = models.ImageField(upload_to='organizations/logos/', blank=True, null=True)
    primary_color = models.CharField(max_length=7, default='#007bff', help_text='Color primario en hexadecimal')
    
    # Estado
    is_active = models.BooleanField(default=True, verbose_name='Activa')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Owner de la organización
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_organizations')
    
    class Meta:
        verbose_name = 'Organización'
        verbose_name_plural = 'Organizaciones'
        ordering = ['name']
    
    def __str__(self):
        return self.name
    
    @property
    def current_subscription(self):
        """Retorna la suscripción activa actual"""
        return self.subscriptions.filter(
            is_active=True,
            start_date__lte=timezone.now(),
            end_date__gte=timezone.now()
        ).first()
    
    @property
    def is_subscription_active(self):
        """Verifica si tiene una suscripción activa"""
        return self.current_subscription is not None
    
    def get_plan_limits(self):
        """Retorna los límites del plan actual"""
        subscription = self.current_subscription
        if subscription:
            return {
                'max_users': subscription.plan.max_users,
                'max_appointments_month': subscription.plan.max_appointments_month,
                'max_patients': subscription.plan.max_patients,
                'max_storage_mb': subscription.plan.max_storage_mb,
                'features': {
                    'whatsapp_integration': subscription.plan.whatsapp_integration,
                    'custom_branding': subscription.plan.custom_branding,
                    'api_access': subscription.plan.api_access,
                    'priority_support': subscription.plan.priority_support,
                    'analytics': subscription.plan.analytics,
                    'multi_location': subscription.plan.multi_location,
                }
            }
        return None
    
    def has_feature(self, feature_code):
        """
        Verifica si la organización tiene acceso a un módulo específico.
        Considera tanto el plan como módulos comprados individualmente.
        """
        # Verificar si viene del plan actual
        subscription = self.current_subscription
        if subscription and subscription.plan.has_feature(feature_code):
            return True
        
        # Verificar si fue habilitado manualmente o comprado por separado
        org_feature = self.enabled_features.filter(
            feature__code=feature_code,
            is_enabled=True
        ).first()
        
        if org_feature:
            return org_feature.is_active
        
        return False
    
    def get_available_invoices(self):
        """
        Calcula el total de facturas electrónicas disponibles.
        Incluye las del plan + paquetes comprados.
        """
        total_available = 0
        
        # Facturas del plan
        subscription = self.current_subscription
        if subscription and subscription.plan.allow_electronic_invoicing:
            plan_invoices = subscription.plan.max_invoices_month
            if plan_invoices == 0:  # Ilimitado
                return 999999
            total_available += plan_invoices
        
        # Facturas de paquetes comprados
        invoice_purchases = self.invoice_purchases.filter(
            payment_status='paid'
        )
        
        for purchase in invoice_purchases:
            if purchase.is_valid:
                total_available += purchase.remaining_invoices
        
        return total_available
    
    def use_invoice(self):
        """
        Registra el uso de una factura electrónica.
        Descuenta primero de los paquetes comprados, luego del plan.
        """
        # Intentar usar de paquetes comprados primero
        invoice_purchases = self.invoice_purchases.filter(
            payment_status='paid'
        ).order_by('purchased_at')
        
        for purchase in invoice_purchases:
            if purchase.is_valid and purchase.remaining_invoices > 0:
                purchase.used_invoices += 1
                purchase.save()
                return True
        
        # Si no hay paquetes, verificar si el plan permite
        subscription = self.current_subscription
        if subscription and subscription.plan.allow_electronic_invoicing:
            if subscription.plan.max_invoices_month == 0:  # Ilimitado
                return True
            # Si tiene límite, deberíamos llevar un contador mensual
            # Por ahora retornamos True si el plan lo permite
            return True
        
        return False


class Subscription(models.Model):
    """Suscripción de una organización a un plan"""
    BILLING_CYCLES = [
        ('monthly', 'Mensual'),
        ('yearly', 'Anual'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.CASCADE)
    billing_cycle = models.CharField(max_length=10, choices=BILLING_CYCLES, default='monthly')
    
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField()
    
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=True, verbose_name='Renovación Automática')
    
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS, default='pending')
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Suscripción'
        verbose_name_plural = 'Suscripciones'
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.organization.name} - {self.plan.name} ({self.billing_cycle})"
    
    def save(self, *args, **kwargs):
        # Calcular end_date si no está establecida
        if not self.end_date:
            if self.billing_cycle == 'monthly':
                self.end_date = self.start_date + timedelta(days=30)
            else:  # yearly
                self.end_date = self.start_date + timedelta(days=365)
        
        # Establecer el monto pagado según el plan
        if not self.amount_paid:
            if self.billing_cycle == 'monthly':
                self.amount_paid = self.plan.price_monthly
            else:
                self.amount_paid = self.plan.price_yearly
        
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Verifica si la suscripción ha expirado"""
        return timezone.now() > self.end_date
    
    @property
    def days_remaining(self):
        """Calcula los días restantes de la suscripción"""
        if self.is_expired:
            return 0
        delta = self.end_date - timezone.now()
        return delta.days
    
    def has_feature(self, feature_code):
        """Verifica si la suscripción tiene acceso a un módulo específico"""
        if not self.is_active or self.is_expired:
            return False
        return self.plan.has_feature(feature_code)


class OrganizationMember(models.Model):
    """Miembros de una organización con sus roles"""
    ROLES = [
        ('owner', 'Propietario'),
        ('admin', 'Administrador'),
        ('staff', 'Personal'),
        ('viewer', 'Visualizador'),
    ]
    
    organization = models.ForeignKey(Organization, on_delete=models.CASCADE, related_name='members')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='organization_memberships')
    role = models.CharField(max_length=20, choices=ROLES, default='staff')
    
    is_active = models.BooleanField(default=True)
    joined_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Miembro de Organización'
        verbose_name_plural = 'Miembros de Organización'
        unique_together = ['organization', 'user']
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.organization.name} ({self.get_role_display()})"


class LandingPageConfig(models.Model):
    """Configuración personalizada de la landing page"""
    
    NAVBAR_STYLES = [
        ('classic', 'Clásico - Navbar blanco con sombra'),
        ('modern', 'Moderno - Navbar con gradiente y transparencia'),
        ('minimal', 'Minimalista - Navbar transparente con línea inferior'),
        ('bold', 'Bold - Navbar oscuro con contraste alto'),
        ('glass', 'Glass - Efecto cristal difuminado (moderno)'),
        ('floating', 'Flotante - Navbar elevado con sombras suaves'),
        ('gradient_modern', 'Gradiente Moderno - Colores vibrantes'),
        ('sidebar', 'Sidebar - Navegación lateral (responsive)'),
    ]
    
    HERO_STYLES = [
        ('gradient', 'Gradiente - Fondo con degradado de colores'),
        ('image', 'Imagen - Imagen de fondo con overlay'),
        ('split', 'Split - Contenido dividido 50/50'),
        ('centered', 'Centrado - Contenido al centro con imagen de fondo'),
        ('video', 'Video - Fondo de video (próximamente)'),
    ]
    
    SERVICES_LAYOUT = [
        ('grid', 'Grid - Tarjetas en cuadrícula'),
        ('carousel', 'Carrusel - Deslizable horizontal'),
        ('list', 'Lista - Vista vertical detallada'),
        ('masonry', 'Masonry - Diseño tipo Pinterest'),
    ]
    
    FONT_FAMILIES = [
        ('inter', 'Inter - Moderna y limpia'),
        ('roboto', 'Roboto - Profesional y versátil'),
        ('poppins', 'Poppins - Redondeada y amigable'),
        ('playfair', 'Playfair Display - Elegante y serif'),
        ('montserrat', 'Montserrat - Bold y geométrica'),
        ('lato', 'Lato - Clásica y legible'),
    ]
    
    ANIMATION_SPEEDS = [
        ('none', 'Sin animaciones'),
        ('slow', 'Lentas - Suaves y sutiles'),
        ('normal', 'Normales - Balance perfecto'),
        ('fast', 'Rápidas - Dinámicas y enérgicas'),
    ]
    
    organization = models.OneToOneField(
        Organization, 
        on_delete=models.CASCADE, 
        related_name='landing_config',
        verbose_name='Organización'
    )
    
    # Logo de la organización
    logo = models.ImageField(
        upload_to='landing/logos/', 
        blank=True, 
        null=True,
        verbose_name='Logo',
        help_text='Logo de la empresa. Recomendado: 200x60px, fondo transparente PNG'
    )
    
    LOGO_SIZES = [
        ('small', 'Pequeño - 8 (32px)'),
        ('medium', 'Mediano - 10 (40px)'),
        ('large', 'Grande - 12 (48px)'),
        ('xlarge', 'Extra Grande - 16 (64px)'),
        ('xxlarge', 'Muy Grande - 20 (80px)'),
    ]
    
    logo_size = models.CharField(
        max_length=10,
        choices=LOGO_SIZES,
        default='medium',
        verbose_name='Tamaño del Logo',
        help_text='Selecciona el tamaño del logo en el navbar'
    )
    
    # Estilo del navbar
    navbar_style = models.CharField(
        max_length=20,
        choices=NAVBAR_STYLES,
        default='classic',
        verbose_name='Estilo del Navbar',
        help_text='Selecciona el diseño del navbar'
    )
    
    # Estilo de la sección Hero
    hero_style = models.CharField(
        max_length=20,
        choices=HERO_STYLES,
        default='gradient',
        verbose_name='Estilo del Hero',
        help_text='Diseño de la sección principal'
    )
    hero_bg_gradient_start = models.CharField(
        max_length=7,
        default='#3b82f6',
        verbose_name='Color inicio degradado',
        help_text='Color inicial del gradiente'
    )
    hero_bg_gradient_end = models.CharField(
        max_length=7,
        default='#8b5cf6',
        verbose_name='Color fin degradado',
        help_text='Color final del gradiente'
    )
    hero_overlay_opacity = models.IntegerField(
        default=50,
        verbose_name='Opacidad del overlay',
        help_text='0-100, aplica a imagen de fondo'
    )
    
    HERO_IMAGE_FIT = [
        ('cover', 'Cubrir - Llena todo el espacio (puede recortar)'),
        ('contain', 'Contener - Muestra la imagen completa (sin recortar)'),
        ('fill', 'Rellenar - Estira la imagen para llenar el espacio'),
        ('none', 'Original - Tamaño original de la imagen'),
    ]
    
    hero_image_fit = models.CharField(
        max_length=10,
        choices=HERO_IMAGE_FIT,
        default='cover',
        verbose_name='Ajuste de Imagen Hero',
        help_text='Cómo se ajusta la imagen de fondo en la sección principal'
    )
    
    # Posición y zoom de la imagen hero
    hero_image_position_x = models.IntegerField(
        default=50,
        verbose_name='Posición Horizontal',
        help_text='0-100, posición horizontal de la imagen (%)'
    )
    hero_image_position_y = models.IntegerField(
        default=50,
        verbose_name='Posición Vertical',
        help_text='0-100, posición vertical de la imagen (%)'
    )
    hero_image_scale = models.IntegerField(
        default=100,
        verbose_name='Escala de Imagen',
        help_text='50-200, tamaño de la imagen (%)'
    )
    
    # Layout de servicios
    services_layout = models.CharField(
        max_length=20,
        choices=SERVICES_LAYOUT,
        default='grid',
        verbose_name='Layout de Servicios',
        help_text='Diseño de la sección de servicios'
    )
    services_bg_color = models.CharField(
        max_length=7,
        default='#f9fafb',
        verbose_name='Color de fondo Servicios',
        help_text='Color en formato hexadecimal'
    )
    
    # Tipografía
    font_family = models.CharField(
        max_length=20,
        choices=FONT_FAMILIES,
        default='inter',
        verbose_name='Familia de fuente',
        help_text='Tipografía principal del sitio'
    )
    heading_font_size = models.IntegerField(
        default=48,
        verbose_name='Tamaño título principal',
        help_text='Tamaño en píxeles'
    )
    
    # Animaciones
    animation_speed = models.CharField(
        max_length=20,
        choices=ANIMATION_SPEEDS,
        default='normal',
        verbose_name='Velocidad de animaciones',
        help_text='Controla las animaciones del sitio'
    )
    enable_parallax = models.BooleanField(
        default=False,
        verbose_name='Efecto Parallax',
        help_text='Efecto de profundidad en scroll'
    )
    enable_hover_effects = models.BooleanField(
        default=True,
        verbose_name='Efectos Hover',
        help_text='Efectos al pasar el mouse'
    )
    
    # Colores del navbar
    navbar_bg_color = models.CharField(
        max_length=7, 
        default='#ffffff',
        verbose_name='Color de fondo del Navbar',
        help_text='Color en formato hexadecimal (ej: #ffffff)'
    )
    navbar_text_color = models.CharField(
        max_length=7, 
        default='#1f2937',
        verbose_name='Color del texto del Navbar',
        help_text='Color en formato hexadecimal (ej: #1f2937)'
    )
    navbar_hover_color = models.CharField(
        max_length=7, 
        default='#2563eb',
        verbose_name='Color hover del Navbar',
        help_text='Color en formato hexadecimal (ej: #2563eb)'
    )
    
    # Imágenes de la landing page
    hero_image = models.ImageField(
        upload_to='landing/hero/', 
        blank=True, 
        null=True,
        verbose_name='Imagen Principal (Hero)',
        help_text='Recomendado: 1920x1080px'
    )
    service_image_1 = models.ImageField(
        upload_to='landing/services/', 
        blank=True, 
        null=True,
        verbose_name='Imagen Servicio 1 (Examen Visual)',
        help_text='Recomendado: 612x612px'
    )
    service_image_2 = models.ImageField(
        upload_to='landing/services/', 
        blank=True, 
        null=True,
        verbose_name='Imagen Servicio 2 (Monturas)',
        help_text='Recomendado: 612x612px'
    )
    service_image_3 = models.ImageField(
        upload_to='landing/services/', 
        blank=True, 
        null=True,
        verbose_name='Imagen Servicio 3 (Lentes de Contacto)',
        help_text='Recomendado: 612x612px'
    )
    service_image_4 = models.ImageField(
        upload_to='landing/services/', 
        blank=True, 
        null=True,
        verbose_name='Imagen Servicio 4 (Lentes de Sol)',
        help_text='Recomendado: 612x612px'
    )
    
    # Textos personalizables
    hero_title = models.CharField(
        max_length=200, 
        default='Cuida tu Salud Visual',
        verbose_name='Título Principal',
        blank=True
    )
    hero_subtitle = models.TextField(
        default='Tecnología de última generación y atención personalizada para el cuidado de tus ojos.',
        verbose_name='Subtítulo Principal',
        blank=True
    )
    hero_title_color = models.CharField(
        max_length=7, 
        default='#ffffff',
        verbose_name='Color del Título Principal',
        help_text='Color en formato hexadecimal (ej: #ffffff)'
    )
    hero_subtitle_color = models.CharField(
        max_length=7, 
        default='#bfdbfe',
        verbose_name='Color del Subtítulo Principal',
        help_text='Color en formato hexadecimal (ej: #bfdbfe)'
    )
    
    # Sección "Por qué elegirnos"
    why_choose_title = models.CharField(
        max_length=200, 
        default='¿Por qué elegirnos?',
        verbose_name='Título "Por qué elegirnos"',
        blank=True
    )
    why_choose_subtitle = models.CharField(
        max_length=200, 
        default='La mejor atención para tus ojos',
        verbose_name='Subtítulo "Por qué elegirnos"',
        blank=True
    )
    
    # Sección Servicios
    services_title = models.CharField(
        max_length=200, 
        default='Nuestros Servicios',
        verbose_name='Título Servicios',
        blank=True
    )
    services_subtitle = models.CharField(
        max_length=200, 
        default='Cuidado integral para tu salud visual',
        verbose_name='Subtítulo Servicios',
        blank=True
    )
    
    service_1_title = models.CharField(
        max_length=100, 
        default='Examen Visual Completo',
        verbose_name='Título Servicio 1',
        blank=True
    )
    service_1_description = models.TextField(
        default='Evaluación exhaustiva de tu salud visual con equipos de última generación.',
        verbose_name='Descripción Servicio 1',
        blank=True
    )
    
    service_2_title = models.CharField(
        max_length=100, 
        default='Monturas y Lentes',
        verbose_name='Título Servicio 2',
        blank=True
    )
    service_2_description = models.TextField(
        default='Amplio catálogo de monturas y lentes de las mejores marcas.',
        verbose_name='Descripción Servicio 2',
        blank=True
    )
    
    service_3_title = models.CharField(
        max_length=100, 
        default='Lentes de Contacto',
        verbose_name='Título Servicio 3',
        blank=True
    )
    service_3_description = models.TextField(
        default='Adaptación profesional y variedad de lentes de contacto.',
        verbose_name='Descripción Servicio 3',
        blank=True
    )
    
    service_4_title = models.CharField(
        max_length=100, 
        default='Lentes de Sol',
        verbose_name='Título Servicio 4',
        blank=True
    )
    service_4_description = models.TextField(
        default='Protección UV total con estilo y calidad garantizada.',
        verbose_name='Descripción Servicio 4',
        blank=True
    )
    
    # Sección Contacto
    contact_title = models.CharField(
        max_length=200, 
        default='¿Tienes Preguntas?',
        verbose_name='Título Contacto',
        blank=True
    )
    contact_subtitle = models.TextField(
        default='Estamos aquí para ayudarte. Contáctanos por cualquiera de nuestros canales.',
        verbose_name='Subtítulo Contacto',
        blank=True
    )
    
    # Configuración de botones
    primary_button_color = models.CharField(
        max_length=7, 
        default='#2563eb',
        verbose_name='Color Botón Primario',
        help_text='Color en formato hexadecimal (ej: #2563eb)'
    )
    secondary_button_color = models.CharField(
        max_length=7, 
        default='#ffffff',
        verbose_name='Color Botón Secundario',
        help_text='Color en formato hexadecimal (ej: #ffffff)'
    )
    button_border_radius = models.IntegerField(
        default=8,
        verbose_name='Radio de borde botones',
        help_text='En píxeles (0 = cuadrado, 999 = circular)'
    )
    button_shadow = models.BooleanField(
        default=True,
        verbose_name='Sombra en botones',
        help_text='Agrega sombra a los botones'
    )
    
    # Tarjetas y contenedores
    card_border_radius = models.IntegerField(
        default=12,
        verbose_name='Radio de borde tarjetas',
        help_text='En píxeles para tarjetas de servicios'
    )
    card_shadow_intensity = models.CharField(
        max_length=20,
        choices=[
            ('none', 'Sin sombra'),
            ('sm', 'Suave'),
            ('md', 'Media'),
            ('lg', 'Fuerte'),
            ('xl', 'Extra fuerte'),
        ],
        default='md',
        verbose_name='Intensidad de sombra',
        help_text='Sombra de tarjetas y elementos'
    )
    
    # Espaciado
    section_spacing = models.CharField(
        max_length=20,
        choices=[
            ('compact', 'Compacto - Espacios pequeños'),
            ('normal', 'Normal - Balance estándar'),
            ('spacious', 'Espacioso - Espacios amplios'),
        ],
        default='normal',
        verbose_name='Espaciado de secciones',
        help_text='Espaciado vertical entre secciones'
    )
    
    # Elementos adicionales
    show_scroll_indicator = models.BooleanField(
        default=True,
        verbose_name='Indicador de scroll',
        help_text='Flecha animada en hero section'
    )
    show_testimonials = models.BooleanField(
        default=False,
        verbose_name='Mostrar testimonios',
        help_text='Sección de testimonios de clientes'
    )
    show_stats = models.BooleanField(
        default=False,
        verbose_name='Mostrar estadísticas',
        help_text='Números destacados (años, clientes, etc)'
    )
    cta_badge_text = models.CharField(
        max_length=50,
        blank=True,
        verbose_name='Texto badge CTA',
        help_text='Pequeño badge sobre título (ej: "Nuevo", "Popular")'
    )
    cta_badge_color = models.CharField(
        max_length=7,
        default='#10b981',
        verbose_name='Color badge CTA',
        help_text='Color del badge en hexadecimal'
    )
    
    # Footer
    footer_bg_color = models.CharField(
        max_length=7, 
        default='#111827',
        verbose_name='Color de fondo del Footer',
        help_text='Color en formato hexadecimal (ej: #111827)'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Configuración de Landing Page'
        verbose_name_plural = 'Configuraciones de Landing Page'
    
    def __str__(self):
        return f"Landing Page Config - {self.organization.name}"


class OrganizationFeature(models.Model):
    """Módulos/características habilitados para una organización específica"""
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='enabled_features',
        verbose_name='Organización'
    )
    feature = models.ForeignKey(
        PlanFeature,
        on_delete=models.CASCADE,
        related_name='organization_assignments',
        verbose_name='Módulo'
    )
    
    # Control de acceso
    is_enabled = models.BooleanField(default=True, verbose_name='Habilitado')
    granted_by_plan = models.BooleanField(
        default=True,
        verbose_name='Incluido en Plan',
        help_text='True si viene del plan, False si fue comprado por separado'
    )
    
    # Información de compra adicional
    purchased_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Compra')
    expires_at = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Expiración')
    amount_paid = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name='Monto Pagado'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Módulo de Organización'
        verbose_name_plural = 'Módulos de Organizaciones'
        unique_together = ['organization', 'feature']
        ordering = ['organization', 'feature__category', 'feature__name']
    
    def __str__(self):
        return f"{self.organization.name} - {self.feature.name}"
    
    @property
    def is_active(self):
        """Verifica si el módulo está activo y no ha expirado"""
        if not self.is_enabled:
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        return True


class InvoicePackagePurchase(models.Model):
    """Compra de paquetes adicionales de facturas electrónicas DIAN"""
    PACKAGE_SIZES = [
        (50, '50 facturas'),
        (100, '100 facturas'),
        (200, '200 facturas'),
        (500, '500 facturas'),
        (1000, '1000 facturas'),
    ]
    
    PACKAGE_PRICES = {
        50: 19900.00,
        100: 35900.00,
        200: 65900.00,
        500: 149900.00,
        1000: 279900.00,
    }
    
    PAYMENT_STATUS = [
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado'),
    ]
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='invoice_purchases',
        verbose_name='Organización'
    )
    
    quantity = models.IntegerField(
        choices=PACKAGE_SIZES,
        verbose_name='Cantidad de Facturas'
    )
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio'
    )
    
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending',
        verbose_name='Estado de Pago'
    )
    
    used_invoices = models.IntegerField(
        default=0,
        verbose_name='Facturas Usadas'
    )
    
    purchased_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Compra')
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name='Fecha de Expiración',
        help_text='Opcional: fecha de vencimiento del paquete'
    )
    
    # Información de pago
    payment_reference = models.CharField(max_length=100, blank=True, verbose_name='Referencia de Pago')
    payment_date = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Pago')
    
    class Meta:
        verbose_name = 'Compra de Paquete de Facturas'
        verbose_name_plural = 'Compras de Paquetes de Facturas'
        ordering = ['-purchased_at']
    
    def __str__(self):
        return f"{self.organization.name} - {self.quantity} facturas ({self.get_payment_status_display()})"
    
    @property
    def remaining_invoices(self):
        """Facturas restantes del paquete"""
        return max(0, self.quantity - self.used_invoices)
    
    @property
    def is_valid(self):
        """Verifica si el paquete es válido (pagado y no expirado)"""
        if self.payment_status != 'paid':
            return False
        if self.expires_at and timezone.now() > self.expires_at:
            return False
        if self.remaining_invoices <= 0:
            return False
        return True


class AddonPurchase(models.Model):
    """Compra de add-ons/módulos individuales"""
    BILLING_CYCLES = [
        ('monthly', 'Mensual'),
        ('quarterly', 'Trimestral'),
        ('yearly', 'Anual'),
        ('lifetime', 'Vitalicio'),
    ]
    
    PAYMENT_STATUS = [
        ('pending', 'Pendiente'),
        ('paid', 'Pagado'),
        ('failed', 'Fallido'),
        ('cancelled', 'Cancelado'),
    ]
    
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='addon_purchases',
        verbose_name='Organización'
    )
    feature = models.ForeignKey(
        PlanFeature,
        on_delete=models.PROTECT,
        verbose_name='Módulo'
    )
    
    billing_cycle = models.CharField(
        max_length=20,
        choices=BILLING_CYCLES,
        default='monthly',
        verbose_name='Ciclo de Facturación'
    )
    
    price = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        verbose_name='Precio'
    )
    
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS,
        default='pending',
        verbose_name='Estado de Pago'
    )
    
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    auto_renew = models.BooleanField(default=True, verbose_name='Renovación Automática')
    
    start_date = models.DateTimeField(default=timezone.now, verbose_name='Fecha de Inicio')
    end_date = models.DateTimeField(verbose_name='Fecha de Fin')
    
    purchased_at = models.DateTimeField(auto_now_add=True, verbose_name='Fecha de Compra')
    
    # Información de pago
    payment_reference = models.CharField(max_length=100, blank=True, verbose_name='Referencia de Pago')
    payment_date = models.DateTimeField(null=True, blank=True, verbose_name='Fecha de Pago')
    
    class Meta:
        verbose_name = 'Compra de Módulo Adicional'
        verbose_name_plural = 'Compras de Módulos Adicionales'
        ordering = ['-purchased_at']
    
    def __str__(self):
        return f"{self.organization.name} - {self.feature.name} ({self.get_billing_cycle_display()})"
    
    def save(self, *args, **kwargs):
        # Calcular end_date según el ciclo de facturación
        if not self.end_date:
            if self.billing_cycle == 'monthly':
                self.end_date = self.start_date + timedelta(days=30)
            elif self.billing_cycle == 'quarterly':
                self.end_date = self.start_date + timedelta(days=90)
            elif self.billing_cycle == 'yearly':
                self.end_date = self.start_date + timedelta(days=365)
            else:  # lifetime
                self.end_date = self.start_date + timedelta(days=36500)  # 100 años
        
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Verifica si la compra ha expirado"""
        return timezone.now() > self.end_date
    
    @property
    def days_remaining(self):
        """Días restantes de la compra"""
        if self.is_expired:
            return 0
        delta = self.end_date - timezone.now()
        return delta.days
