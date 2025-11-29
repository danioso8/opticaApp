from django.urls import path
from . import views

app_name = 'sales'

urlpatterns = [
    # Dashboard de ventas
    path('', views.sales_dashboard, name='dashboard'),
    path('new/', views.new_sale, name='new_sale'),
    path('<int:pk>/', views.sale_detail, name='sale_detail'),
    
    # API endpoints para gráficos
    path('api/daily-stats/', views.daily_stats_api, name='daily_stats_api'),
    path('api/weekly-stats/', views.weekly_stats_api, name='weekly_stats_api'),
    path('api/monthly-stats/', views.monthly_stats_api, name='monthly_stats_api'),
    path('api/top-products/', views.top_products_api, name='top_products_api'),
]
