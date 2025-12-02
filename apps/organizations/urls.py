from django.urls import path
from . import views

app_name = 'organizations'

urlpatterns = [
    path('', views.organization_list, name='list'),
    path('create/', views.organization_create, name='create'),
    path('<int:org_id>/', views.organization_detail, name='detail'),
    path('<int:org_id>/switch/', views.organization_switch, name='switch'),
    path('<int:org_id>/settings/', views.organization_settings, name='settings'),
    path('subscription/plans/', views.subscription_plans, name='subscription_plans'),
    path('subscription/expired/', views.subscription_expired, name='subscription_expired'),
]
