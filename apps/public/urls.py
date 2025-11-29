from django.urls import path
from . import views

app_name = 'public'

urlpatterns = [
    path('', views.home, name='home'),
    path('agendar/', views.booking, name='booking'),
    path('tienda/', views.shop, name='shop'),
]
