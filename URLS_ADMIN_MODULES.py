# -*- coding: utf-8 -*-
"""
URLs adicionales para admin dashboard de módulos SAAS
"""
from django.urls import path
from apps.admin_dashboard import views_modules

# Estas URLs se agregan al apps/admin_dashboard/urls.py existente

saas_admin_urls = [
    # Dashboard principal de módulos
    path('modules/dashboard/', views_modules.modules_dashboard, name='modules_dashboard'),
    
    # Gestión
    path('modules/management/', views_modules.modules_management, name='modules_management'),
    path('modules/pricing/', views_modules.module_pricing_config, name='module_pricing_config'),
    
    # Trials
    path('modules/trials/', views_modules.trials_dashboard, name='trials_dashboard'),
    path('modules/trials/<int:trial_id>/', views_modules.trial_detail, name='trial_detail'),
    
    # Analytics
    path('modules/analytics/', views_modules.conversion_analytics, name='conversion_analytics'),
    path('modules/notifications/', views_modules.notifications_log, name='notifications_log'),
    
    # AJAX APIs
    path('modules/api/update-price/<int:module_id>/', views_modules.update_module_price, name='update_module_price'),
    path('modules/api/toggle-status/<int:module_id>/', views_modules.toggle_module_status, name='toggle_module_status'),
]
