# URLs para el módulo de facturación
from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Configuración DIAN
    path('dian/config/', views.dian_configuration_view, name='dian_config'),
    
    # Facturas
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
]

