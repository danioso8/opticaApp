"""
URLs para el módulo de promociones
"""
from django.urls import path
from apps.promotions import views

app_name = 'promotions'

urlpatterns = [
    # Promociones
    path('', views.promotion_list, name='promotion_list'),
    path('crear/', views.promotion_create, name='promotion_create'),
    path('<int:promotion_id>/editar/', views.promotion_edit, name='promotion_edit'),
    path('<int:promotion_id>/eliminar/', views.promotion_delete, name='promotion_delete'),
    
    # Campañas
    path('campanas/', views.campaign_list, name='campaign_list'),
    path('campanas/crear/', views.campaign_create, name='campaign_create'),
    path('campanas/<int:campaign_id>/', views.campaign_detail, name='campaign_detail'),
    path('campanas/<int:campaign_id>/iniciar/', views.campaign_start, name='campaign_start'),
    path('campanas/<int:campaign_id>/pausar/', views.campaign_pause, name='campaign_pause'),
    path('campanas/<int:campaign_id>/reanudar/', views.campaign_resume, name='campaign_resume'),
    path('campanas/<int:campaign_id>/enviar-lote/', views.campaign_send_batch, name='campaign_send_batch'),
    
    # API
    path('campanas/<int:campaign_id>/stats/', views.campaign_stats_json, name='campaign_stats_json'),
]
