from django import forms
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q, Count
from django.utils import timezone
from django.http import JsonResponse
from datetime import date, timedelta
from .enhanced_models import CheckIn
from .forms import CheckInForm, CheckInSearchForm, QuickCheckInForm, EnhancedCheckInForm
from booking.models import Booking
from booking.forms import BookingForm
from guest.models import Guest
from rooms.models import Room


class CheckInForm(forms.ModelForm):
    class Meta:
        model = CheckIn
        fields = [
            # ...existing fields...
            'base_tariff',
            'gst_type',
            'cgst_rate',
            'sgst_rate',
            'discount_amount',
        ]

    def clean(self):
        cleaned_data = super().clean()
        # Recalculate final amount before saving
        base_tariff = cleaned_data.get('base_tariff')
        gst_type = cleaned_data.get('gst_type')
        cgst_rate = cleaned_data.get('cgst_rate')
        sgst_rate = cleaned_data.get('sgst_rate')
        discount_amount = cleaned_data.get('discount_amount')

        if all([base_tariff, gst_type, cgst_rate, sgst_rate]):
            # Your calculation logic here
            pass

        return cleaned_data


def checkin_list(request):
    """Display list of all check-ins with search and filter functionality"""
    search_query = request.GET.get('search', '')
    payment_status_filter = request.GET.get('payment_status', '')
    date_range_filter = request.GET.get('date_range', '')
    id_verified_filter = request.GET.get('id_verified', '')

    checkins = CheckIn.objects.select_related('guest', 'room_number', 'booking').all()

    # Apply search filter
    # if search_query:
       # checkins = checkins.filter(
       #     Q(check_in_id__icontains=search_query) |
       #     Q(guest__first_name__icontains=search_query) |
       #     Q(guest__last_name__icontains=search_query) |
       #     Q(room_number__room_number__icontains=search_query) |
       #     Q(assigned_staff__icontains=search_query)
       # )
    
def guest_search(request):
    try:
        q = request.GET.get('q', '').strip()
        
        if len(q) < 2:
            return JsonResponse({'results': [], 'guests': []})
        
        # Search guests by first name, last name, email, or phone number
        guests = Guest.objects.filter(
            Q(first_name__icontains=q) |
            Q(last_name__icontains=q) |
            Q(email__icontains=q) |
            Q(contact_number__icontains=q)
        ).order_by('first_name', 'last_name')[:10]
        
        results = []
        for guest in guests:
            try:
                # Get booking history count
                booking_count = guest.bookings.count()
                last_booking = guest.bookings.order_by('-check_in_date').first()
                
                results.append({
                    'id': guest.guest_id,  # Use the correct primary key field
                    'name': guest.full_name,
                    'full_name': guest.full_name,  # Keep for backward compatibility
                    'email': guest.email,
                    'phone': guest.contact_number,
                    'phone_number': guest.contact_number,  # Keep for backward compatibility
                    'address': guest.address or 'Not provided',
                    'id_proof_type': guest.get_id_proof_type_display() if guest.id_proof_type else 'Not provided',
                    'id_proof_number': guest.id_proof_number or 'Not provided',
                    'gender': guest.get_gender_display() if guest.gender else 'Not specified',
                    'nationality': guest.nationality or 'Not specified',
                    'date_of_birth': guest.date_of_birth.strftime('%d-%m-%Y') if guest.date_of_birth else 'Not provided',
                    'booking_count': booking_count,
                    'last_booking_date': last_booking.check_in_date.strftime('%d-%m-%Y') if last_booking else 'No previous bookings',
                    'display': f"{guest.full_name} - {guest.email} - {guest.contact_number}"
                })
            except Exception as e:
                # Skip problematic guests but continue processing
                print(f"Error processing guest {guest.guest_id}: {e}")
                continue
        
        return JsonResponse({'results': results, 'guests': results})  # Support both formats
    
    except Exception as e:
        # Return error information for debugging
        return JsonResponse({
            'error': str(e),
            'results': [],
            'guests': []
        }, status=500)


