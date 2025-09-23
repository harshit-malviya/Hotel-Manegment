from django.shortcuts import render, redirect
from .forms import BookingForm

def create_booking(request):
    if request.method == 'POST':
        form = BookingForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect('booking_success')
    else:
        form = BookingForm()
    return render(request, 'booking_master/booking_form.html', {'form': form})

def booking_success(request):
    return render(request, 'booking_master/booking_success.html')
