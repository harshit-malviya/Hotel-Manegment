from django.urls import path
from . import views

app_name = 'timemaster'

urlpatterns = [
    path('time-entry/', views.time_entry_view, name='time_entry'),
]