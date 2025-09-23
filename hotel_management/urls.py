"""
URL configuration for hotel_management project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('rooms/', include('rooms.urls')),
    path('amenities/', include('amenities.urls')),
    path('guests/', include('guest.urls')),
    path('bookings/', include('booking.urls')),
    path('rates/', include('rate.urls')),
    path('services/', include('service.urls')),
    path('housekeeping/', include('housekeeping.urls')),
    path('checkin/', include('checkin.urls')),
    path('', include('dashboard.urls')),  # Default to dashboard home
    path('timeslotmaster/', include('timeslotmaster.urls')),
    path('discount_master/', include('discount_master.urls')),
    path('reservation-sources/', include('reservation_source_master.urls')),
    path('booking_master/', include('booking_master.urls')),
]

# Serve media files during development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
