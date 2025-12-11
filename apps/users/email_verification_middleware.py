"""
Middleware para verificar que el usuario tenga su email verificado
"""
from django.shortcuts import redirect
from django.urls import reverse
from django.contrib import messages
from apps.users.email_verification_models import UserProfile


class EmailVerificationMiddleware:
    """
    Middleware que verifica que los usuarios autenticados tengan su email verificado
    antes de acceder a las áreas protegidas
    """
    
    # URLs que NO requieren verificación de email
    EXEMPT_URLS = [
        '/users/verify/',
        '/users/verification/',
        '/users/subscription/',  # Checkout y pagos
        '/users/payment-methods/',
        '/users/webhooks/',
        '/accounts/logout/',
        '/organizations/logout/',
        '/dashboard/logout/',
        '/static/',
        '/media/',
        '/admin/',  # Admin panel no requiere verificación
        '/api/',    # APIs pueden tener su propia lógica
    ]
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Si el usuario está autenticado
        if request.user.is_authenticated:
            # Verificar si la URL está en la lista de excepciones
            path = request.path
            is_exempt = any(path.startswith(exempt) for exempt in self.EXEMPT_URLS)
            
            if not is_exempt:
                # Obtener o crear perfil del usuario
                profile, created = UserProfile.objects.get_or_create(user=request.user)
                
                # Si el email NO está verificado, redirigir a página de verificación
                if not profile.is_email_verified:
                    # No mostrar mensaje repetidamente si ya está en la página de verificación
                    if path != reverse('users:verification_pending'):
                        # Intentar agregar mensaje solo si el middleware de mensajes ya se ejecutó
                        if hasattr(request, '_messages'):
                            messages.warning(
                                request, 
                                'Debes verificar tu correo electrónico para acceder a esta área.'
                            )
                    return redirect('users:verification_pending')
        
        response = self.get_response(request)
        return response
