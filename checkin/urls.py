from django.urls import path
from . import views

urlpatterns = [
    # Check-in URLs
    path('', views.checkin_dashboard, name='checkin-dashboard'),
    path('list/', views.checkin_list, name='checkin-list'),
    path('create/', views.checkin_create, name='checkin-create'),  # Redirects to enhanced
    path('legacy-create/', views.checkin_create_legacy, name='checkin-create-legacy'),  # Original form
    path('enhanced-create/', views.enhanced_checkin_create, name='enhanced-checkin-create'),
    path('quick/', views.quick_checkin, name='quick-checkin'),
    path('from-booking/<int:booking_id>/', views.checkin_from_booking, name='checkin-from-booking'),
    path('<int:checkin_id>/', views.checkin_detail, name='checkin-detail'),
    path('<int:checkin_id>/edit/', views.checkin_update, name='checkin-update'),
    path('<int:checkin_id>/enhanced-edit/', views.enhanced_checkin_update, name='enhanced-checkin-update'),
    path('<int:checkin_id>/verify-id/', views.verify_id_proof, name='checkin-verify-id'),
    path('<int:checkin_id>/update-payment/', views.update_payment_status, name='checkin-update-payment'),
    
    # API endpoints
    #path('api/guest-search/', views.guest_search_api, name='guest-search-api'),
    path('ajax/guest-search/', views.guest_search, name='guest-search'),
    path('api/save-guest/', views.save_guest_data_api, name='save-guest-api'),
    path('debug/guest-count/', views.debug_guest_count, name='debug-guest-count'),
]