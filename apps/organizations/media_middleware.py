"""
Middleware para servir archivos de medios en desarrollo con Daphne/ASGI
"""
import os
from django.conf import settings
from django.http import FileResponse, Http404, HttpResponseRedirect
from django.utils.deprecation import MiddlewareMixin


class MediaFileMiddleware(MiddlewareMixin):
    """
    Middleware para servir archivos de media en desarrollo cuando se usa Daphne/ASGI
    Solo se activa si DEBUG=True
    Si el archivo no existe localmente, intenta usar la URL de producción (Render)
    """
    
    def process_request(self, request):
        if not settings.DEBUG:
            return None
        
        # Solo procesar URLs que empiecen con MEDIA_URL
        if not request.path.startswith(settings.MEDIA_URL):
            return None
        
        # Obtener la ruta relativa del archivo
        relative_path = request.path[len(settings.MEDIA_URL):]
        
        # Construir la ruta completa
        file_path = os.path.join(settings.MEDIA_ROOT, relative_path)
        
        # Si el archivo existe localmente, servirlo
        if os.path.exists(file_path) and os.path.isfile(file_path):
            return FileResponse(open(file_path, 'rb'))
        
        # Si no existe localmente, usar placeholder o URL de producción
        # Puedes configurar la URL de producción en settings
        production_media_url = getattr(settings, 'PRODUCTION_MEDIA_URL', None)
        
        if production_media_url:
            # Redirigir a la URL de producción
            production_url = f"{production_media_url.rstrip('/')}/{relative_path}"
            return HttpResponseRedirect(production_url)
        
        # Si no hay URL de producción configurada, devolver 404
        raise Http404(f"Archivo no encontrado localmente: {relative_path}. Configura PRODUCTION_MEDIA_URL en settings.py o sube el archivo.")
