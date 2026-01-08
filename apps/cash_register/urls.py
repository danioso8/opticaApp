from django.urls import path
from . import views

app_name = 'cash_register'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Cajas Registradoras
    path('registers/', views.cash_register_list, name='register_list'),
    path('registers/create/', views.create_cash_register, name='create_register'),
    path('registers/<int:pk>/', views.cash_register_detail, name='detail'),
    path('registers/<int:pk>/open/', views.open_cash_register, name='open'),
    path('registers/<int:pk>/close/', views.close_cash_register, name='close'),
    
    # Movimientos
    path('movements/', views.movement_list, name='movement_list'),
    path('movements/create/', views.create_movement, name='movement_create'),
    
    # Cierres
    path('closures/', views.closure_list, name='closure_list'),
    path('closures/<int:pk>/', views.closure_detail, name='closure_detail'),
    path('closures/<int:pk>/approve/', views.approve_closure, name='approve_closure'),
    path('closures/<int:pk>/reject/', views.reject_closure, name='reject_closure'),
    
    # Reportes
    path('reports/', views.reports, name='reports'),
    
    # API Endpoints
    path('api/registers/<int:pk>/summary/', views.api_cash_register_summary, name='api_summary'),
    path('api/daily-report/', views.api_daily_report, name='api_daily_report'),
    
    # Categorías (AJAX)
    path('api/categories/create/', views.create_category_ajax, name='create_category_ajax'),
    path('api/categories/', views.get_categories_ajax, name='get_categories_ajax'),
]
