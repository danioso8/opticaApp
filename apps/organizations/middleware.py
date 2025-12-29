from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from .models import Organization, OrganizationMember


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware que identifica y establece la organización (tenant) actual
    basándose en el subdominio o en la sesión del usuario
    """
    
    EXEMPT_PATHS = ['/admin/', '/saas-admin/', '/dashboard/login/', '/dashboard/logout/', '/organizations/register/']
    
    def process_request(self, request):
        # Inicializar el tenant en None
        request.organization = None
        request.tenant = None
        
        # Verificar si la ruta está exenta
        for exempt_path in self.EXEMPT_PATHS:
            if request.path.startswith(exempt_path):
                return None
        
        # Si el usuario no está autenticado, no hay tenant
        if not request.user.is_authenticated:
            return None
        
        # Los superusuarios no requieren tenant
        if request.user.is_superuser:
            return None
        
        # Intentar obtener la organización del subdominio
        host = request.get_host().split(':')[0]  # Remover puerto si existe
        subdomain = self._get_subdomain(host)
        
        if subdomain and subdomain != 'www':
            try:
                organization = Organization.objects.get(slug=subdomain, is_active=True)
                # Verificar que el usuario es miembro de esta organización
                if self._user_is_member(request.user, organization):
                    request.organization = organization
                    request.tenant = organization
                    return None
            except Organization.DoesNotExist:
                pass
        
        # Si no hay subdomain válido, intentar obtener de la sesión
        org_id = request.session.get('current_organization_id')
        if org_id:
            try:
                organization = Organization.objects.get(id=org_id, is_active=True)
                if self._user_is_member(request.user, organization):
                    request.organization = organization
                    request.tenant = organization
                    return None
            except Organization.DoesNotExist:
                # Limpiar sesión si la organización no existe
                del request.session['current_organization_id']
        
        # Si el usuario no tiene organización, intentar obtener la primera disponible
        membership = OrganizationMember.objects.filter(
            user=request.user,
            is_active=True,
            organization__is_active=True
        ).first()
        
        if membership:
            request.organization = membership.organization
            request.tenant = membership.organization
            request.session['current_organization_id'] = membership.organization.id
        
        return None
    
    def _get_subdomain(self, host):
        """Extrae el subdominio del host"""
        parts = host.split('.')
        if len(parts) > 2:
            return parts[0]
        return None
    
    def _user_is_member(self, user, organization):
        """Verifica si el usuario es miembro de la organización"""
        return OrganizationMember.objects.filter(
            user=user,
            organization=organization,
            is_active=True
        ).exists()


class SubscriptionMiddleware(MiddlewareMixin):
    """
    Middleware que verifica que el usuario tenga una suscripción activa
    (La suscripción está asociada al usuario, no a la organización)
    """
    
    # URLs que no requieren suscripción activa
    EXEMPT_URLS = [
        '/admin/',
        '/saas-admin/',
        '/dashboard/login/',
        '/dashboard/logout/',
        '/dashboard/register/',
        '/organizations/register/',
        '/organizations/subscription/',
        '/users/verify-email/',
        '/users/resend-verification/',
        '/users/verification/',
        '/users/subscription/',  # Checkout y procesamiento de pagos
        '/users/payment-methods/',
        '/users/webhooks/',  # Webhook de Wompi
        '/static/',
        '/media/',
        '/',  # Página de inicio pública
        '/agendar/',  # Página de booking pública
        '/tienda/',  # Página de tienda pública
    ]
    
    def process_request(self, request):
        # Si el usuario no está autenticado, no verificar suscripción
        if not request.user.is_authenticated:
            return None
        
        # Los superusuarios tienen acceso sin restricciones
        if request.user.is_superuser:
            return None
        
        # Verificar si la URL está exenta
        for exempt_url in self.EXEMPT_URLS:
            if request.path.startswith(exempt_url):
                return None
        
        # Verificar si el usuario tiene suscripción activa
        try:
            from apps.users.models import UserSubscription
            user_subscription = UserSubscription.objects.get(user=request.user)
            
            # Si la suscripción no está pagada Y NO es plan gratuito, redirigir al checkout
            if user_subscription.payment_status == 'pending' and user_subscription.plan.plan_type != 'free':
                # Permitir acceso solo al checkout y rutas de pago
                if not request.path.startswith('/users/subscription/') and not request.path.startswith('/users/payment-methods/'):
                    return redirect('users:subscription_checkout', plan_id=user_subscription.plan.id)
            
            # Si la suscripción ha expirado o no está activa
            if not user_subscription.is_active or user_subscription.is_expired:
                if request.path != reverse('organizations:subscription_expired'):
                    return redirect('organizations:subscription_expired')
        except UserSubscription.DoesNotExist:
            # Si no tiene suscripción, redirigir a seleccionar plan
            if request.path != reverse('organizations:subscription_plans'):
                return redirect('organizations:subscription_plans')
        
        return None


class PlanLimitsMiddleware(MiddlewareMixin):
    """
    Middleware que verifica los límites del plan de suscripción
    y adjunta información del plan al request
    """
    
    # URLs que no requieren verificación
    EXEMPT_URLS = [
        '/admin/',
        '/saas-admin/',
        '/accounts/login/',
        '/accounts/logout/',
        '/media/',
        '/static/',
        '/upgrade/',
        '/checkout/',
        '/pricing/',
        '/organizations/register/',
    ]
    
    def process_request(self, request):
        """Procesa cada request para adjuntar info del plan"""
        
        # Saltar verificación para URLs exentas
        if any(request.path.startswith(url) for url in self.EXEMPT_URLS):
            return None
        
        # Solo verificar para usuarios autenticados
        if not request.user.is_authenticated:
            return None
        
        # Superusuarios tienen acceso completo
        if request.user.is_superuser:
            return None
        
        # Obtener suscripción del usuario
        subscription = self._get_user_subscription(request)
        
        if subscription:
            # Guardar info en request para uso posterior
            request.subscription = subscription
            request.plan = subscription.plan
        
        return None
    
    def _get_user_subscription(self, request):
        """Obtiene la suscripción activa del usuario"""
        try:
            from apps.users.models import UserSubscription
            return UserSubscription.objects.filter(
                user=request.user,
                is_active=True
            ).select_related('plan').first()
        except:
            return None


class PlanFeatureMiddleware(MiddlewareMixin):
    """
    Middleware que verifica si el plan del usuario incluye
    características/módulos específicos antes de permitir acceso
    """
    
    # Mapeo de URLs a características requeridas (feature codes)
    FEATURE_REQUIREMENTS = {
        '/api/': 'api_access',
        '/analytics/': 'analytics_advanced',
        '/whatsapp/': 'whatsapp_integration',
        '/branding/': 'custom_branding',
        '/integrations/': 'integrations_access',
        '/reports/advanced/': 'advanced_reports',
        '/multi-location/': 'multi_location_support',
        '/inventory/advanced/': 'inventory_management',
        '/patients/export/': 'data_export',
        '/marketing/': 'marketing_tools',
        '/billing/invoices/': 'electronic_invoicing',
    }
    
    # URLs exentas
    EXEMPT_URLS = [
        '/admin/',
        '/saas-admin/',
        '/accounts/',
        '/media/',
        '/static/',
        '/upgrade/',
        '/pricing/',
        '/organizations/register/',
    ]
    
    def process_request(self, request):
        """Verifica si el usuario tiene acceso a la característica"""
        
        # Saltar verificación para URLs exentas
        if any(request.path.startswith(url) for url in self.EXEMPT_URLS):
            return None
        
        # Solo verificar para usuarios autenticados
        if not request.user.is_authenticated:
            return None
        
        # Superusuarios tienen acceso completo
        if request.user.is_superuser:
            return None
        
        # Verificar si la URL requiere una característica específica
        required_feature = self._get_required_feature(request.path)
        
        if not required_feature:
            return None
        
        # Obtener el plan del usuario
        plan = getattr(request, 'plan', None)
        
        if not plan:
            return None
        
        # Verificar si el plan incluye la característica
        has_feature = self._check_feature_access(plan, required_feature)
        
        if not has_feature:
            # Bloquear acceso y mostrar mensaje
            from django.contrib import messages
            feature_name = self._get_feature_display_name(required_feature)
            messages.warning(
                request,
                f'🔒 La característica "{feature_name}" no está disponible en tu plan actual. '
                f'Actualiza tu plan para desbloquearla.'
            )
            return redirect(reverse('dashboard:home'))
        
        return None
    
    def _get_required_feature(self, path):
        """Obtiene la característica requerida para una URL"""
        for url_pattern, feature_code in self.FEATURE_REQUIREMENTS.items():
            if path.startswith(url_pattern):
                return feature_code
        return None
    
    def _check_feature_access(self, plan, feature_code):
        """Verifica si el plan tiene acceso a una característica"""
        
        # Mapeo de feature codes a campos booleanos del plan
        legacy_features = {
            'api_access': plan.api_access,
            'whatsapp_integration': plan.whatsapp_integration,
            'custom_branding': plan.custom_branding,
            'analytics_advanced': plan.analytics,
            'multi_location_support': plan.multi_location,
            'electronic_invoicing': plan.allow_electronic_invoicing,
        }
        
        # Verificar campo booleano legacy primero
        if feature_code in legacy_features:
            if legacy_features[feature_code]:
                return True
        
        # Verificar en PlanFeatures (M2M)
        return plan.has_feature(feature_code)
    
    def _get_feature_display_name(self, feature_code):
        """Retorna el nombre visible de una característica"""
        feature_names = {
            'api_access': 'Acceso API',
            'analytics_advanced': 'Analytics Avanzado',
            'whatsapp_integration': 'Integración WhatsApp',
            'custom_branding': 'Marca Personalizada',
            'integrations_access': 'Integraciones',
            'advanced_reports': 'Reportes Avanzados',
            'multi_location_support': 'Múltiples Ubicaciones',
            'inventory_management': 'Gestión de Inventario Avanzada',
            'data_export': 'Exportación de Datos',
            'marketing_tools': 'Herramientas de Marketing',
            'electronic_invoicing': 'Facturación Electrónica DIAN',
        }
        return feature_names.get(feature_code, feature_code.replace('_', ' ').title())


class LimitEnforcementMiddleware(MiddlewareMixin):
    """
    Middleware que previene la creación de recursos que excedan los límites del plan
    """
    
    # Mapeo de URLs de creación a tipos de límite
    LIMIT_URLS = {
        '/users/create/': 'users',
        '/patients/create/': 'patients',
        '/patients/add/': 'patients',
        '/appointments/create/': 'appointments',
        '/appointments/add/': 'appointments',
        '/organizations/create/': 'organizations',
        '/billing/invoices/create/': 'invoices',
    }
    
    def process_request(self, request):
        """Verifica límites antes de crear nuevos recursos"""
        
        # Solo verificar en POST (creación)
        if request.method != 'POST':
            return None
        
        # Solo para usuarios autenticados no superusuarios
        if not request.user.is_authenticated or request.user.is_superuser:
            return None
        
        # Verificar si la URL es de creación
        limit_type = self._get_limit_type(request.path)
        
        if not limit_type:
            return None
        
        # Obtener plan y organización
        plan = getattr(request, 'plan', None)
        organization = getattr(request, 'organization', None)
        
        if not plan:
            return None
        
        # Para organizaciones, usar el usuario como referencia
        if limit_type == 'organizations':
            current_count = Organization.objects.filter(owner=request.user).count()
        elif organization:
            current_count = self._get_current_count(organization, limit_type)
        else:
            return None
        
        # Verificar límite
        limit_reached, max_allowed = plan.check_limit_reached(limit_type, current_count)
        
        if limit_reached:
            from django.contrib import messages
            limit_name = self._get_limit_display_name(limit_type)
            messages.error(
                request,
                f'⚠️ Has alcanzado el límite de {limit_name} de tu plan ({max_allowed}). '
                f'Actualiza tu plan para crear más.'
            )
            # Redirigir a la página anterior
            return redirect(request.META.get('HTTP_REFERER', '/'))
        
        return None
    
    def _get_limit_type(self, path):
        """Obtiene el tipo de límite para una URL"""
        for url_pattern, limit_type in self.LIMIT_URLS.items():
            if url_pattern in path:
                return limit_type
        return None
    
    def _get_current_count(self, organization, limit_type):
        """Obtiene el conteo actual de un recurso"""
        from datetime import datetime
        
        counts = {
            'users': OrganizationMember.objects.filter(organization=organization, is_active=True).count(),
        }
        
        # Importar modelos según se necesiten
        try:
            from apps.patients.models import Patient
            counts['patients'] = Patient.objects.filter(organization=organization).count()
        except:
            counts['patients'] = 0
        
        # Citas del mes actual
        if limit_type == 'appointments':
            try:
                from apps.appointments.models import Appointment
                now = datetime.now()
                start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                counts['appointments'] = Appointment.objects.filter(
                    organization=organization,
                    appointment_date__gte=start_of_month
                ).count()
            except:
                counts['appointments'] = 0
        
        # Facturas del mes actual
        if limit_type == 'invoices':
            try:
                from apps.billing.models import Invoice
                now = datetime.now()
                start_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
                counts['invoices'] = Invoice.objects.filter(
                    organization=organization,
                    created_at__gte=start_of_month
                ).count()
            except:
                counts['invoices'] = 0
        
        return counts.get(limit_type, 0)
    
    def _get_limit_display_name(self, limit_type):
        """Retorna el nombre visible del límite"""
        names = {
            'users': 'usuarios',
            'patients': 'pacientes',
            'appointments': 'citas este mes',
            'organizations': 'organizaciones',
            'invoices': 'facturas este mes',
        }
        return names.get(limit_type, limit_type)
