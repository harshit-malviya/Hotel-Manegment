from django.urls import path
from . import views

urlpatterns = [
    path('create/', views.create_booking, name='create_booking'),
    path('success/', views.booking_success, name='booking_success'),
    path('ajax/get_time_slots/', views.get_time_slots, name='get_time_slots'),
    path('ajax/get_price/', views.get_price, name='get_price'),
]
