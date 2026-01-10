from django.urls import path
from . import views

app_name = 'admin_dashboard'

urlpatterns = [
    # Autenticación
    path('login/', views.saas_admin_login, name='login'),
    path('logout/', views.saas_admin_logout, name='logout'),
    
    # Dashboard principal
    path('', views.admin_dashboard_home, name='home'),
    
    # Gestión de usuarios
    path('users/', views.users_list, name='users_list'),
    path('users/<int:user_id>/', views.user_detail, name='user_detail'),
    path('users/<int:user_id>/toggle-active/', views.user_toggle_active, name='user_toggle_active'),
    path('users/<int:user_id>/delete/', views.user_delete, name='user_delete'),
    path('users/<int:user_id>/unlimited/', views.subscription_unlimited, name='subscription_unlimited'),
    path('users/<int:user_id>/revoke-unlimited/', views.subscription_revoke_unlimited, name='subscription_revoke_unlimited'),
    path('users/<int:user_id>/verify-email/', views.verify_user_email, name='verify_user_email'),
    path('users/<int:user_id>/unverify-email/', views.unverify_user_email, name='unverify_user_email'),
    
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
    path('plans/<int:plan_id>/delete/', views.plan_delete, name='plan_delete'),
    
    # Gestión de módulos/características
    path('features/', views.features_list, name='features_list'),
    path('features/create/', views.feature_create, name='feature_create'),
    path('features/<int:feature_id>/edit/', views.feature_edit, name='feature_edit'),
    path('features/<int:feature_id>/delete/', views.feature_delete, name='feature_delete'),
    
    # Gestión de módulos por organización
    path('organizations/<int:org_id>/features/', views.organization_features, name='organization_features'),
    path('organizations/<int:org_id>/features/toggle/', views.organization_feature_toggle, name='organization_feature_toggle'),
    path('organizations/<int:org_id>/features/sync/', views.organization_sync_plan_features, name='organization_sync_plan_features'),
    
    # Gestión de paquetes de facturas
    path('invoice-packages/', views.invoice_packages_list, name='invoice_packages_list'),
    path('organizations/<int:org_id>/invoice-packages/create/', views.invoice_package_create, name='invoice_package_create'),
    
    # Gestión de compras de módulos adicionales
    path('addon-purchases/', views.addon_purchases_list, name='addon_purchases_list'),
    path('organizations/<int:org_id>/addon-purchases/create/', views.addon_purchase_create, name='addon_purchase_create'),
    
    # Monitoreo de errores
    path('errors/', views.error_monitoring, name='error_monitoring'),
]
