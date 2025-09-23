from django.contrib import admin
from .models import Booking

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('booking_id', 'customer_first_name', 'customer_last_name', 'phone_number', 'booking_date', 'room_type', 'payment_method')
    search_fields = ('booking_id', 'customer_first_name', 'customer_last_name', 'phone_number')
