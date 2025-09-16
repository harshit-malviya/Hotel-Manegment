"""
Enhanced models for the booking system to support improved workflows,
real-time availability, smart room assignment, and analytics.
"""

from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from decimal import Decimal
import uuid
import json


class BookingWorkflow(models.Model):
    """Track booking creation workflow steps"""
    
    WORKFLOW_STEPS = [
        ('GUEST_INFO', 'Guest Information'),
        ('ROOM_SELECTION', 'Room Selection'),
        ('PAYMENT', 'Payment Processing'),
        ('CONFIRMATION', 'Booking Confirmation'),
    ]
    
    booking = models.OneToOneField(
        'booking.Booking',
        on_delete=models.CASCADE,
        related_name='workflow'
    )
    step_completed = models.CharField(
        max_length=50,
        choices=WORKFLOW_STEPS,
        default='GUEST_INFO',
        help_text="Current completed step in the booking workflow"
    )
    workflow_data = models.JSONField(
        default=dict,
        help_text="Store intermediate data during booking process"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Booking Workflow'
        verbose_name_plural = 'Booking Workflows'
    
    def __str__(self):
        return f"Workflow for Booking #{self.booking.id} - Step: {self.step_completed}"
    
    def advance_to_next_step(self):
        """Advance workflow to the next step"""
        steps = [choice[0] for choice in self.WORKFLOW_STEPS]
        current_index = steps.index(self.step_completed)
        if current_index < len(steps) - 1:
            self.step_completed = steps[current_index + 1]
            self.save()
            return True
        return False
    
    def is_completed(self):
        """Check if workflow is completed"""
        return self.step_completed == 'CONFIRMATION'
    
    def get_progress_percentage(self):
        """Get workflow completion percentage"""
        steps = [choice[0] for choice in self.WORKFLOW_STEPS]
        current_index = steps.index(self.step_completed)
        return ((current_index + 1) / len(steps)) * 100


class RoomAvailabilityCache(models.Model):
    """Cache room availability for performance optimization"""
    
    room = models.ForeignKey(
        'rooms.Room',
        on_delete=models.CASCADE,
        related_name='availability_cache'
    )
    date = models.DateField(
        help_text="Date for which availability is cached"
    )
    is_available = models.BooleanField(
        default=True,
        help_text="Whether room is available on this date"
    )
    booking_id = models.IntegerField(
        null=True,
        blank=True,
        help_text="ID of booking that makes room unavailable"
    )
    last_updated = models.DateTimeField(
        auto_now=True,
        help_text="When this cache entry was last updated"
    )
    
    class Meta:
        unique_together = ['room', 'date']
        verbose_name = 'Room Availability Cache'
        verbose_name_plural = 'Room Availability Cache'
        indexes = [
            models.Index(fields=['date', 'is_available']),
            models.Index(fields=['room', 'date']),
        ]
    
    def __str__(self):
        status = "Available" if self.is_available else "Unavailable"
        return f"Room {self.room.room_number} - {self.date} - {status}"
    
    @classmethod
    def update_availability(cls, room, date_range, is_available, booking_id=None):
        """Update availability cache for a room across a date range"""
        for single_date in date_range:
            cache_entry, created = cls.objects.get_or_create(
                room=room,
                date=single_date,
                defaults={
                    'is_available': is_available,
                    'booking_id': booking_id
                }
            )
            if not created:
                cache_entry.is_available = is_available
                cache_entry.booking_id = booking_id
                cache_entry.save()
    
    @classmethod
    def get_available_rooms(cls, check_in_date, check_out_date, room_type=None):
        """Get available rooms for a date range"""
        from rooms.models import Room
        from datetime import timedelta
        
        # Generate date range
        date_range = []
        current_date = check_in_date
        while current_date < check_out_date:
            date_range.append(current_date)
            current_date += timedelta(days=1)
        
        # Find rooms that are available for all dates in range
        available_room_ids = Room.objects.all().values_list('id', flat=True)
        
        for date in date_range:
            unavailable_on_date = cls.objects.filter(
                date=date,
                is_available=False
            ).values_list('room_id', flat=True)
            available_room_ids = [rid for rid in available_room_ids if rid not in unavailable_on_date]
        
        queryset = Room.objects.filter(id__in=available_room_ids)
        if room_type:
            queryset = queryset.filter(room_type=room_type)
        
        return queryset


class GuestPreference(models.Model):
    """Store guest preferences for room assignment and service customization"""
    
    FLOOR_PREFERENCES = [
        ('LOW', 'Lower Floors (1-3)'),
        ('MID', 'Middle Floors (4-7)'),
        ('HIGH', 'Higher Floors (8+)'),
        ('NO_PREFERENCE', 'No Preference'),
    ]
    
    guest = models.OneToOneField(
        'guest.Guest',
        on_delete=models.CASCADE,
        related_name='preferences'
    )
    preferred_floor = models.IntegerField(
        null=True,
        blank=True,
        help_text="Specific preferred floor number"
    )
    floor_preference = models.CharField(
        max_length=20,
        choices=FLOOR_PREFERENCES,
        default='NO_PREFERENCE',
        help_text="General floor preference"
    )
    preferred_view = models.CharField(
        max_length=20,
        choices=[],  # Will be populated from Room.VIEW_CHOICES
        blank=True,
        help_text="Preferred room view"
    )
    preferred_bed_type = models.CharField(
        max_length=20,
        choices=[],  # Will be populated from Room.BED_TYPE_CHOICES
        blank=True,
        help_text="Preferred bed type"
    )
    accessibility_needs = models.BooleanField(
        default=False,
        help_text="Guest has accessibility requirements"
    )
    quiet_room_preference = models.BooleanField(
        default=False,
        help_text="Guest prefers quiet rooms"
    )
    smoking_preference = models.BooleanField(
        default=False,
        help_text="Guest prefers smoking rooms"
    )
    high_floor_preference = models.BooleanField(
        default=False,
        help_text="Guest prefers higher floors"
    )
    connecting_rooms = models.BooleanField(
        default=False,
        help_text="Guest often needs connecting rooms"
    )
    early_checkin = models.BooleanField(
        default=False,
        help_text="Guest often requests early check-in"
    )
    late_checkout = models.BooleanField(
        default=False,
        help_text="Guest often requests late check-out"
    )
    special_dietary_requirements = models.TextField(
        blank=True,
        help_text="Special dietary requirements or preferences"
    )
    preferred_amenities = models.JSONField(
        default=list,
        help_text="List of preferred amenity IDs"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional preference notes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Guest Preference'
        verbose_name_plural = 'Guest Preferences'
    
    def __str__(self):
        return f"Preferences for {self.guest.full_name}"
    
    def get_preference_score(self, room):
        """Calculate preference score for a room (0-100)"""
        score = 50  # Base score
        
        # Floor preference scoring
        if self.preferred_floor and room.floor == self.preferred_floor:
            score += 20
        elif self.floor_preference == 'LOW' and room.floor <= 3:
            score += 15
        elif self.floor_preference == 'MID' and 4 <= room.floor <= 7:
            score += 15
        elif self.floor_preference == 'HIGH' and room.floor >= 8:
            score += 15
        
        # View preference scoring
        if self.preferred_view and room.view == self.preferred_view:
            score += 15
        
        # Bed type preference scoring
        if self.preferred_bed_type and room.bed_type == self.preferred_bed_type:
            score += 10
        
        # High floor preference
        if self.high_floor_preference and room.floor >= 5:
            score += 5
        
        # Amenity preferences
        if self.preferred_amenities:
            room_amenity_ids = list(room.amenities.values_list('id', flat=True))
            matching_amenities = set(self.preferred_amenities) & set(room_amenity_ids)
            if matching_amenities:
                score += len(matching_amenities) * 2
        
        return min(100, max(0, score))
    
    def update_from_booking_history(self):
        """Update preferences based on guest's booking history"""
        from booking.models import Booking
        
        bookings = Booking.objects.filter(
            guest=self.guest,
            status__in=['CHECKED_OUT', 'CHECKED_IN']
        ).select_related('room').order_by('-created_at')[:10]  # Last 10 bookings
        
        if not bookings:
            return
        
        # Analyze floor preferences
        floors = [b.room.floor for b in bookings if b.room.floor]
        if floors:
            avg_floor = sum(floors) / len(floors)
            if avg_floor <= 3:
                self.floor_preference = 'LOW'
            elif avg_floor <= 7:
                self.floor_preference = 'MID'
            else:
                self.floor_preference = 'HIGH'
        
        # Analyze view preferences
        views = [b.room.view for b in bookings if b.room.view]
        if views:
            most_common_view = max(set(views), key=views.count)
            self.preferred_view = most_common_view
        
        # Analyze bed type preferences
        bed_types = [b.room.bed_type for b in bookings if b.room.bed_type]
        if bed_types:
            most_common_bed = max(set(bed_types), key=bed_types.count)
            self.preferred_bed_type = most_common_bed
        
        self.save()


class RoomAssignmentRule(models.Model):
    """Define rules for automatic room assignment"""
    
    RULE_TYPES = [
        ('LOYALTY_BASED', 'Loyalty Level Based'),
        ('PREFERENCE_BASED', 'Guest Preference Based'),
        ('AVAILABILITY_BASED', 'Availability Based'),
        ('REVENUE_BASED', 'Revenue Optimization'),
        ('CUSTOM', 'Custom Rule'),
    ]
    
    name = models.CharField(
        max_length=100,
        help_text="Rule name for identification"
    )
    rule_type = models.CharField(
        max_length=20,
        choices=RULE_TYPES,
        default='CUSTOM'
    )
    priority = models.IntegerField(
        default=0,
        help_text="Rule priority (higher number = higher priority)"
    )
    conditions = models.JSONField(
        default=dict,
        help_text="Rule conditions in JSON format"
    )
    actions = models.JSONField(
        default=dict,
        help_text="Actions to take when rule matches"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this rule is currently active"
    )
    description = models.TextField(
        blank=True,
        help_text="Description of what this rule does"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-priority', 'name']
        verbose_name = 'Room Assignment Rule'
        verbose_name_plural = 'Room Assignment Rules'
    
    def __str__(self):
        return f"{self.name} (Priority: {self.priority})"
    
    def evaluate(self, booking, available_rooms):
        """Evaluate if this rule applies to the given booking and return scored rooms"""
        if not self.is_active:
            return []
        
        try:
            # This is a simplified rule evaluation
            # In a real implementation, you'd have a more sophisticated rule engine
            scored_rooms = []
            
            for room in available_rooms:
                score = 0
                
                # Loyalty-based scoring
                if self.rule_type == 'LOYALTY_BASED':
                    loyalty_scores = {
                        'DIAMOND': 100,
                        'PLATINUM': 80,
                        'GOLD': 60,
                        'SILVER': 40,
                        'BRONZE': 20
                    }
                    score += loyalty_scores.get(booking.guest.loyalty_level, 0)
                
                # Preference-based scoring
                elif self.rule_type == 'PREFERENCE_BASED':
                    if hasattr(booking.guest, 'preferences'):
                        score += booking.guest.preferences.get_preference_score(room)
                
                # Revenue-based scoring (prefer higher-priced rooms)
                elif self.rule_type == 'REVENUE_BASED':
                    if room.room_type and room.room_type.price_per_night:
                        # Normalize price to 0-100 scale
                        max_price = 10000  # Assume max price for normalization
                        score += (float(room.room_type.price_per_night) / max_price) * 100
                
                if score > 0:
                    scored_rooms.append((room, score))
            
            # Sort by score (highest first)
            scored_rooms.sort(key=lambda x: x[1], reverse=True)
            return scored_rooms
            
        except Exception as e:
            # Log error and return empty list
            print(f"Error evaluating rule {self.name}: {e}")
            return []


class PaymentTransaction(models.Model):
    """Track all payment transactions for bookings and check-ins"""
    
    TRANSACTION_TYPES = [
        ('BOOKING_ADVANCE', 'Booking Advance Payment'),
        ('CHECKIN_PAYMENT', 'Check-in Payment'),
        ('ADDITIONAL_CHARGES', 'Additional Charges'),
        ('REFUND', 'Refund'),
        ('CANCELLATION_FEE', 'Cancellation Fee'),
    ]
    
    PAYMENT_METHODS = [
        ('CASH', 'Cash'),
        ('CARD', 'Credit/Debit Card'),
        ('UPI', 'UPI'),
        ('NET_BANKING', 'Net Banking'),
        ('WALLET', 'Digital Wallet'),
        ('BANK_TRANSFER', 'Bank Transfer'),
        ('CHEQUE', 'Cheque'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PROCESSING', 'Processing'),
        ('SUCCESS', 'Success'),
        ('FAILED', 'Failed'),
        ('CANCELLED', 'Cancelled'),
        ('REFUNDED', 'Refunded'),
    ]
    
    transaction_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique transaction identifier"
    )
    booking = models.ForeignKey(
        'booking.Booking',
        on_delete=models.CASCADE,
        related_name='payment_transactions',
        null=True,
        blank=True,
        help_text="Associated booking"
    )
    checkin = models.ForeignKey(
        'checkin.CheckIn',
        on_delete=models.CASCADE,
        related_name='payment_transactions',
        null=True,
        blank=True,
        help_text="Associated check-in"
    )
    transaction_type = models.CharField(
        max_length=20,
        choices=TRANSACTION_TYPES,
        help_text="Type of transaction"
    )
    amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Transaction amount"
    )
    payment_method = models.CharField(
        max_length=20,
        choices=PAYMENT_METHODS,
        help_text="Payment method used"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="Transaction status"
    )
    gateway_transaction_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="Payment gateway transaction ID"
    )
    gateway_response = models.JSONField(
        default=dict,
        help_text="Payment gateway response data"
    )
    processed_by = models.CharField(
        max_length=100,
        blank=True,
        help_text="Staff member who processed the transaction"
    )
    notes = models.TextField(
        blank=True,
        help_text="Additional transaction notes"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Payment Transaction'
        verbose_name_plural = 'Payment Transactions'
    
    def __str__(self):
        return f"Transaction {self.transaction_id} - {self.amount} - {self.status}"
    
    def save(self, *args, **kwargs):
        if not self.transaction_id:
            # Generate unique transaction ID
            self.transaction_id = f"TXN{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def mark_success(self, gateway_transaction_id=None, gateway_response=None):
        """Mark transaction as successful"""
        self.status = 'SUCCESS'
        if gateway_transaction_id:
            self.gateway_transaction_id = gateway_transaction_id
        if gateway_response:
            self.gateway_response = gateway_response
        self.save()
    
    def mark_failed(self, error_message=None):
        """Mark transaction as failed"""
        self.status = 'FAILED'
        if error_message:
            self.notes = error_message
        self.save()
    
    @property
    def is_successful(self):
        """Check if transaction was successful"""
        return self.status == 'SUCCESS'
    
    @property
    def can_refund(self):
        """Check if transaction can be refunded"""
        return self.status == 'SUCCESS' and self.transaction_type != 'REFUND'


class BookingAnalytics(models.Model):
    """Store daily booking analytics data"""
    
    date = models.DateField(
        unique=True,
        help_text="Date for analytics data"
    )
    total_bookings = models.IntegerField(
        default=0,
        help_text="Total bookings created on this date"
    )
    confirmed_bookings = models.IntegerField(
        default=0,
        help_text="Number of confirmed bookings"
    )
    cancelled_bookings = models.IntegerField(
        default=0,
        help_text="Number of cancelled bookings"
    )
    walk_in_bookings = models.IntegerField(
        default=0,
        help_text="Number of walk-in bookings"
    )
    total_revenue = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Total revenue from bookings"
    )
    average_booking_value = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Average booking value"
    )
    occupancy_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Occupancy rate percentage"
    )
    average_daily_rate = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Average daily rate (ADR)"
    )
    revenue_per_available_room = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        help_text="Revenue per available room (RevPAR)"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Booking Analytics'
        verbose_name_plural = 'Booking Analytics'
    
    def __str__(self):
        return f"Booking Analytics - {self.date}"
    
    @classmethod
    def calculate_for_date(cls, date):
        """Calculate and store analytics for a specific date"""
        from booking.models import Booking
        from rooms.models import Room
        
        # Get bookings for the date
        bookings = Booking.objects.filter(created_at__date=date)
        
        # Calculate metrics
        total_bookings = bookings.count()
        confirmed_bookings = bookings.filter(status='CONFIRMED').count()
        cancelled_bookings = bookings.filter(status='CANCELED').count()
        walk_in_bookings = bookings.filter(booking_source='WALK_IN').count()
        
        # Revenue calculations
        total_revenue = sum(b.total_amount for b in bookings if b.total_amount)
        average_booking_value = total_revenue / total_bookings if total_bookings > 0 else 0
        
        # Occupancy calculations
        total_rooms = Room.objects.filter(status__in=['AVAILABLE', 'OCCUPIED']).count()
        occupied_rooms = bookings.filter(
            status='CHECKED_IN',
            check_in_date__lte=date,
            check_out_date__gt=date
        ).count()
        occupancy_rate = (occupied_rooms / total_rooms * 100) if total_rooms > 0 else 0
        
        # ADR and RevPAR
        average_daily_rate = total_revenue / occupied_rooms if occupied_rooms > 0 else 0
        revenue_per_available_room = total_revenue / total_rooms if total_rooms > 0 else 0
        
        # Create or update analytics record
        analytics, created = cls.objects.get_or_create(
            date=date,
            defaults={
                'total_bookings': total_bookings,
                'confirmed_bookings': confirmed_bookings,
                'cancelled_bookings': cancelled_bookings,
                'walk_in_bookings': walk_in_bookings,
                'total_revenue': total_revenue,
                'average_booking_value': average_booking_value,
                'occupancy_rate': occupancy_rate,
                'average_daily_rate': average_daily_rate,
                'revenue_per_available_room': revenue_per_available_room,
            }
        )
        
        if not created:
            # Update existing record
            analytics.total_bookings = total_bookings
            analytics.confirmed_bookings = confirmed_bookings
            analytics.cancelled_bookings = cancelled_bookings
            analytics.walk_in_bookings = walk_in_bookings
            analytics.total_revenue = total_revenue
            analytics.average_booking_value = average_booking_value
            analytics.occupancy_rate = occupancy_rate
            analytics.average_daily_rate = average_daily_rate
            analytics.revenue_per_available_room = revenue_per_available_room
            analytics.save()
        
        return analytics


