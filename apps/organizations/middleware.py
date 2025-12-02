from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from .models import Organization, OrganizationMember


class TenantMiddleware(MiddlewareMixin):
    """
    Middleware que identifica y establece la organización (tenant) actual
    basándose en el subdominio o en la sesión del usuario
    """
    
    def process_request(self, request):
        # Inicializar el tenant en None
        request.organization = None
        request.tenant = None
        
        # Si el usuario no está autenticado, no hay tenant
        if not request.user.is_authenticated:
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
    Middleware que verifica que la organización tenga una suscripción activa
    """
    
    # URLs que no requieren suscripción activa
    EXEMPT_URLS = [
        '/admin/',
        '/accounts/login/',
        '/accounts/logout/',
        '/subscription/expired/',
        '/subscription/plans/',
        '/subscription/checkout/',
    ]
    
    def process_request(self, request):
        # Si no hay organización, no verificar suscripción
        if not hasattr(request, 'organization') or not request.organization:
            return None
        
        # Verificar si la URL está exenta
        for exempt_url in self.EXEMPT_URLS:
            if request.path.startswith(exempt_url):
                return None
        
        # Verificar si la organización tiene suscripción activa
        organization = request.organization
        
        if not organization.is_subscription_active:
            # Redirigir a página de suscripción expirada
            if request.path != reverse('subscription_expired'):
                return redirect('subscription_expired')
        
        return None
