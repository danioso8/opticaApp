"""config URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Admin Dashboard URLs (SaaS Management)
    path('saas-admin/', include('apps.admin_dashboard.urls')),
    
    # Organizations URLs
    path('organizations/', include('apps.organizations.urls')),
    
    # Users URLs (Payments & Subscriptions)
    path('users/', include('apps.users.urls')),
    
    # Dashboard URLs
    path('dashboard/', include('apps.dashboard.urls')),
    
    # Billing URLs (Facturación Electrónica DIAN)
    path('dashboard/billing/', include('apps.billing.urls')),
    
    # Payroll URLs (Nómina Electrónica DIAN)
    path('dashboard/payroll/', include('apps.payroll.urls')),
    
    # Sales URLs
    path('dashboard/sales/', include('apps.sales.urls')),
    
    # Inventory URLs
    path('dashboard/inventory/', include('apps.inventory.urls')),
    
    # Cash Register URLs (Caja/Tesorería)
    path('dashboard/cash/', include('apps.cash_register.urls')),
    
    # API URLs
    path('api/', include('apps.appointments.urls')),
    
    # Public URLs
    path('', include('apps.public.urls')),
]

# Servir archivos media en desarrollo Y producción
# En producción con Daphne, necesitamos servir archivos media explícitamente
from django.views.static import serve
from django.urls import re_path

urlpatterns += [
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
]

# En desarrollo también servir archivos estáticos
if settings.DEBUG:
    urlpatterns += [
        re_path(r'^static/(?P<path>.*)$', serve, {
            'document_root': settings.STATIC_ROOT,
        }),
    ]
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
