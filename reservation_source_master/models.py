from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal
from guest.models import Guest
from rooms.models import Room
from rate.models import RatePlan


class ReservationSource(models.Model):
    """Model for managing reservation sources like OTAs, websites, etc."""
    
    SOURCE_TYPE_CHOICES = [
        ('OTA', 'Online Travel Agency'),
        ('WEBSITE', 'Website'),
        ('AGENT', 'Travel Agent'),
        ('CORPORATE', 'Corporate'),
        ('DIRECT', 'Direct'),
        ('PHONE', 'Phone'),
        ('EMAIL', 'Email'),
        ('WALK_IN', 'Walk-in'),
        ('OTHER', 'Other'),
    ]
    
    source_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique source identifier"
    )
    
    name = models.CharField(
        max_length=100,
        help_text="Source name (e.g., Booking.com, Expedia, Company Website)"
    )
    
    source_type = models.CharField(
        max_length=20,
        choices=SOURCE_TYPE_CHOICES,
        default='OTHER',
        help_text="Type of reservation source"
    )
    
    contact_person = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Contact person name"
    )
    
    email = models.EmailField(
        blank=True,
        null=True,
        help_text="Contact email"
    )
    
    phone = models.CharField(
        max_length=20,
        blank=True,
        null=True,
        help_text="Contact phone number"
    )
    
    address = models.TextField(
        blank=True,
        null=True,
        help_text="Contact address"
    )
    
    commission_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(0), MaxValueValidator(100)],
        help_text="Commission rate percentage (0-100)"
    )
    
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this source is currently active"
    )
    
    website_url = models.URLField(
        blank=True,
        null=True,
        help_text="Website URL"
    )
    
    notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional notes about this source"
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['name']
        verbose_name = 'Reservation Source'
        verbose_name_plural = 'Reservation Sources'
    
    def __str__(self):
        return f"{self.source_id} - {self.name}"
    
    def save(self, *args, **kwargs):
        if not self.source_id:
            prefix = self.source_type[:3].upper()
            count = ReservationSource.objects.filter(source_type=self.source_type).count() + 1
            self.source_id = f"{prefix}{count:04d}"
        super().save(*args, **kwargs)


# Reservation Source Model
class Booking(models.Model):
    reservation_source = models.ForeignKey(
        'ReservationSource',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='source_bookings',
        help_text="Reservation source (OTA, website, etc.)"
    )