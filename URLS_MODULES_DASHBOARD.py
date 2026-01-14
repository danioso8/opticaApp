# -*- coding: utf-8 -*-
"""
URLs adicionales para dashboard de módulos
"""
from django.urls import path
from apps.dashboard import views_modules

# Estas URLs se agregan al apps/dashboard/urls.py existente

module_urls = [
    # Marketplace y Selector
    path('modules/marketplace/', views_modules.module_marketplace, name='module_marketplace'),
    path('modules/my-plan/', views_modules.my_plan, name='my_plan'),
    path('modules/selector/', views_modules.module_selector, name='module_selector'),
    path('modules/checkout/', views_modules.module_checkout, name='module_checkout'),
    
    # API
    path('modules/api/calculate-price/', views_modules.calculate_price, name='calculate_price'),
    
    # Acciones
    path('modules/<int:module_id>/add/', views_modules.add_module, name='add_module'),
    path('modules/<int:module_id>/remove/', views_modules.remove_module, name='remove_module'),
]
