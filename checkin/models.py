from django.db import models
from django.core.validators import RegexValidator
from django.utils import timezone
from booking.models import Booking
from guest.models import Guest
from rooms.models import Room


# class CheckIn(models.Model):
#     """Model for managing guest check-ins"""
    
#     PAYMENT_STATUS_CHOICES = [
#         ('PENDING', 'Pending'),
#         ('PARTIAL', 'Partial Payment'),
#         ('PAID', 'Fully Paid'),
#         ('REFUNDED', 'Refunded'),
#     ]
    
#     GST_CHOICES = [
#         ('INCLUDING', 'Including GST'),
#         ('EXCLUDING', 'Excluding GST')
#     ]
    
#     check_in_id = models.CharField(
#         max_length=20,
#         unique=True,
#         help_text="Unique check-in identifier"
#     )
    
#     # Link to booking or guest (one must be provided)
#     booking = models.ForeignKey(
#         Booking,
#         on_delete=models.CASCADE,
#         related_name='check_ins',
#         blank=True,
#         null=True,
#         help_text="Associated booking (if pre-booked)"
#     )
    
#     guest = models.ForeignKey(
#         Guest,
#         on_delete=models.CASCADE,
#         related_name='check_ins',
#         help_text="Primary guest checking in"
#     )
    
#     actual_check_in_date_time = models.DateTimeField(
#         default=timezone.now,
#         help_text="Actual date and time of check-in"
#     )
    
#     room_number = models.ForeignKey(
#         Room,
#         on_delete=models.CASCADE,
#         related_name='check_ins',
#         help_text="Room assigned for check-in"
#     )
    
#     id_proof_verified = models.BooleanField(
#         default=False,
#         help_text="Whether guest's ID proof has been verified"
#     )
    
#     payment_status = models.CharField(
#         max_length=10,
#         choices=PAYMENT_STATUS_CHOICES,
#         default='PENDING',
#         help_text="Current payment status"
#     )
    
#     assigned_staff = models.CharField(
#         max_length=100,
#         blank=True,
#         null=True,
#         help_text="Staff member who handled the check-in"
#     )
    
#     remarks_notes = models.TextField(
#         blank=True,
#         null=True,
#         help_text="Additional remarks or notes about the check-in"
#     )
    
#     # Additional useful fields
#     expected_check_out_date = models.DateField(
#         blank=True,
#         null=True,
#         help_text="Expected check-out date"
#     )
    
#     number_of_guests = models.PositiveIntegerField(
#         default=1,
#         help_text="Total number of guests checking in"
#     )
    
#     advance_payment = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         default=0.00,
#         help_text="Advance payment received"
#     )
    
#     total_amount = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         default=0.00,
#         help_text="Total amount for the stay"
#     )
    
#     base_tariff = models.DecimalField(
#         max_digits=10, 
#         decimal_places=2,
#         help_text="Base room tariff",
#         default=000.00,
#         null=True


#     )
#     gst_type = models.CharField(
#         max_length=20,
#         choices=GST_CHOICES,
#         default='EXCLUDING',
#         help_text="Whether tariff includes GST"
#     )
#     cgst_rate = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         default=9.00,
#         help_text="CGST rate in percentage"
#     )
#     sgst_rate = models.DecimalField(
#         max_digits=5,
#         decimal_places=2,
#         default=9.00,
#         help_text="SGST rate in percentage"
#     )
#     discount_amount = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         default=0.00,
#         help_text="Discount amount"
#     )
#     final_amount = models.DecimalField(
#         max_digits=10,
#         decimal_places=2,
#         help_text="Final amount after GST and discount",
#         null=True
#     )
    
#     # Enhanced fields for improved functionality
#     digital_key_issued = models.BooleanField(
#         default=False,
#         help_text="Track if digital key card has been issued"
#     )
#     mobile_checkin = models.BooleanField(
#         default=False,
#         help_text="Track if check-in was done via mobile"
#     )
#     checkin_duration = models.DurationField(
#         null=True,
#         blank=True,
#         help_text="Time taken to complete check-in process"
#     )
#     satisfaction_rating = models.IntegerField(
#         null=True,
#         blank=True,
#         help_text="Guest satisfaction rating (1-5)"
#     )
    
#     # Workflow tracking
#     workflow_completed = models.BooleanField(
#         default=False,
#         help_text="Whether check-in workflow is completed"
#     )
    
#     # Additional check-in details
#     checkin_method = models.CharField(
#         max_length=20,
#         choices=[
#             ('FRONT_DESK', 'Front Desk'),
#             ('MOBILE', 'Mobile Check-in'),
#             ('KIOSK', 'Self-Service Kiosk'),
#         ],
#         default='FRONT_DESK',
#         help_text="Method used for check-in"
#     )
    
#     # ID verification details
#     id_verification_method = models.CharField(
#         max_length=20,
#         choices=[
#             ('MANUAL', 'Manual Verification'),
#             ('DIGITAL', 'Digital Verification'),
#             ('AUTOMATED', 'Automated Verification'),
#         ],
#         blank=True,
#         help_text="Method used for ID verification"
#     )
    
#     # Welcome package and amenities
#     welcome_package_provided = models.BooleanField(
#         default=False,
#         help_text="Whether welcome package was provided"
#     )
    
#     # Special requests handling
#     special_requests_fulfilled = models.BooleanField(
#         default=False,
#         help_text="Whether special requests were fulfilled"
#     )
    
#     # Timestamps
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         ordering = ['-actual_check_in_date_time']
#         verbose_name = 'Check-In'
#         verbose_name_plural = 'Check-Ins'
    
#     def __str__(self):
#         return f"Check-In {self.check_in_id} - {self.guest.full_name} - Room {self.room_number.room_number}"
    