class CheckInAnalytics(models.Model):
    """Store daily check-in analytics data"""
    
    date = models.DateField(
        unique=True,
        help_text="Date for analytics data"
    )
    total_checkins = models.IntegerField(
        default=0,
        help_text="Total check-ins completed on this date"
    )
    walk_in_checkins = models.IntegerField(
        default=0,
        help_text="Number of walk-in check-ins"
    )
    mobile_checkins = models.IntegerField(
        default=0,
        help_text="Number of mobile check-ins"
    )
    average_checkin_time = models.DurationField(
        null=True,
        blank=True,
        help_text="Average time taken for check-in process"
    )
    payment_completion_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Percentage of check-ins with completed payments"
    )
    id_verification_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Percentage of check-ins with verified IDs"
    )
    digital_key_issuance_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        help_text="Percentage of check-ins with digital keys issued"
    )
    average_satisfaction_rating = models.DecimalField(
        max_digits=3,
        decimal_places=2,
        null=True,
        blank=True,
        help_text="Average guest satisfaction rating"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-date']
        verbose_name = 'Check-In Analytics'
        verbose_name_plural = 'Check-In Analytics'
    
    def __str__(self):
        return f"Check-In Analytics - {self.date}"
    
    @classmethod
    def calculate_for_date(cls, date):
        """Calculate and store check-in analytics for a specific date"""
        from checkin.models import CheckIn
        from datetime import timedelta
        
        # Get check-ins for the date
        checkins = CheckIn.objects.filter(actual_check_in_date_time__date=date)
        
        # Calculate metrics
        total_checkins = checkins.count()
        walk_in_checkins = checkins.filter(booking__isnull=True).count()
        mobile_checkins = checkins.filter(mobile_checkin=True).count()
        
        # Average check-in time
        checkin_durations = [c.checkin_duration for c in checkins if c.checkin_duration]
        average_checkin_time = None
        if checkin_durations:
            total_seconds = sum(d.total_seconds() for d in checkin_durations)
            average_checkin_time = timedelta(seconds=total_seconds / len(checkin_durations))
        
        # Payment completion rate
        paid_checkins = checkins.filter(payment_status='PAID').count()
        payment_completion_rate = (paid_checkins / total_checkins * 100) if total_checkins > 0 else 0
        
        # ID verification rate
        verified_checkins = checkins.filter(id_proof_verified=True).count()
        id_verification_rate = (verified_checkins / total_checkins * 100) if total_checkins > 0 else 0
        
        # Digital key issuance rate
        digital_key_checkins = checkins.filter(digital_key_issued=True).count()
        digital_key_issuance_rate = (digital_key_checkins / total_checkins * 100) if total_checkins > 0 else 0
        
        # Average satisfaction rating
        ratings = [c.satisfaction_rating for c in checkins if c.satisfaction_rating]
        average_satisfaction_rating = sum(ratings) / len(ratings) if ratings else None
        
        # Create or update analytics record
        analytics, created = cls.objects.get_or_create(
            date=date,
            defaults={
                'total_checkins': total_checkins,
                'walk_in_checkins': walk_in_checkins,
                'mobile_checkins': mobile_checkins,
                'average_checkin_time': average_checkin_time,
                'payment_completion_rate': payment_completion_rate,
                'id_verification_rate': id_verification_rate,
                'digital_key_issuance_rate': digital_key_issuance_rate,
                'average_satisfaction_rating': average_satisfaction_rating,
            }
        )
        
        if not created:
            # Update existing record
            analytics.total_checkins = total_checkins
            analytics.walk_in_checkins = walk_in_checkins
            analytics.mobile_checkins = mobile_checkins
            analytics.average_checkin_time = average_checkin_time
            analytics.payment_completion_rate = payment_completion_rate
            analytics.id_verification_rate = id_verification_rate
            analytics.digital_key_issuance_rate = digital_key_issuance_rate
            analytics.average_satisfaction_rating = average_satisfaction_rating
            analytics.save()
        
        return analytics