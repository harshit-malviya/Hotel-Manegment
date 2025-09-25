from django import forms
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import date, timedelta, datetime
from .enhanced_models import CheckIn
from booking_master.models import Booking
from guest.models import Guest
from rooms.models import Room


class DateTime12HourWidget(forms.DateTimeInput):
    """Custom widget for 12-hour datetime input with Indian timezone"""
    
    def __init__(self, attrs=None):
        default_attrs = {
            'class': 'form-control',
            'type': 'datetime-local',
            'step': '60'  # 1 minute steps
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(attrs=default_attrs)
    
    def format_value(self, value):
        if value is None:
            return ''
        
        # Convert to Indian timezone if it's timezone-aware
        if timezone.is_aware(value):
            indian_tz = timezone.get_current_timezone()
            value = value.astimezone(indian_tz)
        
        # Format for datetime-local input (24-hour format for HTML input)
        return value.strftime('%Y-%m-%dT%H:%M')
    
    def value_from_datadict(self, data, files, name):
        value = super().value_from_datadict(data, files, name)
        if value:
            try:
                # Parse the datetime-local format
                dt = datetime.strptime(value, '%Y-%m-%dT%H:%M')
                # Make it timezone-aware with Indian timezone
                indian_tz = timezone.get_current_timezone()
                # Use replace() method for zoneinfo.ZoneInfo objects
                return dt.replace(tzinfo=indian_tz)
            except ValueError:
                return None
        return None


class CheckInForm(forms.ModelForm):
    class Meta:
        model = CheckIn
        fields = [
            'check_in_id', 'booking', 'guest', 'actual_check_in_date_time',
            'room_number', 'id_proof_verified', 'payment_status',
            'assigned_staff', 'expected_check_out_date', 'number_of_guests',
            'advance_payment', 'total_amount', 'remarks_notes','base_tariff','discount_amount',
        ]
        
        widgets = {
            'check_in_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auto-generated if left blank'
            }),
            'booking': forms.Select(attrs={
                'class': 'form-control'
            }),
            'guest': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'actual_check_in_date_time': DateTime12HourWidget(),
            'room_number': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'id_proof_verified': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'payment_status': forms.Select(attrs={
                'class': 'form-control'
            }),
            'assigned_staff': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Staff member name'
            }),
            'expected_check_out_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'number_of_guests': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
            'advance_payment': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'remarks_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes or special requests...'
            }),
            'base_tariff': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
        }
        
        labels = {
            'check_in_id': 'Check-In ID',
            'booking': 'Booking Reference',
            'guest': 'Primary Guest',
            'actual_check_in_date_time': 'Check-In Date & Time',
            'room_number': 'Room Number',
            'id_proof_verified': 'ID Proof Verified',
            'payment_status': 'Payment Status',
            'assigned_staff': 'Assigned Staff',
            'expected_check_out_date': 'Expected Check-Out Date',
            'number_of_guests': 'Number of Guests',
            'advance_payment': 'Advance Payment (₹)',
            'total_amount': 'Total Amount (₹)',
            'remarks_notes': 'Remarks/Notes',
        }
    
    def __init__(self, *args, **kwargs):
        booking_instance = kwargs.pop('booking_instance', None)
        room_instance = kwargs.pop('room_instance', None)
        super().__init__(*args, **kwargs)

        self.fields['room_number'].queryset = Room.objects.filter(status='AVAILABLE')

        if room_instance:
            self.fields['room_number'].queryset = (
                self.fields['room_number'].queryset | Room.objects.filter(pk=room_instance.pk)
            ).distinct()
            self.fields['room_number'].initial = room_instance.pk
        
        # Set querysets
        self.fields['guest'].queryset = Guest.objects.all().order_by('first_name', 'last_name')
        self.fields['room_number'].queryset = Room.objects.all().order_by('room_number')
        self.fields['booking'].queryset = Booking.objects.filter(
            status__in=['CONFIRMED', 'CHECKED_IN']
        ).order_by('-created_at')
        
        # Set empty labels
        self.fields['booking'].empty_label = "Select Booking (Optional for Walk-ins)"
        self.fields['guest'].empty_label = "Select Guest"
        self.fields['room_number'].empty_label = "Select Room"
        
        # Make some fields optional
        self.fields['check_in_id'].required = False
        self.fields['booking'].required = False
        self.fields['assigned_staff'].required = False
        self.fields['expected_check_out_date'].required = False
        self.fields['remarks_notes'].required = False
        
        # Set default check-in time to current Indian time
        if not self.instance.pk:
            current_time = timezone.now()
            self.fields['actual_check_in_date_time'].initial = current_time
        
        # Pre-fill from booking if provided
        if booking_instance and not self.instance.pk:
            self.fields['booking'].initial = booking_instance.pk
            self.fields['guest'].initial = booking_instance.guest.pk
            self.fields['room_number'].initial = booking_instance.room.pk
            self.fields['expected_check_out_date'].initial = booking_instance.check_out_date
            self.fields['total_amount'].initial = booking_instance.total_amount
            self.fields['number_of_guests'].initial = booking_instance.number_of_guests
    
    def clean(self):
        cleaned_data = super().clean()
        booking = cleaned_data.get('booking')
        guest = cleaned_data.get('guest')
        room_number = cleaned_data.get('room_number')
        actual_check_in_date_time = cleaned_data.get('actual_check_in_date_time')
        expected_check_out_date = cleaned_data.get('expected_check_out_date')
        advance_payment = cleaned_data.get('advance_payment', 0)
        total_amount = cleaned_data.get('total_amount', 0)
        
        # Validate that either booking or guest is provided
        if not booking and not guest:
            raise ValidationError('Either booking reference or guest must be provided.')
        
        # If booking is provided, validate guest matches
        if booking and guest and booking.guest != guest:
            raise ValidationError('Selected guest does not match the booking guest.')
        
        # Validate check-in date is not in the future (allow some flexibility)
        if actual_check_in_date_time and actual_check_in_date_time > timezone.now() + timedelta(hours=1):
            raise ValidationError('Check-in date cannot be more than 1 hour in the future.')
        
        # Validate expected check-out is after check-in
        if actual_check_in_date_time and expected_check_out_date:
            if expected_check_out_date <= actual_check_in_date_time.date():
                raise ValidationError('Expected check-out date must be after check-in date.')
        
        # Validate advance payment doesn't exceed total amount
        if advance_payment and total_amount and advance_payment > total_amount:
            raise ValidationError('Advance payment cannot exceed total amount.')
        
        # Check room availability (basic check)
        if room_number and actual_check_in_date_time:
            overlapping_checkins = CheckIn.objects.filter(
                room_number=room_number,
                actual_check_in_date_time__date=actual_check_in_date_time.date()
            )
            if self.instance.pk:
                overlapping_checkins = overlapping_checkins.exclude(pk=self.instance.pk)
            
            if overlapping_checkins.exists():
                raise ValidationError(f'Room {room_number.room_number} already has a check-in for this date.')
        
        return cleaned_data


