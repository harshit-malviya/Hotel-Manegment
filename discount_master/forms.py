from django import forms
from .models import DiscountMaster

class DiscountMasterForm(forms.ModelForm):
    class Meta:
        model = DiscountMaster
        fields = ['description', 'discount_value', 'temporary_price']
        widgets = {
            'description': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Discount Description'}),
            'discount_value': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. 100 or 10%'}),
            'temporary_price': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Base Price'}),
        }