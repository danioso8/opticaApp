"""
URLs para Testing App
"""
from django.urls import path
from . import views

app_name = 'testing'

urlpatterns = [
    path('', views.test_bot_list, name='bot_list'),
    path('create/', views.test_bot_create, name='bot_create'),
    path('<int:bot_id>/', views.test_bot_detail, name='bot_detail'),
    path('<int:bot_id>/run/', views.test_bot_run, name='bot_run'),
    path('<int:bot_id>/toggle/', views.test_bot_toggle, name='bot_toggle'),
    path('run/<int:run_id>/', views.test_run_detail, name='run_detail'),
]
