from django.urls import path
from . import views

app_name = 'public'

urlpatterns = [
    path('', views.home, name='home'),
    path('agendar/', views.booking, name='booking'),
    path('tienda/', views.shop, name='shop'),
    # Rutas específicas de organización (deben ir antes de la ruta genérica)
    path('<slug:org_slug>/agendar/', views.booking, name='booking_org'),
    # Landing page pública por slug de organización
    path('<slug:org_slug>/', views.organization_landing, name='organization_landing'),
]
