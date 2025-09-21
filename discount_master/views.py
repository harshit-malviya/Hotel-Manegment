
from django.shortcuts import render, get_object_or_404, redirect
from .models import DiscountMaster
from .forms import DiscountMasterForm

def discount_list(request):
    discounts = DiscountMaster.objects.all()
    return render(request, 'discount_master/discount_list.html', {'discounts': discounts})

def discount_create(request):
    if request.method == 'POST':
        form = DiscountMasterForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('discount_list')
    else:
        form = DiscountMasterForm()
    return render(request, 'discount_master/discount_form.html', {'form': form, 'action': 'Create'})

def discount_update(request, pk):
    discount = get_object_or_404(DiscountMaster, pk=pk)
    if request.method == 'POST':
        form = DiscountMasterForm(request.POST, instance=discount)
        if form.is_valid():
            form.save()
            return redirect('discount_list')
    else:
        form = DiscountMasterForm(instance=discount)
    return render(request, 'discount_master/discount_form.html', {'form': form, 'action': 'Update'})

def discount_delete(request, pk):
    discount = get_object_or_404(DiscountMaster, pk=pk)
    if request.method == 'POST':
        discount.delete()
        return redirect('discount_list')
    return render(request, 'discount_master/discount_confirm_delete.html', {'discount': discount})

def discount_detail(request, pk):
    discount = get_object_or_404(DiscountMaster, pk=pk)
    return render(request, 'discount_master/discount_detail.html', {'discount': discount})