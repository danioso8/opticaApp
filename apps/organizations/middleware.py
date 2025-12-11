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
