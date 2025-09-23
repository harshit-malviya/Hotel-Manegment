from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_booking, name='create_booking'),
    path('success/', views.booking_success, name='booking_success'),
]
