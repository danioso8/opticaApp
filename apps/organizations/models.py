from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from datetime import timedelta


class SubscriptionPlan(models.Model):
    """Planes de suscripción disponibles"""
    PLAN_TYPES = [
        ('free', 'Gratuito'),
        ('basic', 'Básico'),
        ('professional', 'Profesional'),
        ('enterprise', 'Empresarial'),
    ]
    
    name = models.CharField(max_length=100, verbose_name='Nombre')
    slug = models.SlugField(unique=True)
    plan_type = models.CharField(max_length=20, choices=PLAN_TYPES, default='free')
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio Mensual')
    price_yearly = models.DecimalField(max_digits=10, decimal_places=2, verbose_name='Precio Anual')
    
    # Límites del plan
    max_users = models.IntegerField(default=1, verbose_name='Máximo de Usuarios')
    max_appointments_month = models.IntegerField(default=50, verbose_name='Máximo de Citas/Mes')
    max_patients = models.IntegerField(default=100, verbose_name='Máximo de Pacientes')
    max_storage_mb = models.IntegerField(default=100, verbose_name='Almacenamiento (MB)')
    
    # Características
    whatsapp_integration = models.BooleanField(default=False, verbose_name='Integración WhatsApp')
    custom_branding = models.BooleanField(default=False, verbose_name='Marca Personalizada')
    api_access = models.BooleanField(default=False, verbose_name='Acceso API')
    priority_support = models.BooleanField(default=False, verbose_name='Soporte Prioritario')
    analytics = models.BooleanField(default=False, verbose_name='Análisis Avanzado')
    multi_location = models.BooleanField(default=False, verbose_name='Múltiples Ubicaciones')
    
    is_active = models.BooleanField(default=True, verbose_name='Activo')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = 'Plan de Suscripción'
        verbose_name_plural = 'Planes de Suscripción'
        ordering = ['price_monthly']
    
    def __str__(self):
        return f"{self.name} - ${self.price_monthly}/mes"


class Organization(models.Model):
    """Representa una organización/tenant en el sistema SaaS"""
    name = models.CharField(max_length=200, verbose_name='Nombre de la Organización')
    slug = models.SlugField(unique=True, max_length=100)
    
    # Información de contacto
    email = models.EmailField(verbose_name='Email')
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    address = models.TextField(blank=True, verbose_name='Dirección')
    
    # Configuración de marca
    logo = models.ImageField(upload_to='organizations/logos/', blank=True, null=True)
    primary_color = models.CharField(max_length=7, default='#007bff', help_text='Color primario en hexadecimal')
    
    # Estado
    is_active = models.BooleanField(default=True, verbose_name='Activa')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Owner de la organización
    owner = models.ForeignKey(User, on_delete=models.PROTECT, related_name='owned_organizations')
    
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
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
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
