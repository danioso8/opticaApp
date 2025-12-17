# URLs para el módulo de facturación
from django.urls import path
from . import views

app_name = 'billing'

urlpatterns = [
    # Configuración DIAN
    path('dian/config/', views.dian_configuration_view, name='dian_configuration'),
    path('dian-config/', views.dian_configuration_view, name='dian_config'),  # Alias
    
    # Facturas
    path('invoices/', views.invoice_list, name='invoice_list'),
    path('invoices/create/', views.invoice_create, name='invoice_create'),
    path('invoices/<int:invoice_id>/', views.invoice_detail, name='invoice_detail'),
    path('invoices/<int:invoice_id>/pdf/', views.invoice_pdf, name='invoice_pdf'),
    path('invoices/<int:invoice_id>/register-payment/', views.register_payment, name='register_payment'),
    
    # Proveedores (Suppliers)
    path('suppliers/', views.supplier_list, name='supplier_list'),
    path('suppliers/create/', views.supplier_create, name='supplier_create'),
    path('suppliers/<int:supplier_id>/edit/', views.supplier_edit, name='supplier_edit'),
    path('suppliers/<int:supplier_id>/delete/', views.supplier_delete, name='supplier_delete'),
    path('suppliers/categoria/create/', views.supplier_categoria_create, name='supplier_categoria_create'),
    path('suppliers/ajax/create/', views.supplier_create_ajax, name='supplier_create_ajax'),
    
    # Productos (Products)
    path('products/', views.product_list, name='product_list'),
    path('products/create/', views.product_create, name='product_create'),
    path('products/<int:product_id>/edit/', views.product_edit, name='product_edit'),
    path('products/<int:product_id>/delete/', views.product_delete, name='product_delete'),
    path('products/ajax/create/', views.product_create_ajax, name='product_create_ajax'),
    
    # Configuración de Facturación
    path('config/', views.invoice_config, name='invoice_config'),
]
