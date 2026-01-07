from django.urls import path
from apps.inventory import views

app_name = 'inventory'

urlpatterns = [
    # Dashboard
    path('', views.inventory_dashboard, name='dashboard'),
    
    # Movimientos
    path('movements/', views.movement_list, name='movement_list'),
    path('movements/create/', views.movement_create, name='movement_create'),
    path('kardex/<int:product_id>/', views.product_kardex, name='product_kardex'),
    
    # Lotes
    path('lots/', views.lot_list, name='lot_list'),
    path('lots/create/', views.lot_create, name='lot_create'),
    
    # Alertas
    path('alerts/', views.alert_list, name='alert_list'),
    path('alerts/<int:alert_id>/resolve/', views.alert_resolve, name='alert_resolve'),
    
    # Ajustes
    path('adjustments/', views.adjustment_list, name='adjustment_list'),
    path('adjustments/create/', views.adjustment_create, name='adjustment_create'),
    path('adjustments/<int:adjustment_id>/approve/', views.adjustment_approve, name='adjustment_approve'),
    path('adjustments/<int:adjustment_id>/reject/', views.adjustment_reject, name='adjustment_reject'),
    
    # API
    path('api/product/<int:product_id>/', views.get_product_info, name='get_product_info'),
    path('api/product/<int:product_id>/lots/', views.get_product_lots, name='get_product_lots'),
]
