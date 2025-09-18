from django.urls import path
from . import views

urlpatterns = [
    path('', views.timeslot_list, name='timeslot_list'),
    path('create/', views.timeslot_create, name='timeslot_create'),
    path('<int:pk>/', views.timeslot_detail, name='timeslot_detail'),
    path('<int:pk>/update/', views.timeslot_update, name='timeslot_update'),
    path('<int:pk>/delete/', views.timeslot_delete, name='timeslot_delete'),
]
