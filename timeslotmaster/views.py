
from django.shortcuts import render, get_object_or_404, redirect
from .models import TimeslotMaster
from .forms import TimeslotMasterForm

def timeslot_list(request):
	timeslots = TimeslotMaster.objects.all()
	return render(request, 'timeslotmaster/list.html', {'timeslots': timeslots})

def timeslot_detail(request, pk):
	timeslot = get_object_or_404(TimeslotMaster, pk=pk)
	return render(request, 'timeslotmaster/detail.html', {'timeslot': timeslot})

def timeslot_create(request):
	if request.method == 'POST':
		form = TimeslotMasterForm(request.POST)
		if form.is_valid():
			form.save()
			return redirect('timeslot_list')
	else:
		form = TimeslotMasterForm()
	return render(request, 'timeslotmaster/form.html', {'form': form, 'action': 'Create'})

def timeslot_update(request, pk):
	timeslot = get_object_or_404(TimeslotMaster, pk=pk)
	if request.method == 'POST':
		form = TimeslotMasterForm(request.POST, instance=timeslot)
		if form.is_valid():
			form.save()
			return redirect('timeslot_list')
	else:
		form = TimeslotMasterForm(instance=timeslot)
	return render(request, 'timeslotmaster/form.html', {'form': form, 'action': 'Update'})

def timeslot_delete(request, pk):
	timeslot = get_object_or_404(TimeslotMaster, pk=pk)
	if request.method == 'POST':
		timeslot.delete()
		return redirect('timeslot_list')
	return render(request, 'timeslotmaster/confirm_delete.html', {'timeslot': timeslot})
