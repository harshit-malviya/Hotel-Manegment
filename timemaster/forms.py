from django import forms
from .models import TimeEntry

class TimeEntryForm(forms.ModelForm):
    class Meta:
        model = TimeEntry
        fields = ['entry_id', 'name', 'hours']
        widgets = {
            'entry_id': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter ID'}),
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter Name'}),
            'hours': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Enter Hours'}),
        }