def debug_guest_count(request):
    """Debug endpoint to check guest data"""
    try:
        total_guests = Guest.objects.count()
        sample_guests = Guest.objects.all()[:5]
        
        guest_data = []
        for guest in sample_guests:
            guest_data.append({
                'id': guest.guest_id,
                'name': guest.full_name,
                'email': guest.email,
                'phone': guest.contact_number,
            })
        
        return JsonResponse({
            'total_guests': total_guests,
            'sample_guests': guest_data
        })
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)

    # # Apply payment status filter
    # if payment_status_filter:
    #     checkins = checkins.filter(payment_status=payment_status_filter)

    # # Apply ID verification filter
    # if id_verified_filter:
    #     if id_verified_filter == 'true':
    #         checkins = checkins.filter(id_proof_verified=True)
    #     elif id_verified_filter == 'false':
    #         checkins = checkins.filter(id_proof_verified=False)

    # # Apply date range filter
    # if date_range_filter:
    #     today = date.today()
    #     if date_range_filter == 'today':
    #         checkins = checkins.filter(actual_check_in_date_time__date=today)
    #     elif date_range_filter == 'yesterday':
    #         yesterday = today - timedelta(days=1)
    #         checkins = checkins.filter(actual_check_in_date_time__date=yesterday)
    #     elif date_range_filter == 'this_week':
    #         week_start = today - timedelta(days=today.weekday())
    #         checkins = checkins.filter(actual_check_in_date_time__date__gte=week_start)
    #     elif date_range_filter == 'this_month':
    #         month_start = today.replace(day=1)
    #         checkins = checkins.filter(actual_check_in_date_time__date__gte=month_start)

    # # Pagination
    # paginator = Paginator(checkins, 15)
    # page_number = request.GET.get('page')
    # page_obj = paginator.get_page(page_number)

    # context = {
    #     'page_obj': page_obj,
    #     'search_query': search_query,
    #     'payment_status_filter': payment_status_filter,
    #     'date_range_filter': date_range_filter,
    #     'id_verified_filter': id_verified_filter,
    #     'payment_status_choices': CheckIn.PAYMENT_STATUS_CHOICES,
    #     'total_checkins': checkins.count()
    # }
    # return render(request, 'checkin/checkin_list.html', context)


def checkin_detail(request, checkin_id):
    """Display detailed view of a check-in"""
    checkin = get_object_or_404(
        CheckIn.objects.select_related('guest', 'room_number', 'booking'),
        id=checkin_id
    )

    context = {
        'checkin': checkin,
    }
    return render(request, 'checkin/checkin_detail.html', context)


def checkin_create(request):
    """Redirect to enhanced check-in form"""
    # Preserve query parameters when redirecting
    query_params = request.GET.urlencode()
    redirect_url = '/checkin/enhanced-create/'
    if query_params:
        redirect_url += f'?{query_params}'
    return redirect(redirect_url)