#     def calculate_gst(self):
#         """Calculate GST amounts"""
#         if self.gst_type == 'INCLUDING':
#             # For including GST, we need to extract GST from the base_tariff
#             total_gst_rate = (self.cgst_rate + self.sgst_rate) / 100
#             base_without_gst = self.base_tariff / (1 + total_gst_rate)
#             cgst_amount = base_without_gst * (self.cgst_rate / 100)
#             sgst_amount = base_without_gst * (self.sgst_rate / 100)
#         else:
#             # For excluding GST, we add GST to base_tariff
#             cgst_amount = self.base_tariff * (self.cgst_rate / 100)
#             sgst_amount = self.base_tariff * (self.sgst_rate / 100)
        
#         return cgst_amount, sgst_amount

#     def calculate_final_amount(self):
#         """Calculate final amount including GST and discount"""
#         cgst_amount, sgst_amount = self.calculate_gst()
        
#         if self.gst_type == 'INCLUDING':
#             final = self.base_tariff
#         else:
#             final = self.base_tariff + cgst_amount + sgst_amount
        
#         # Apply discount
#         final -= self.discount_amount
        
#         self.final_amount = final
#         return final
    
#     def save(self, *args, **kwargs):
#         # Auto-generate check_in_id if not provided
#         if not self.check_in_id:
#             today = timezone.now().date()
#             date_str = today.strftime('%Y%m%d')
#             count = CheckIn.objects.filter(
#                 actual_check_in_date_time__date=today
#             ).count() + 1
#             self.check_in_id = f"CI{date_str}{count:03d}"
        
#         # Set total amount from booking if available
#         if self.booking and not self.total_amount:
#             self.total_amount = self.booking.total_amount
        
#         # Set expected check-out from booking if available
#         if self.booking and not self.expected_check_out_date:
#             self.expected_check_out_date = self.booking.check_out_date
            
#         self.calculate_final_amount()
#         super().save(*args, **kwargs)
    
#     @property
#     def remaining_amount(self):
#         """Calculate remaining amount to be paid"""
#         return self.total_amount - self.advance_payment
    
#     @property
#     def payment_percentage(self):
#         """Calculate payment completion percentage"""
#         if self.total_amount > 0:
#             return (self.advance_payment / self.total_amount) * 100
#         return 0
    
#     @property
#     def is_walk_in(self):
#         """Check if this is a walk-in guest (no prior booking)"""
#         return self.booking is None
    
#     @property
#     def days_since_checkin(self):
#         """Calculate days since check-in"""
#         return (timezone.now().date() - self.actual_check_in_date_time.date()).days
    
#     def generate_digital_key(self, expires_hours=24):
#         """Generate digital key card for the guest"""
#         from checkin.enhanced_models import DigitalKeyCard
#         from datetime import timedelta
        
#         # Deactivate any existing keys
#         existing_keys = DigitalKeyCard.objects.filter(checkin=self, is_active=True)
#         existing_keys.update(is_active=False)
        
#         # Create new digital key
#         expires_at = timezone.now() + timedelta(hours=expires_hours)
#         digital_key = DigitalKeyCard.objects.create(
#             checkin=self,
#             expires_at=expires_at
#         )
        
#         # Mark that digital key has been issued
#         self.digital_key_issued = True
#         self.save(update_fields=['digital_key_issued'])
        
#         return digital_key
    
#     def send_welcome_notification(self):
#         """Send welcome message to guest"""
#         from checkin.enhanced_models import NotificationTemplate, NotificationLog
        
#         try:
#             # Get welcome message template
#             template = NotificationTemplate.objects.get(
#                 template_type='WELCOME_MESSAGE',
#                 is_active=True
#             )
            
#             # Prepare context for template rendering
#             context = {
#                 'guest_name': self.guest.full_name,
#                 'room_number': self.room_number.room_number,
#                 'checkin_id': self.check_in_id,
#                 'hotel_name': 'Your Hotel Name',  # This could be from settings
#                 'checkin_date': self.actual_check_in_date_time.strftime('%B %d, %Y'),
#                 'checkout_date': self.expected_check_out_date.strftime('%B %d, %Y') if self.expected_check_out_date else 'TBD',
#             }
            
#             # Render template content
#             rendered_content = template.render_content(context)
            
#             # Create notification log entry
#             notification = NotificationLog.objects.create(
#                 checkin=self,
#                 template=template,
#                 notification_type='EMAIL',
#                 recipient_email=self.guest.email,
#                 subject=rendered_content['subject'],
#                 content=rendered_content['email_content']
#             )
            
#             # Here you would integrate with actual email service
#             # For now, just mark as sent
#             notification.mark_sent()
            
#             return notification
#         except NotificationTemplate.DoesNotExist:
#             # Template not found, skip notification
#             pass
#         except Exception as e:
#             # Log error but don't fail the check-in process
#             print(f"Error sending welcome notification: {e}")
        
#         return None
    
#     def calculate_checkin_duration(self, start_time=None):
#         """Calculate and store check-in duration"""
#         if start_time and self.actual_check_in_date_time:
#             duration = self.actual_check_in_date_time - start_time
#             self.checkin_duration = duration
#             self.save(update_fields=['checkin_duration'])
#             return duration
#         return None
    
#     def create_workflow(self):
#         """Create a check-in workflow if it doesn't exist"""
#         from checkin.enhanced_models import CheckInWorkflow
        
#         if not hasattr(self, 'workflow'):
#             workflow = CheckInWorkflow.objects.create(checkin=self)
#             return workflow
#         return self.workflow
    
#     def complete_workflow_step(self, step_name, data=None):
#         """Complete a workflow step"""
#         workflow = self.create_workflow()
#         workflow.complete_step(step_name, data)
#         return workflow