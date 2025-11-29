from django.urls import path, include
from rest_framework.routers import DefaultRouter
from . import views

router = DefaultRouter()
router.register(r'appointments', views.AppointmentViewSet, basename='appointment')

urlpatterns = [
    # URLs del router
    path('', include(router.urls)),
    
    # APIs públicas (landing page)
    path('available-dates/', views.available_dates, name='available-dates'),
    path('available-slots/', views.available_slots, name='available-slots'),
    path('book/', views.book_appointment, name='book-appointment'),
    
    # APIs administrativas
    path('configuration/', views.configuration, name='configuration'),
    path('toggle-system/', views.toggle_system, name='toggle-system'),
    path('block-date/', views.block_date, name='block-date'),
    path('block-slot/', views.block_slot, name='block-slot'),
]