def checkin_create_legacy(request):
    """Legacy check-in form (kept for compatibility)"""
    booking_id = request.GET.get('booking_id')
    room_id = request.GET.get('room_id')  # Get room_id from URL
    booking_instance = None
    room_instance = None

    # Get booking instance if a booking_id is provided
    if booking_id:
        booking_instance = get_object_or_404(Booking, id=booking_id)
        # If the booking has a pre-assigned room, use it
        if booking_instance.room:
            room_instance = booking_instance.room
            
    # If no booking, check for a room_id (for walk-ins from the dashboard)
    elif room_id:
        # Ensure the selected room is actually available
        room_instance = get_object_or_404(Room, id=room_id, status='AVAILABLE')

    if request.method == 'POST':
        # The form submission logic remains the same
        form = CheckInForm(request.POST, booking_instance=booking_instance)
        if form.is_valid():
            checkin = form.save()
            
            # Update room status to occupied
            checkin.room_number.status = 'OCCUPIED'
            checkin.room_number.save()
            
            # Update booking status if linked
            if checkin.booking:
                checkin.booking.status = 'CHECKED_IN'
                checkin.booking.save()
            
            messages.success(request, f'Check-in {checkin.check_in_id} created successfully!')
            return redirect('checkin-detail', checkin_id=checkin.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        # Pass the room instance to pre-select it in the form
        form = CheckInForm(booking_instance=booking_instance, room_instance=room_instance)

    context = {
        'form': form,
        'booking_instance': booking_instance,
        'title': 'Standard Check-In',
        'submit_text': 'Complete Check-In'
    }
    return render(request, 'checkin/checkin_form.html', context)


def checkin_update(request, checkin_id):
    """Update an existing check-in"""
    checkin = get_object_or_404(CheckIn, id=checkin_id)

    if request.method == 'POST':
        form = CheckInForm(request.POST, instance=checkin)
        if form.is_valid():
            checkin = form.save()
            messages.success(request, f'Check-in {checkin.check_in_id} updated successfully!')
            return redirect('checkin-detail', checkin_id=checkin.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = CheckInForm(instance=checkin)

    context = {
        'form': form,
        'checkin': checkin,
        'title': f'Edit Check-In: {checkin.check_in_id}',
        'submit_text': 'Update Check-In'
    }
    return render(request, 'checkin/checkin_form.html', context)


def quick_checkin(request):
    """Quick check-in for walk-in guests"""
    if request.method == 'POST':
        form = QuickCheckInForm(request.POST)
        if form.is_valid():
            checkin = form.save(commit=False)
            checkin.actual_check_in_date_time = timezone.now()
            checkin.payment_status = 'PENDING'
            checkin.save()

            # Update room status
            checkin.room_number.status = 'OCCUPIED'
            checkin.room_number.save()

            messages.success(request, f'Quick check-in completed! Check-in ID: {checkin.check_in_id}')
            return redirect('checkin-detail', checkin_id=checkin.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = QuickCheckInForm()

    context = {
        'form': form,
        'title': 'Quick Check-In (Walk-in)',
        'submit_text': 'Complete Quick Check-In'
    }
    return render(request, 'checkin/quick_checkin_form.html', context)


def checkin_from_booking(request, booking_id):
    """Check-in from an existing booking"""
    booking = get_object_or_404(Booking, id=booking_id)

    # Check if already checked in
    existing_checkin = CheckIn.objects.filter(booking=booking).first()
    if existing_checkin:
        messages.info(request, f'This booking is already checked in (ID: {existing_checkin.check_in_id})')
        return redirect('checkin-detail', checkin_id=existing_checkin.id)

    return redirect('checkin-create') + f'?booking_id={booking_id}'


def checkin_dashboard(request):
    """Check-in dashboard with statistics and recent activity"""
    today = date.today()
    room_view = request.GET.get('room_view', None)

    # Statistics
    total_checkins = CheckIn.objects.count()
    todays_checkins = CheckIn.objects.filter(actual_check_in_date_time__date=today).count()
    pending_payments = CheckIn.objects.filter(payment_status='PENDING').count()
    unverified_ids = CheckIn.objects.filter(id_proof_verified=False).count()

    # Recent check-ins
    recent_checkins = CheckIn.objects.select_related(
        'guest', 'room_number', 'booking'
    ).order_by('-actual_check_in_date_time')[:10]

    # Today's check-ins
    todays_checkin_list = CheckIn.objects.filter(
        actual_check_in_date_time__date=today
    ).select_related('guest', 'room_number').order_by('-actual_check_in_date_time')

    # Payment status summary
    payment_summary = CheckIn.objects.values('payment_status').annotate(
        count=Count('id')
    ).order_by('payment_status')

    # --- FIX IS HERE ---
    # Get the list of available rooms as a queryset
    available_rooms = Room.objects.filter(status='AVAILABLE')
    if room_view:
        available_rooms = available_rooms.filter(view=room_view)
    # --- END FIX ---
    
    context = {
        'today': today,
        'total_checkins': total_checkins,
        'todays_checkins': todays_checkins,
        'pending_payments': pending_payments,
        'unverified_ids': unverified_ids,
        'recent_checkins': recent_checkins,
        'todays_checkin_list': todays_checkin_list,
        'payment_summary': payment_summary,
        
        # --- FIX IS HERE ---
        # Pass the queryset and other filter-related context
        'available_rooms': available_rooms,
        'room_views': Room.VIEW_CHOICES,
        'selected_view': room_view,
        # --- END FIX ---
    }
    return render(request, 'checkin/dashboard.html', context)


def verify_id_proof(request, checkin_id):
    """Mark ID proof as verified"""
    checkin = get_object_or_404(CheckIn, id=checkin_id)

    if request.method == 'POST':
        checkin.id_proof_verified = True
        checkin.save()
        messages.success(request, f'ID proof verified for check-in {checkin.check_in_id}')

    return redirect('checkin-detail', checkin_id=checkin.id)


def update_payment_status(request, checkin_id):
    """Update payment status"""
    checkin = get_object_or_404(CheckIn, id=checkin_id)

    if request.method == 'POST':
        new_status = request.POST.get('payment_status')
        if new_status in dict(CheckIn.PAYMENT_STATUS_CHOICES):
            checkin.payment_status = new_status
            checkin.save()
            messages.success(request, f'Payment status updated to {checkin.get_payment_status_display()}')
        else:
            messages.error(request, 'Invalid payment status')

    return redirect('checkin-detail', checkin_id=checkin.id)


def enhanced_checkin_create(request):
    """Enhanced check-in with guest creation capability and booking form toggle"""
    booking_id = request.GET.get('booking_id')
    room_id = request.GET.get('room_id')
    form_type = request.GET.get('form_type', 'checkin')  # 'checkin' or 'booking'
    booking_instance = None
    room_instance = None

    # Get booking instance if a booking_id is provided
    if booking_id:
        booking_instance = get_object_or_404(Booking, id=booking_id)
        if booking_instance.room:
            room_instance = booking_instance.room
            
    # If no booking, check for a room_id (for walk-ins from the dashboard)
    elif room_id:
        room_instance = get_object_or_404(Room, id=room_id, status='AVAILABLE')

    if request.method == 'POST':
        # Determine which form was submitted
        if 'booking_submit' in request.POST:
            # Handle booking form submission
            booking_form = BookingForm(request.POST)
            if booking_form.is_valid():
                booking = booking_form.save()
                messages.success(request, f'Booking {booking.id} created successfully!')
                return redirect('booking-detail', booking_id=booking.id)
            else:
                messages.error(request, 'Please correct the errors in the booking form.')
                # Initialize check-in form for display
                checkin_form = EnhancedCheckInForm(booking_instance=booking_instance, room_instance=room_instance)
        else:
            # Handle check-in form submission
            checkin_form = EnhancedCheckInForm(request.POST, request.FILES, booking_instance=booking_instance)
            if checkin_form.is_valid():
                checkin = checkin_form.save()
                
                # Update room status to occupied
                checkin.room_number.status = 'OCCUPIED'
                checkin.room_number.save()
                
                # Update booking status if linked
                if checkin.booking:
                    checkin.booking.status = 'CHECKED_IN'
                    checkin.booking.save()
                
                # Create workflow if enhanced models are available
                try:
                    checkin.create_workflow()
                except:
                    pass  # Ignore if enhanced models not available
                
                success_message = f'Check-in {checkin.check_in_id} completed successfully!'
                if checkin_form.cleaned_data.get('create_new_guest'):
                    success_message += f' New guest profile created for {checkin.guest.full_name}.'
                
                messages.success(request, success_message)
                return redirect('checkin-detail', checkin_id=checkin.id)
            else:
                messages.error(request, 'Please correct the errors in the check-in form.')
                # Initialize booking form for display
                booking_form = BookingForm()
    else:
        # Initialize forms based on form_type parameter
        checkin_form = EnhancedCheckInForm(booking_instance=booking_instance, room_instance=room_instance)
        booking_form = BookingForm()

    context = {
        'checkin_form': checkin_form,
        'booking_form': booking_form,
        'booking_instance': booking_instance,
        'form_type': form_type,
        'title': 'Guest Check-In & Booking',
        'submit_text': 'Complete Check-In'
    }
    return render(request, 'checkin/enhanced_checkin_form.html', context)


def enhanced_checkin_update(request, checkin_id):
    """Update an existing check-in using enhanced form"""
    checkin = get_object_or_404(CheckIn, id=checkin_id)

    if request.method == 'POST':
        form = EnhancedCheckInForm(request.POST, request.FILES, instance=checkin)
        if form.is_valid():
            checkin = form.save()
            messages.success(request, f'Check-in {checkin.check_in_id} updated successfully!')
            return redirect('checkin-detail', checkin_id=checkin.id)
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = EnhancedCheckInForm(instance=checkin)

    context = {
        'form': form,
        'checkin': checkin,
        'title': f'Edit Check-In: {checkin.check_in_id}',
        'submit_text': 'Update Check-In'
    }
    return render(request, 'checkin/enhanced_checkin_form.html', context)


def guest_search_api(request):
    """API endpoint for guest search functionality with detailed information"""
    query = request.GET.get('q', '').strip()
    
    if len(query) < 2:
        return JsonResponse({'guests': []})
    
    # Search guests by name, email, or phone
    guests = Guest.objects.filter(
        Q(first_name__icontains=query) |
        Q(last_name__icontains=query) |
        Q(email__icontains=query) |
        Q(contact_number__icontains=query)
    ).order_by('first_name', 'last_name')[:10]
    
    guest_data = []
    for guest in guests:
        # Get booking history count
        booking_count = guest.bookings.count()
        last_booking = guest.bookings.order_by('-check_in_date').first()
        
        guest_data.append({
            'id': guest.guest_id,  # Use the correct primary key field
            'name': guest.full_name,
            'email': guest.email,
            'phone': guest.contact_number,
            'address': guest.address or 'Not provided',
            'id_proof_type': guest.get_id_proof_type_display() if guest.id_proof_type else 'Not provided',
            'id_proof_number': guest.id_proof_number or 'Not provided',
            'gender': guest.get_gender_display() if guest.gender else 'Not specified',
            'nationality': guest.nationality or 'Not specified',
            'date_of_birth': guest.date_of_birth.strftime('%d-%m-%Y') if guest.date_of_birth else 'Not provided',
            'booking_count': booking_count,
            'last_booking_date': last_booking.check_in_date.strftime('%d-%m-%Y') if last_booking else 'No previous bookings',
            'display': f"{guest.full_name} - {guest.email} - {guest.contact_number}"
        })
    
    return JsonResponse({'guests': guest_data})


def save_guest_data_api(request):
    """API endpoint to save guest data and return guest info"""
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'Method not allowed'})
    
    try:
        # Get form data
        first_name = request.POST.get('first_name', '').strip()
        last_name = request.POST.get('last_name', '').strip()
        email = request.POST.get('email', '').strip()
        phone = request.POST.get('phone', '').strip()
        address = request.POST.get('address', '').strip()
        id_proof_type = request.POST.get('id_proof_type', 'OTHER')
        id_proof_number = request.POST.get('id_proof_number', '').strip()
        date_of_birth_str = request.POST.get('date_of_birth', '').strip()
        gender = request.POST.get('gender', 'O')
        
        # Validate required fields
        if not all([first_name, last_name, email, phone]):
            return JsonResponse({
                'success': False, 
                'error': 'First name, last name, email, and phone are required.'
            })
        
        # Check if guest with email already exists
        if Guest.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False, 
                'error': 'A guest with this email already exists.'
            })
        
        # Parse date of birth if provided
        guest_date_of_birth = None
        if date_of_birth_str:
            try:
                from datetime import datetime
                guest_date_of_birth = datetime.strptime(date_of_birth_str, '%Y-%m-%d').date()
            except ValueError:
                pass  # Use None if parsing fails
        
        # Create new guest
        guest = Guest.objects.create(
            first_name=first_name,
            last_name=last_name,
            email=email,
            contact_number=phone,
            address=address,
            id_proof_type=id_proof_type,
            id_proof_number=id_proof_number,
            date_of_birth=guest_date_of_birth,
            gender=gender,
            nationality='Indian'  # Default nationality
        )
        
        return JsonResponse({
            'success': True,
            'guest': {
                'id': guest.id,
                'name': guest.full_name,
                'email': guest.email,
                'phone': guest.contact_number,
                'display': f"{guest.full_name} - {guest.email} - {guest.contact_number}"
            }
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False, 
            'error': f'Error saving guest: {str(e)}'
        })