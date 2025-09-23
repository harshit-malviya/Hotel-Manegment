from django.urls import path
from . import views
from . import corporate_agent_views

urlpatterns = [
    # Booking URLs
    path('', views.booking_list, name='booking-list'),
    path('create/', views.booking_create, name='booking-create'),
    path('search/', views.room_availability_search, name='room-availability-search'),
    path('calculate-amount/', views.calculate_booking_amount, name='calculate-booking-amount'),
    path('api/reservation-sources/', views.reservation_sources_api, name='reservation-sources-api'),
    path('api/rooms-by-type/', views.get_available_rooms_by_type, name='rooms-by-type-api'),
    path('<int:booking_id>/', views.booking_detail, name='booking-detail'),
    path('<int:booking_id>/edit/', views.booking_update, name='booking-update'),
    path('<int:booking_id>/delete/', views.booking_delete, name='booking-delete'),
    path('<int:booking_id>/check-in/', views.booking_check_in, name='booking-check-in'),
    path('<int:booking_id>/check-out/', views.booking_check_out, name='booking-check-out'),
    path('<int:booking_id>/cancel/', views.booking_cancel, name='booking-cancel'),
    
    # Corporate/Agent URLs
    path('corporate-agents/', corporate_agent_views.corporate_agent_list, name='corporate-agent-list'),
    path('corporate-agents/create/', corporate_agent_views.corporate_agent_create, name='corporate-agent-create'),
    path('corporate-agents/<int:agent_id>/', corporate_agent_views.corporate_agent_detail, name='corporate-agent-detail'),
    path('corporate-agents/<int:agent_id>/edit/', corporate_agent_views.corporate_agent_update, name='corporate-agent-update'),
    path('corporate-agents/<int:agent_id>/delete/', corporate_agent_views.corporate_agent_delete, name='corporate-agent-delete'),
]