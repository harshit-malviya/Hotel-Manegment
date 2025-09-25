from django.urls import path
from . import views

urlpatterns = [
    path('', views.reservation_source_list, name='reservation-source-list'),
    path('create/', views.reservation_source_create, name='reservation-source-create'),
    path('<int:source_id>/', views.reservation_source_detail, name='reservation-source-detail'),
    path('<int:source_id>/edit/', views.reservation_source_update, name='reservation-source-update'),
    path('<int:source_id>/delete/', views.reservation_source_delete, name='reservation-source-delete'),
]