from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import ReservationSource
from .forms import ReservationSourceForm

def reservation_source_list(request):
    """Display list of all reservation sources"""
    sources = ReservationSource.objects.all()
    context = {
        'sources': sources,
        'title': 'Reservation Sources'
    }
    return render(request, 'reservation_source_master/reservation_source_list.html', context)

def reservation_source_create(request):
    """Create a new reservation source"""
    if request.method == 'POST':
        form = ReservationSourceForm(request.POST)
        if form.is_valid():
            source = form.save()
            messages.success(request, f'Reservation source "{source.name}" created successfully!')
            return redirect('reservation-source-list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReservationSourceForm()
    
    context = {
        'form': form,
        'title': 'Create New Reservation Source',
        'submit_text': 'Create Source'
    }
    return render(request, 'reservation_source_master/reservation_source_form.html', context)

def reservation_source_detail(request, source_id):
    """Display details of a specific reservation source"""
    source = get_object_or_404(ReservationSource, id=source_id)
    context = {
        'source': source,
        'title': f'Reservation Source: {source.name}'
    }
    return render(request, 'reservation_source_master/reservation_source_detail.html', context)

def reservation_source_update(request, source_id):
    """Update an existing reservation source"""
    source = get_object_or_404(ReservationSource, id=source_id)
    if request.method == 'POST':
        form = ReservationSourceForm(request.POST, instance=source)
        if form.is_valid():
            source = form.save()
            messages.success(request, f'Reservation source "{source.name}" updated successfully!')
            return redirect('reservation-source-list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = ReservationSourceForm(instance=source)
    
    context = {
        'form': form,
        'source': source,
        'title': f'Edit Reservation Source: {source.name}',
        'submit_text': 'Update Source'
    }
    return render(request, 'reservation_source_master/reservation_source_form.html', context)

def reservation_source_delete(request, source_id):
    """Delete a reservation source"""
    source = get_object_or_404(ReservationSource, id=source_id)
    if request.method == 'POST':
        source_name = source.name
        source.delete()
        messages.success(request, f'Reservation source "{source_name}" deleted successfully!')
        return redirect('reservation-source-list')
    
    context = {
        'source': source,
        'title': f'Delete Reservation Source: {source.name}'
    }
    return render(request, 'reservation_source_master/reservation_source_confirm_delete.html', context)
