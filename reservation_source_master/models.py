from django.db import models
import uuid

class ReservationSource(models.Model):
    SOURCE_TYPE_CHOICES = [
        ('OTA', 'Online Travel Agency'),
        ('DIRECT', 'Direct Booking'),
        ('CORPORATE', 'Corporate'),
        ('TRAVEL_AGENT', 'Travel Agent'),
        ('OTHER', 'Other')
    ]
    
    source_id = models.CharField(max_length=50, unique=True, blank=True)
    name = models.CharField(max_length=100)
    source_type = models.CharField(max_length=20, choices=SOURCE_TYPE_CHOICES)
    contact_person = models.CharField(max_length=100, blank=True)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)
    commission_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0)
    is_active = models.BooleanField(default=True)
    website_url = models.URLField(blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def save(self, *args, **kwargs):
        if not self.source_id:
            # Generate a unique source ID
            self.source_id = f"RS{str(uuid.uuid4())[:8].upper()}"
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Reservation Source"
        verbose_name_plural = "Reservation Sources"
        ordering = ['name']