class CheckInSearchForm(forms.Form):
    search = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search by Check-In ID, Guest name, or Room number...'
        })
    )
    
    payment_status = forms.ChoiceField(
        choices=[('', 'All Payment Status')] + CheckIn.PAYMENT_STATUS_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    date_range = forms.ChoiceField(
        choices=[
            ('', 'All Dates'),
            ('today', 'Today'),
            ('yesterday', 'Yesterday'),
            ('this_week', 'This Week'),
            ('this_month', 'This Month'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )
    
    id_verified = forms.ChoiceField(
        choices=[
            ('', 'All'),
            ('true', 'ID Verified'),
            ('false', 'ID Not Verified'),
        ],
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        })
    )


class QuickCheckInForm(forms.ModelForm):
    """Simplified form for quick walk-in check-ins"""
    
    class Meta:
        model = CheckIn
        fields = [
            'guest', 'room_number', 'number_of_guests', 
            'expected_check_out_date', 'advance_payment', 'total_amount'
        ]
        
        widgets = {
            'guest': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'room_number': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'number_of_guests': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
            'expected_check_out_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
                'min': date.today().isoformat()
            }),
            'advance_payment': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
            'total_amount': forms.NumberInput(attrs={
                'class': 'form-control',
                'step': '0.01',
                'min': '0',
                'placeholder': '0.00'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Set querysets for available rooms only
        self.fields['room_number'].queryset = Room.objects.filter(
            status='AVAILABLE'
        ).order_by('room_number')
        
        self.fields['guest'].queryset = Guest.objects.all().order_by('first_name', 'last_name')
        
        # Set empty labels
        self.fields['guest'].empty_label = "Select Guest"
        self.fields['room_number'].empty_label = "Select Available Room"
        
        # Set default expected check-out to tomorrow
        self.fields['expected_check_out_date'].initial = date.today() + timedelta(days=1)


class EnhancedCheckInForm(forms.ModelForm):
    """Enhanced check-in form with guest creation capability and simplified payment"""
    
    # Hidden field to store selected guest ID
    selected_guest_id = forms.CharField(
        required=False,
        widget=forms.HiddenInput(attrs={
            'id': 'selected_guest_id'
        })
    )
    
    # Guest creation fields (optional)
    create_new_guest = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={
            'class': 'form-check-input',
            'id': 'create_new_guest'
        }),
        label='Create New Guest'
    )
    
    # New guest fields
    guest_first_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter first name'
        }),
        label='First Name'
    )
    
    guest_last_name = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter last name'
        }),
        label='Last Name'
    )
    
    guest_email = forms.EmailField(
        required=False,
        widget=forms.EmailInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter email address'
        }),
        label='Email'
    )
    
    guest_phone = forms.CharField(
        max_length=17,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': '+91XXXXXXXXXX'
        }),
        label='Phone Number'
    )
    
    guest_address = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'class': 'form-control',
            'rows': 2,
            'placeholder': 'Enter address'
        }),
        label='Address'
    )
    
    guest_id_proof_type = forms.ChoiceField(
        choices=Guest.ID_PROOF_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='ID Proof Type'
    )
    
    guest_id_proof_number = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter ID proof number'
        }),
        label='ID Proof Number'
    )
    
    guest_date_of_birth = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={
            'class': 'form-control',
            'type': 'date'
        }),
        label='Date of Birth'
    )
    
    guest_gender = forms.ChoiceField(
        choices=Guest.GENDER_CHOICES,
        required=False,
        widget=forms.Select(attrs={
            'class': 'form-control'
        }),
        label='Gender'
    )
    
    guest_id_proof_image = forms.ImageField(
        required=False,
        widget=forms.ClearableFileInput(attrs={
            'class': 'form-control',
            'accept': 'image/*'
        }),
        label='ID Proof Image'
    )
    
    class Meta:
        model = CheckIn
        fields = [
            'check_in_id', 'booking', 'guest', 'actual_check_in_date_time',
            'room_number', 'id_proof_verified', 'assigned_staff', 
            'expected_check_out_date', 'number_of_guests', 'remarks_notes'
        ]
        
        widgets = {
            'check_in_id': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Auto-generated if left blank'
            }),
            'booking': forms.Select(attrs={
                'class': 'form-control'
            }),
            'guest': forms.TextInput(attrs={
                'class': 'form-control guest-search',
                'placeholder': 'Search guest by name, email, or phone...',
                'autocomplete': 'off'
            }),
            'actual_check_in_date_time': DateTime12HourWidget(),
            'room_number': forms.Select(attrs={
                'class': 'form-control',
                'required': True
            }),
            'id_proof_verified': forms.CheckboxInput(attrs={
                'class': 'form-check-input'
            }),
            'assigned_staff': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Staff member name'
            }),
            'expected_check_out_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date'
            }),
            'number_of_guests': forms.NumberInput(attrs={
                'class': 'form-control',
                'min': '1',
                'value': '1'
            }),
            'remarks_notes': forms.Textarea(attrs={
                'class': 'form-control',
                'rows': 3,
                'placeholder': 'Additional notes or special requests...'
            }),
        }
        
        labels = {
            'check_in_id': 'Check-In ID',
            'booking': 'Booking Reference',
            'guest': 'Select Existing Guest',
            'actual_check_in_date_time': 'Check-In Date & Time',
            'room_number': 'Room Number',
            'id_proof_verified': 'ID Proof Verified',
            'assigned_staff': 'Assigned Staff',
            'expected_check_out_date': 'Expected Check-Out Date',
            'number_of_guests': 'Number of Guests',
            'remarks_notes': 'Remarks/Notes',
        }
    
    def __init__(self, *args, **kwargs):
        booking_instance = kwargs.pop('booking_instance', None)
        room_instance = kwargs.pop('room_instance', None)
        super().__init__(*args, **kwargs)
        
        # Set querysets
        self.fields['guest'].queryset = Guest.objects.all().order_by('first_name', 'last_name')
        self.fields['room_number'].queryset = Room.objects.filter(status='AVAILABLE').order_by('room_number')
        self.fields['booking'].queryset = Booking.objects.filter(
            status__in=['CONFIRMED', 'CHECKED_IN']
        ).order_by('-created_at')
        
        # Set empty labels
        self.fields['booking'].empty_label = "Select Booking (Optional for Walk-ins)"
        self.fields['guest'].empty_label = "Select Existing Guest or Create New"
        self.fields['room_number'].empty_label = "Select Room"
        
        # Make some fields optional
        self.fields['check_in_id'].required = False
        self.fields['booking'].required = False
        self.fields['guest'].required = False  # Will be validated in clean method
        self.fields['assigned_staff'].required = False
        self.fields['expected_check_out_date'].required = False
        self.fields['remarks_notes'].required = False
        
        # Set default check-in time to current time
        if not self.instance.pk:
            current_time = timezone.now()
            self.fields['actual_check_in_date_time'].initial = current_time
        
        # Pre-fill from booking if provided
        if booking_instance and not self.instance.pk:
            self.fields['booking'].initial = booking_instance.pk
            self.fields['guest'].initial = booking_instance.guest.pk
            if booking_instance.room:
                self.fields['room_number'].initial = booking_instance.room.pk
            self.fields['expected_check_out_date'].initial = booking_instance.check_out_date
            self.fields['number_of_guests'].initial = booking_instance.total_guests
        
        # Pre-select room if provided
        if room_instance:
            self.fields['room_number'].queryset = (
                self.fields['room_number'].queryset | Room.objects.filter(pk=room_instance.pk)
            ).distinct()
            self.fields['room_number'].initial = room_instance.pk
    
    def clean(self):
        cleaned_data = super().clean()
        create_new_guest = cleaned_data.get('create_new_guest')
        selected_guest_id = cleaned_data.get('selected_guest_id')
        booking = cleaned_data.get('booking')
        
        # Handle guest selection from search
        guest = None
        if selected_guest_id and not create_new_guest:
            try:
                guest = Guest.objects.get(id=selected_guest_id)
                cleaned_data['guest'] = guest
            except Guest.DoesNotExist:
                self.add_error('guest', 'Selected guest not found.')
        
        # Validate guest selection or creation
        if create_new_guest:
            # Validate new guest fields
            required_guest_fields = ['guest_first_name', 'guest_last_name', 'guest_email', 'guest_phone']
            for field in required_guest_fields:
                if not cleaned_data.get(field):
                    self.add_error(field, f'This field is required when creating a new guest.')
            
            # Validate email uniqueness
            guest_email = cleaned_data.get('guest_email')
            if guest_email and Guest.objects.filter(email=guest_email).exists():
                self.add_error('guest_email', 'A guest with this email already exists.')
        else:
            # Validate existing guest selection
            if not guest and not booking:
                self.add_error('guest', 'Please search and select an existing guest or choose to create a new guest.')
        
        # If booking is provided, validate guest matches
        if booking and guest and booking.guest != guest:
            self.add_error('guest', 'Selected guest does not match the booking guest.')
        
        # Other validations
        actual_check_in_date_time = cleaned_data.get('actual_check_in_date_time')
        expected_check_out_date = cleaned_data.get('expected_check_out_date')
        room_number = cleaned_data.get('room_number')
        
        # Validate check-in date is not in the future
        if actual_check_in_date_time and actual_check_in_date_time > timezone.now() + timedelta(hours=1):
            self.add_error('actual_check_in_date_time', 'Check-in date cannot be more than 1 hour in the future.')
        
        # Validate expected check-out is after check-in
        if actual_check_in_date_time and expected_check_out_date:
            if expected_check_out_date <= actual_check_in_date_time.date():
                self.add_error('expected_check_out_date', 'Expected check-out date must be after check-in date.')
        
        # Check room availability
        if room_number and actual_check_in_date_time:
            overlapping_checkins = CheckIn.objects.filter(
                room_number=room_number,
                actual_check_in_date_time__date=actual_check_in_date_time.date()
            )
            if self.instance.pk:
                overlapping_checkins = overlapping_checkins.exclude(pk=self.instance.pk)
            
            if overlapping_checkins.exists():
                self.add_error('room_number', f'Room {room_number.room_number} already has a check-in for this date.')
        
        return cleaned_data
    
    def save(self, commit=True):
        checkin = super().save(commit=False)
        
        # Create new guest if requested
        if self.cleaned_data.get('create_new_guest'):
            guest = Guest.objects.create(
                first_name=self.cleaned_data['guest_first_name'],
                last_name=self.cleaned_data['guest_last_name'],
                email=self.cleaned_data['guest_email'],
                contact_number=self.cleaned_data['guest_phone'],
                address=self.cleaned_data.get('guest_address', ''),
                id_proof_type=self.cleaned_data.get('guest_id_proof_type', 'OTHER'),
                id_proof_number=self.cleaned_data.get('guest_id_proof_number', ''),
                date_of_birth=self.cleaned_data.get('guest_date_of_birth'),  # Can be None now
                gender=self.cleaned_data.get('guest_gender', 'O'),
                nationality='Indian',  # Default nationality
                id_proof_image=self.cleaned_data.get('guest_id_proof_image')
            )
            checkin.guest = guest
        
        # Set default payment status to PAID (no payment processing)
        checkin.payment_status = 'PAID'
        
        if commit:
            checkin.save()
        
        return checkin