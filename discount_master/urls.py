
from django.urls import path
from . import views

urlpatterns = [
    path('', views.discount_list, name='discount_list'),
    path('create/', views.discount_create, name='discount_create'),
    path('<int:pk>/update/', views.discount_update, name='discount_update'),
    path('<int:pk>/delete/', views.discount_delete, name='discount_delete'),
    path('<int:pk>/', views.discount_detail, name='discount_detail'),
]