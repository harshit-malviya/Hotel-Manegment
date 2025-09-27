from django import forms
from .models import Booking


from timeslotmaster.models import TimeslotMaster
from rate.models import RatePlan
from rooms.models import RoomType

class BookingForm(forms.ModelForm):
    time_slot = forms.ModelChoiceField(
        queryset=TimeslotMaster.objects.none(),
        required=True,
        widget=forms.Select(attrs={'class': 'form-control'}),
        label='Time Slot'
    )

    class Meta:
        model = Booking
        fields = '__all__'
        widgets = {
            'customer_first_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'First Name'
            }),
            'customer_last_name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Last Name'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Phone Number'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'id_proof_type': forms.Select(attrs={
                'class': 'form-control'
            }),
            'id_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'ID Number'
            }),
            'id_photo': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'room_type': forms.Select(attrs={
                'class': 'form-control',
                'onchange': 'updateTimeSlotsAndPrice();'
            }),
            'payment_method': forms.Select(attrs={
                'class': 'form-control'
            }),
            'reservation_source': forms.Select(attrs={
                'class': 'form-control',
                'id': 'id_reservation_source'
            }),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if 'room_type' in self.data:
            try:
                room_type_id = int(self.data.get('room_type'))
                self.fields['time_slot'].queryset = RatePlan.objects.filter(room_type_id=room_type_id).values_list('time_slot', flat=True).distinct()
                self.fields['time_slot'].queryset = TimeslotMaster.objects.filter(id__in=self.fields['time_slot'].queryset)
            except (ValueError, TypeError):
                self.fields['time_slot'].queryset = TimeslotMaster.objects.none()
        elif self.instance.pk:
            self.fields['time_slot'].queryset = TimeslotMaster.objects.filter(rate_plans__room_type=self.instance.room_type).distinct()
        else:
            self.fields['time_slot'].queryset = TimeslotMaster.objects.none()
