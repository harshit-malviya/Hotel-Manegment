from django.db import models
from django.core.validators import RegexValidator

class Guest(models.Model):
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
    ]
    
    ID_PROOF_CHOICES = [
        ('AADHAR', 'Aadhar Card'),
        ('PAN', 'PAN Card'),
        ('PASSPORT', 'Passport'),
        ('DRIVING_LICENSE', 'Driving License'),
        ('VOTER_ID', 'Voter ID'),
        ('OTHER', 'Other'),
    ]
    
    LOYALTY_LEVELS = [
        ('BRONZE', 'Bronze'),
        ('SILVER', 'Silver'),
        ('GOLD', 'Gold'),
        ('PLATINUM', 'Platinum'),
        ('DIAMOND', 'Diamond'),
    ]
    
    # Phone number validator
    phone_regex = RegexValidator(
        regex=r'^\+?1?\d{9,15}$',
        message="Phone number must be entered in the format: '+999999999'. Up to 15 digits allowed."
    )
    
    guest_id = models.AutoField(primary_key=True)
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES)
    address = models.TextField()
    contact_number = models.CharField(validators=[phone_regex], max_length=17)
    email = models.EmailField(unique=True)
    nationality = models.CharField(max_length=100, default='Indian')
    id_proof_type = models.CharField(max_length=20, choices=ID_PROOF_CHOICES)
    id_proof_number = models.CharField(max_length=50)
    id_proof_image = models.ImageField(
        upload_to='guest_id_proofs/',
        blank=True,
        null=True,
        help_text="Upload a clear image of the ID proof document (Max size: 5MB)"
    )
    loyalty_level = models.CharField(max_length=10, choices=LOYALTY_LEVELS, default='BRONZE')
    member_id = models.CharField(max_length=20, blank=True, null=True)
    preferences_notes = models.TextField(blank=True, null=True)
    
    # Enhanced fields for improved functionality
    loyalty_points = models.IntegerField(
        default=0,
        help_text="Current loyalty points balance"
    )
    total_stays = models.IntegerField(
        default=0,
        help_text="Total number of completed stays"
    )
    total_spent = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        help_text="Total amount spent across all bookings"
    )
    last_stay_date = models.DateField(
        null=True,
        blank=True,
        help_text="Date of last completed stay"
    )
    preferred_communication = models.CharField(
        max_length=10,
        choices=[
            ('EMAIL', 'Email'),
            ('SMS', 'SMS'),
            ('BOTH', 'Both'),
            ('NONE', 'None'),
        ],
        default='EMAIL',
        help_text="Preferred communication method"
    )
    marketing_consent = models.BooleanField(
        default=True,
        help_text="Consent for marketing communications"
    )
    
    # VIP and special status
    is_vip = models.BooleanField(
        default=False,
        help_text="VIP guest status"
    )
    vip_notes = models.TextField(
        blank=True,
        help_text="VIP guest special notes and requirements"
    )
    
    # Blacklist and restrictions
    is_blacklisted = models.BooleanField(
        default=False,
        help_text="Guest is blacklisted"
    )
    blacklist_reason = models.TextField(
        blank=True,
        help_text="Reason for blacklisting"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['first_name', 'last_name']
        verbose_name = 'Guest'
        verbose_name_plural = 'Guests'
    
    def __str__(self):
        return f"{self.first_name} {self.last_name} (ID: {self.guest_id})"
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}"
    
    def save(self, *args, **kwargs):
        # Auto-generate member ID if loyalty level is not BRONZE
        if self.loyalty_level != 'BRONZE' and not self.member_id:
            # Only generate if we have a guest_id (after first save)
            if self.guest_id:
                self.member_id = f"{self.loyalty_level[:3]}{str(self.guest_id).zfill(6)}"
        super().save(*args, **kwargs)
        
        # Generate member ID after first save if needed
        if self.loyalty_level != 'BRONZE' and not self.member_id and self.guest_id:
            self.member_id = f"{self.loyalty_level[:3]}{str(self.guest_id).zfill(6)}"
            super().save(update_fields=['member_id'])
    
    def update_loyalty_stats(self):
        """Update loyalty statistics based on booking history"""
        from booking.models import Booking
        from decimal import Decimal
        
        completed_bookings = Booking.objects.filter(
            guest=self,
            status='CHECKED_OUT'
        )
        
        self.total_stays = completed_bookings.count()
        self.total_spent = sum(
            booking.total_amount for booking in completed_bookings 
            if booking.total_amount
        ) or Decimal('0.00')
        
        # Update last stay date
        last_booking = completed_bookings.order_by('-check_out_date').first()
        if last_booking:
            self.last_stay_date = last_booking.check_out_date
        
        # Calculate loyalty points (1 point per dollar spent)
        self.loyalty_points = int(self.total_spent)
        
        # Auto-upgrade loyalty level based on spending
        if self.total_spent >= 50000:
            self.loyalty_level = 'DIAMOND'
        elif self.total_spent >= 25000:
            self.loyalty_level = 'PLATINUM'
        elif self.total_spent >= 10000:
            self.loyalty_level = 'GOLD'
        elif self.total_spent >= 5000:
            self.loyalty_level = 'SILVER'
        else:
            self.loyalty_level = 'BRONZE'
        
        self.save()
    
    def get_preference_score_for_room(self, room):
        """Get preference score for a specific room"""
        try:
            return self.preferences.get_preference_score(room)
        except:
            return 50  # Default neutral score
    
    def create_default_preferences(self):
        """Create default guest preferences if they don't exist"""
        from booking.enhanced_models import GuestPreference
        
        if not hasattr(self, 'preferences'):
            GuestPreference.objects.create(guest=self)
    
    @property
    def can_book(self):
        """Check if guest can make new bookings"""
        return not self.is_blacklisted
    
    @property
    def loyalty_discount_percentage(self):
        """Get loyalty discount percentage based on level"""
        discounts = {
            'BRONZE': 0,
            'SILVER': 5,
            'GOLD': 10,
            'PLATINUM': 15,
            'DIAMOND': 20,
        }
        return discounts.get(self.loyalty_level, 0)