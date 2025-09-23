from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from guest.models import Guest
from rooms.models import Room
from rate.models import RatePlan

class Booking(models.Model):
    STATUS_CHOICES = [
        ('CONFIRMED', 'Confirmed'),
        ('CHECKED_IN', 'Checked In'),
        ('CHECKED_OUT', 'Checked Out'),
        ('CANCELED', 'Canceled'),
        ('NO_SHOW', 'No Show'),
        ('PENDING', 'Pending'),
    ]
    
    BOOKING_SOURCE_CHOICES = [
        ('DIRECT', 'Direct'),
        ('OTA', 'Online Travel Agency'),
        ('AGENT', 'Travel Agent'),
        ('PHONE', 'Phone'),
        ('EMAIL', 'Email'),
        ('WALK_IN', 'Walk-in'),
        ('CORPORATE', 'Corporate'),
        ('WEBSITE', 'Website'),
    ]
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partial Payment'),
        ('PAID', 'Fully Paid'),
        ('REFUNDED', 'Refunded'),
        ('CANCELLED', 'Cancelled'),
    ]
    
    # Reservation/Booking ID (unique identifier) - Django auto-creates 'id' field
    
    # Foreign Key relationships
    guest = models.ForeignKey(
        Guest, 
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="Guest ID or details"
    )
    room = models.ForeignKey(
        Room, 
        on_delete=models.CASCADE,
        related_name='bookings',
        help_text="Room Type and Number"
    )
    
    # Rate Plan
    rate_plan = models.ForeignKey(
        RatePlan,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings',
        help_text="Rate Plan applied to this booking"
    )
    
    # Reservation Source
    reservation_source = models.ForeignKey(
        'reservation_source_master.ReservationSource',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings',
        help_text="Reservation source (OTA, website, etc.)"
    )
    
    # Corporate/Agent
    corporate_agent = models.ForeignKey(
        'CorporateAgent',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='bookings',
        help_text="Corporate client or travel agent"
    )
    
    # Date and Time fields
    check_in_date = models.DateField(
        help_text="Check-in Date"
    )
    check_out_date = models.DateField(
        help_text="Check-out Date"
    )
    
    # Actual check-in and check-out times
    actual_check_in_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Actual check-in date and time"
    )
    actual_check_out_time = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Actual check-out date and time"
    )
    
    # Number of Guests
    number_of_adults = models.PositiveIntegerField(
        default=1,
        validators=[MinValueValidator(1)],
        help_text="Number of adults"
    )
    number_of_children = models.PositiveIntegerField(
        default=0,
        validators=[MinValueValidator(0)],
        help_text="Number of children"
    )
    
    # Booking Source
    booking_source = models.CharField(
        max_length=20,
        choices=BOOKING_SOURCE_CHOICES,
        default='DIRECT',
        help_text="Booking Source (direct, OTA, agent)"
    )
    
    # Reservation Status
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='CONFIRMED',
        help_text="Reservation Status (confirmed, pending, cancelled)"
    )
    
    # Payment Details
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Total booking amount"
    )
    
    advance_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Advance payment received"
    )
    
    payment_status = models.CharField(
        max_length=20,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING',
        help_text="Payment status"
    )
    
    payment_method = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Payment method used"
    )
    
    # Special Requests
    special_requests = models.TextField(
        blank=True,
        null=True,
        help_text="Special Requests"
    )
    
    # Additional booking details
    confirmation_number = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="External confirmation number (for OTA bookings)"
    )
    
    booking_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Internal booking notes"
    )
    
    # Enhanced fields for improved functionality
    guest_preferences = models.JSONField(
        default=dict,
        help_text="Store booking-specific guest preferences"
    )
    auto_assigned_room = models.BooleanField(
        default=False,
        help_text="Track if room was automatically assigned"
    )
    modification_count = models.IntegerField(
        default=0,
        help_text="Track number of booking modifications"
    )
    cancellation_reason = models.TextField(
        blank=True,
        help_text="Reason for booking cancellation"
    )
    
    # Workflow tracking
    workflow_completed = models.BooleanField(
        default=False,
        help_text="Whether booking workflow is completed"
    )
    
    # Dynamic pricing fields
    base_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Base booking amount before dynamic pricing"
    )
    dynamic_pricing_applied = models.BooleanField(
        default=False,
        help_text="Whether dynamic pricing has been applied"
    )
    pricing_factors = models.JSONField(
        default=dict,
        help_text="Factors used in dynamic pricing calculation"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Booking'
        verbose_name_plural = 'Bookings'
        
        # Ensure no double booking of the same room for overlapping dates
        constraints = [
            models.CheckConstraint(
                check=models.Q(check_out_date__gt=models.F('check_in_date')),
                name='check_out_after_check_in'
            )
        ]
    
    def __str__(self):
        return f"Booking #{self.id} - {self.guest.full_name} - Room {self.room.room_number}"
    
    @property
    def duration_nights(self):
        """Calculate the number of nights for the stay"""
        return (self.check_out_date - self.check_in_date).days
    
    @property
    def total_guests(self):
        """Calculate total number of guests"""
        return self.number_of_adults + self.number_of_children
    
    def calculate_total_amount(self):
        """Calculate the total amount based on room price and duration"""
        nights = self.duration_nights
        if nights > 0:
            # Try rate plan first
            if self.rate_plan:
                try:
                    return self.rate_plan.calculate_total_rate(nights, self.total_guests)
                except:
                    pass  # Fall back to room rates if rate plan calculation fails
            
            # Try room type price
            if hasattr(self.room, 'room_type') and self.room.room_type and self.room.room_type.price_per_night:
                return self.room.room_type.price_per_night * nights
            
            # Fall back to room default rate
            if self.room.rate_default:
                return self.room.rate_default * nights
                
        return Decimal('0.00')
    
    @property
    def remaining_amount(self):
        """Calculate remaining amount to be paid"""
        return self.total_amount - self.advance_payment
    
    @property
    def is_fully_paid(self):
        """Check if booking is fully paid"""
        return self.payment_status == 'PAID' or self.advance_payment >= self.total_amount
    
    def save(self, *args, **kwargs):
        # Auto-calculate total amount if not provided or if it's zero
        if not self.total_amount or self.total_amount == Decimal('0.00'):
            calculated_amount = self.calculate_total_amount()
            if calculated_amount > 0:
                self.total_amount = calculated_amount
        super().save(*args, **kwargs)
    
    def clean(self):
        """Validate booking data"""
        from django.core.exceptions import ValidationError
        
        # Check if check-out date is after check-in date
        if self.check_out_date <= self.check_in_date:
            raise ValidationError('Check-out date must be after check-in date.')
        
        # Check if the room capacity is sufficient
        if hasattr(self.room, 'room_type') and self.room.room_type.capacity:
            if self.total_guests > self.room.room_type.capacity:
                raise ValidationError(
                    f'Total guests ({self.total_guests}) exceeds room capacity ({self.room.room_type.capacity}).'
                )
    
    def is_active(self):
        """Check if booking is currently active (checked in)"""
        return self.status == 'CHECKED_IN'
    
    def can_check_in(self):
        """Check if booking can be checked in"""
        return self.status in ['CONFIRMED', 'PENDING']
    
    def can_check_out(self):
        """Check if booking can be checked out"""
        return self.status == 'CHECKED_IN'
    
    def can_cancel(self):
        """Check if booking can be canceled"""
        return self.status in ['CONFIRMED', 'PENDING']
    
    def check_in(self):
        """Perform check-in operation"""
        from django.utils import timezone
        if self.can_check_in():
            self.status = 'CHECKED_IN'
            self.actual_check_in_time = timezone.now()
            # Update room status to occupied
            self.room.status = 'OCCUPIED'
            self.room.save()
            self.save()
            return True
        return False
    
    def check_out(self):
        """Perform check-out operation"""
        from django.utils import timezone
        if self.can_check_out():
            self.status = 'CHECKED_OUT'
            self.actual_check_out_time = timezone.now()
            # Update room status to available
            self.room.status = 'AVAILABLE'
            self.room.save()
            self.save()
            return True
        return False
    
    @property
    def actual_duration_hours(self):
        """Calculate actual stay duration in hours"""
        if self.actual_check_in_time and self.actual_check_out_time:
            duration = self.actual_check_out_time - self.actual_check_in_time
            return duration.total_seconds() / 3600
        return None
    
    def get_recommended_rooms(self):
        """Get recommended rooms based on guest preferences and availability"""
        from rooms.models import Room
        from booking.enhanced_models import RoomAvailabilityCache
        
        # Use the enhanced availability cache for better performance
        available_rooms = RoomAvailabilityCache.get_available_rooms(
            self.check_in_date, 
            self.check_out_date,
            room_type=getattr(self.room, 'room_type', None) if hasattr(self, 'room') and self.room else None
        )
        
        # Filter by capacity
        total_guests = self.number_of_adults + self.number_of_children
        available_rooms = available_rooms.filter(
            models.Q(room_type__capacity__gte=total_guests) | 
            models.Q(room_type__capacity__isnull=True)
        )
        
        # Get guest preferences if available
        try:
            preferences = self.guest.preferences
            # Score rooms based on preferences
            room_scores = []
            for room in available_rooms:
                score = preferences.get_preference_score(room)
                room_scores.append((room, score))
            
            # Sort by score (highest first)
            room_scores.sort(key=lambda x: x[1], reverse=True)
            return [room for room, score in room_scores]
        except:
            # If no preferences, return available rooms ordered by room number
            return available_rooms.order_by('room_number')
    
    def calculate_dynamic_pricing(self):
        """Calculate pricing with dynamic factors like seasonality, demand, etc."""
        base_amount = self.calculate_total_amount()
        
        # Apply dynamic pricing factors
        # This could include seasonal adjustments, demand-based pricing, etc.
        # For now, return base amount - can be enhanced later
        return base_amount
    
    def increment_modification_count(self):
        """Increment the modification count"""
        self.modification_count += 1
        self.save(update_fields=['modification_count'])
    
    def create_workflow(self):
        """Create a booking workflow if it doesn't exist"""
        from booking.enhanced_models import BookingWorkflow
        
        if not hasattr(self, 'workflow'):
            workflow = BookingWorkflow.objects.create(booking=self)
            return workflow
        return self.workflow
    
    def update_availability_cache(self):
        """Update room availability cache for this booking"""
        from booking.enhanced_models import RoomAvailabilityCache
        from datetime import timedelta
        
        if self.room and self.check_in_date and self.check_out_date:
            # Generate date range
            date_range = []
            current_date = self.check_in_date
            while current_date < self.check_out_date:
                date_range.append(current_date)
                current_date += timedelta(days=1)
            
            # Update cache based on booking status
            is_available = self.status not in ['CONFIRMED', 'CHECKED_IN']
            booking_id = None if is_available else self.id
            
            RoomAvailabilityCache.update_availability(
                self.room, 
                date_range, 
                is_available, 
                booking_id
            )


class CorporateAgent(models.Model):
    """Model for managing corporate clients and travel agents"""
    
    AGENT_TYPE_CHOICES = [
        ('CORPORATE', 'Corporate Client'),
        ('AGENT', 'Travel Agent'),
        ('TOUR_OPERATOR', 'Tour Operator'),
        ('EVENT_PLANNER', 'Event Planner'),
        ('WEDDING_PLANNER', 'Wedding Planner'),
        ('OTHER', 'Other'),
    ]
    
    PAYMENT_TERMS_CHOICES = [
        ('IMMEDIATE', 'Immediate Payment'),
        ('NET_7', 'Net 7 Days'),
        ('NET_15', 'Net 15 Days'),
        ('NET_30', 'Net 30 Days'),
        ('NET_45', 'Net 45 Days'),
        ('NET_60', 'Net 60 Days'),
        ('ADVANCE', 'Advance Payment Required'),
    ]
    
    agent_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique corporate/agent identifier"
    )
    
    name = models.CharField(
        max_length=150,
        help_text="Corporate/Agent name"
    )
    
    agent_type = models.CharField(
        max_length=20,
        choices=AGENT_TYPE_CHOICES,
        default='CORPORATE',
        help_text="Type of corporate client or agent"
    )
    
    contact_person = models.CharField(
        max_length=100,
        help_text="Primary contact person name"
    )
    
    designation = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Contact person designation"
    )
    
    address = models.TextField(
        help_text="Complete address"
    )
    
    city = models.CharField(
        max_length=100,
        help_text="City"
    )
    
    state = models.CharField(
        max_length=100,
        help_text="State/Province"
    )
    
    country = models.CharField(
        max_length=100,
        default='India',
        help_text="Country"
    )
    
    postal_code = models.CharField(
        max_length=20,
        help_text="Postal/ZIP code"
    )
    
    phone = models.CharField(
        max_length=20,
        help_text="Primary phone number"
    )
    
    mobile = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Mobile number"
    )
    
    email = models.EmailField(
        help_text="Primary email address"
    )
    
    website = models.URLField(
        blank=True,
        null=True,
        help_text="Website URL"
    )
    
    business_registration = models.CharField(
        max_length=50,
        blank=True,
        null=True,
        help_text="Business registration number"
    )
    
    gstin = models.CharField(
        max_length=15,
        blank=True,
        null=True,
        help_text="GSTIN (if applicable)"
    )
    
    pan_number = models.CharField(
        max_length=10,
        blank=True,
        null=True,
        help_text="PAN number"
    )
    
    contracted_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Special contracted rate per night"
    )
    
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Commission rate percentage (0-100)"
    )
    
    credit_limit = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        help_text="Credit limit amount"
    )
    
    payment_terms = models.CharField(
        max_length=20,
        choices=PAYMENT_TERMS_CHOICES,
        default='NET_30',
        help_text="Payment terms"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this corporate/agent is currently active"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Corporate/Agent'
        verbose_name_plural = 'Corporate/Agents'
    
    def __str__(self):
        return f"{self.agent_id} - {self.name}"
    
    @property
    def full_address(self):
        """Return formatted full address"""
        address_parts = [
            self.address,
            self.city,
            self.state,
            self.postal_code,
            self.country
        ]
        return ", ".join([part for part in address_parts if part])
    
    def save(self, *args, **kwargs):
        if not self.agent_id:
            prefix = self.agent_type[:3].upper()
            count = CorporateAgent.objects.filter(agent_type=self.agent_type).count() + 1
            self.agent_id = f"{prefix}{count:04d}"
        super().save(*args, **kwargs)