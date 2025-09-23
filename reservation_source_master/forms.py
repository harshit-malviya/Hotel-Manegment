from django import forms
from django.core.exceptions import ValidationError
from datetime import date, timedelta
from .models import Booking, ReservationSource
from guest.models import Guest
from rooms.models import Room, RoomType
from rate.models import RatePlan


class ReservationSourceForm(forms.ModelForm):
    class Meta:
        model = ReservationSource
        fields = [
            'source_id', 'name', 'source_type', 'contact_person', 'email', 'phone',
            'address', 'commission_rate', 'is_active', 'website_url', 'notes'
        ]
        
        widgets = {
            'source_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Leave blank for auto-generation'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., Booking.com, Expedia, Company Website'
            }),
            'source_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'contact_person': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Contact person name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'contact@example.com'
            }),
            'phone': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': '+91-9876543210'
            }),
            'address': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Complete address'
            }),
            'commission_rate': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'max': '100',
                'placeholder': '0.00'
            }),
            'is_active': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'website_url': forms.URLInput(attrs={
                'class': 'form-control',
                'placeholder': 'https://example.com'
            }),
            'notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes about this source'
            }),
        }
        
        labels = {
            'source_id': 'Source ID',
            'name': 'Source Name',
            'source_type': 'Source Type',
            'contact_person': 'Contact Person',
            'email': 'Email',
            'phone': 'Phone',
            'address': 'Address',
            'commission_rate': 'Commission Rate (%)',
            'is_active': 'Active',
            'website_url': 'Website URL',
            'notes': 'Notes',
        }