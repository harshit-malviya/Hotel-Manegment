from django import forms
from .models import TimeslotMaster

class TimeslotMasterForm(forms.ModelForm):
    class Meta:
        model = TimeslotMaster
        fields = ['name', 'time']
