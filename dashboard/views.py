from django.shortcuts import render
from django.db.models import Count, Sum, Avg, Q
from django.utils import timezone
from datetime import date, timedelta
from decimal import Decimal
from booking_master.models import Booking
from rooms.models import Room
from guest.models import Guest
from rate.models import RatePlan

def dashboard_home(request):
    """Dashboard home view with KPIs"""
    today = date.today()
    
    # Date ranges for calculations
    this_month_start = today.replace(day=1)
    
    # Room Statistics
    total_rooms = Room.objects.count()
    available_rooms = Room.objects.filter(status='AVAILABLE').count()
    occupied_rooms = Room.objects.filter(status='OCCUPIED').count()
    maintenance_rooms = Room.objects.filter(status='MAINTENANCE').count()
    
    # Occupancy Rate
    occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
    
    # Basic Booking Statistics (using available fields)
    total_bookings = Booking.objects.count()
    todays_bookings = Booking.objects.filter(booking_date=today).count()
    this_month_bookings = Booking.objects.filter(
        booking_date__gte=this_month_start
    ).count()
    
    # Guest Statistics
    total_guests = Guest.objects.count()
    new_guests_this_month = Guest.objects.filter(
        created_at__gte=this_month_start
    ).count()
    
    # Recent bookings for quick overview (using available fields)
    recent_bookings = Booking.objects.select_related('room_type').order_by('-booking_date', '-booking_time')[:5]
    
    # Room type booking distribution
    room_type_stats = Room.objects.values('room_type__name').annotate(
        total=Count('id'),
        occupied=Count('id', filter=Q(status='OCCUPIED')),
        available=Count('id', filter=Q(status='AVAILABLE'))
    ).order_by('room_type__name')
    
    context = {
        # Room KPIs
        'total_rooms': total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms': occupied_rooms,
        'maintenance_rooms': maintenance_rooms,
        'occupancy_rate': round(occupancy_rate, 1),
        
        # Booking KPIs (simplified to match available fields)
        'total_bookings': total_bookings,
        'todays_bookings': todays_bookings,
        'this_month_bookings': this_month_bookings,
        
        # Guest KPIs
        'total_guests': total_guests,
        'new_guests_this_month': new_guests_this_month,
        
        # Data for charts and tables
        'recent_bookings': recent_bookings,
        'room_type_stats': room_type_stats,
        
        # Date context
        'today': today,
        'current_month': today.strftime('%B %Y'),
    }
    
    return render(request, 'dashboard/home.html', context)