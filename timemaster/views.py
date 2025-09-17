from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import TimeEntryForm
from .models import TimeEntry
import json

def time_entry_view(request):
    if request.method == 'POST':
        try:
            # Get the JSON data from the request
            entries = json.loads(request.POST.get('entries', '[]'))
            
            # Save each entry
            for entry_data in entries:
                TimeEntry.objects.create(
                    entry_id=entry_data['entry_id'],
                    name=entry_data['name'],
                    hours=entry_data['hours']
                )
            
            messages.success(request, 'Time entries saved successfully!')
            return redirect('timemaster:time_entry')
        except Exception as e:
            messages.error(request, f'Error saving entries: {str(e)}')
    
    form = TimeEntryForm()
    time_entries = TimeEntry.objects.all().order_by('-created_at')
    return render(request, 'timemaster/time_entry.html', {
        'form': form,
        'time_entries': time_entries
    })
