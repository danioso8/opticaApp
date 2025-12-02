from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    # Dashboard principal
    path('', views.admin_dashboard_home, name='home'),
    
    # Gestión de usuarios
    path('users/', views.users_list, name='users_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:user_id>/unlimited/', views.subscription_unlimited, name='subscription_unlimited'),
    path('users/<int:user_id>/revoke-unlimited/', views.subscription_revoke_unlimited, name='subscription_revoke_unlimited'),
    
    # Gestión de suscripciones
    path('subscriptions/', views.subscriptions_list, name='subscriptions_list'),
    path('subscriptions/<int:subscription_id>/edit/', views.subscription_edit, name='subscription_edit'),
    
    # Gestión de organizaciones
    path('organizations/', views.organizations_list, name='organizations_list'),
    path('organizations/<int:org_id>/', views.organization_detail, name='organization_detail'),
    path('organizations/<int:org_id>/toggle-active/', views.organization_toggle_active, name='organization_toggle_active'),
    path('organizations/<int:org_id>/delete/', views.organization_delete, name='organization_delete'),
    
    # Gestión de planes
    path('plans/', views.plans_list, name='plans_list'),
    path('plans/create/', views.plan_create, name='plan_create'),
    path('plans/<int:plan_id>/edit/', views.plan_edit, name='plan_edit'),
    path('plans/<int:plan_id>/toggle-active/', views.plan_toggle_active, name='plan_toggle_active'),
]
