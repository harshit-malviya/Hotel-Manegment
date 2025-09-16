"""
Enhanced models for the check-in system to support streamlined workflows,
digital key management, and notification system.
"""

from django.db import models
from django.utils import timezone
from django.template import Template, Context
import uuid
import secrets
import string

from booking.models import Booking
from guest.models import Guest
from rooms.models import Room



class CheckInWorkflow(models.Model):
    """Track check-in process steps and workflow state"""
    
    WORKFLOW_STEPS = [
        ('BOOKING_RETRIEVAL', 'Booking Information Retrieval'),
        ('ID_VERIFICATION', 'ID Verification'),
        ('PAYMENT_PROCESSING', 'Payment Processing'),
        ('ROOM_ASSIGNMENT', 'Room Assignment'),
        ('KEY_GENERATION', 'Key Card Generation'),
        ('COMPLETION', 'Check-in Completion'),
    ]
    
    checkin = models.OneToOneField(
        'checkin.CheckIn',
        on_delete=models.CASCADE,
        related_name='workflow'
    )
    steps_completed = models.JSONField(
        default=list,
        help_text="List of completed workflow steps"
    )
    current_step = models.CharField(
        max_length=50,
        choices=WORKFLOW_STEPS,
        default='BOOKING_RETRIEVAL',
        help_text="Current step in the check-in workflow"
    )
    workflow_data = models.JSONField(
        default=dict,
        help_text="Store intermediate data during check-in process"
    )
    started_at = models.DateTimeField(
        auto_now_add=True,
        help_text="When the check-in workflow started"
    )
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When the check-in workflow was completed"
    )
    
    class Meta:
        verbose_name = 'Check-In Workflow'
        verbose_name_plural = 'Check-In Workflows'
    
    def __str__(self):
        return f"Workflow for Check-In {self.checkin.check_in_id} - Step: {self.current_step}"
    
    def complete_step(self, step_name, data=None):
        """Mark a workflow step as completed"""
        if step_name not in self.steps_completed:
            self.steps_completed.append(step_name)
        
        if data:
            self.workflow_data.update(data)
        
        # Advance to next step
        steps = [choice[0] for choice in self.WORKFLOW_STEPS]
        try:
            current_index = steps.index(self.current_step)
            if current_index < len(steps) - 1:
                self.current_step = steps[current_index + 1]
        except ValueError:
            pass  # Current step not found in list
        
        # Mark as completed if all steps are done
        if len(self.steps_completed) == len(self.WORKFLOW_STEPS):
            self.completed_at = timezone.now()
        
        self.save()
    
    def is_completed(self):
        """Check if workflow is completed"""
        return self.completed_at is not None
    
    def get_progress_percentage(self):
        """Get workflow completion percentage"""
        return (len(self.steps_completed) / len(self.WORKFLOW_STEPS)) * 100
    
    def get_remaining_steps(self):
        """Get list of remaining workflow steps"""
        all_steps = [choice[0] for choice in self.WORKFLOW_STEPS]
        return [step for step in all_steps if step not in self.steps_completed]


class DigitalKeyCard(models.Model):
    """Digital key card management for mobile check-in"""
    
    checkin = models.ForeignKey(
        'checkin.CheckIn',
        on_delete=models.CASCADE,
        related_name='digital_keys'
    )
    key_code = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique digital key code"
    )
    qr_code_data = models.TextField(
        blank=True,
        help_text="QR code data for mobile scanning"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this key is currently active"
    )
    expires_at = models.DateTimeField(
        help_text="When this key expires"
    )
    access_count = models.IntegerField(
        default=0,
        help_text="Number of times this key has been used"
    )
    last_used_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When this key was last used"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Digital Key Card'
        verbose_name_plural = 'Digital Key Cards'
    
    def __str__(self):
        return f"Digital Key {self.key_code} for {self.checkin.guest.full_name}"
    
    def save(self, *args, **kwargs):
        if not self.key_code:
            # Generate unique key code
            self.key_code = self.generate_key_code()
        
        if not self.qr_code_data:
            # Generate QR code data
            self.qr_code_data = self.generate_qr_data()
        
        super().save(*args, **kwargs)
    
    def generate_key_code(self):
        """Generate a unique key code"""
        while True:
            # Generate 12-character alphanumeric code
            code = ''.join(secrets.choice(string.ascii_uppercase + string.digits) for _ in range(12))
            if not DigitalKeyCard.objects.filter(key_code=code).exists():
                return code
    
    def generate_qr_data(self):
        """Generate QR code data for mobile scanning"""
        import json
        
        qr_data = {
            'key_code': self.key_code,
            'room_number': self.checkin.room_number.room_number,
            'guest_name': self.checkin.guest.full_name,
            'checkin_id': self.checkin.check_in_id,
            'expires_at': self.expires_at.isoformat(),
            'hotel_id': 'HOTEL001',  # This could be from settings
        }
        
        return json.dumps(qr_data)
    
    def is_valid(self):
        """Check if the key is valid and not expired"""
        return self.is_active and timezone.now() < self.expires_at
    
    def use_key(self):
        """Record key usage"""
        if self.is_valid():
            self.access_count += 1
            self.last_used_at = timezone.now()
            self.save()
            return True
        return False
    
    def deactivate(self):
        """Deactivate the key"""
        self.is_active = False
        self.save()


class NotificationTemplate(models.Model):
    """Email/SMS notification templates for various events"""
    
    TEMPLATE_TYPES = [
        ('BOOKING_CONFIRMATION', 'Booking Confirmation'),
        ('CHECKIN_REMINDER', 'Check-in Reminder'),
        ('PAYMENT_REMINDER', 'Payment Reminder'),
        ('WELCOME_MESSAGE', 'Welcome Message'),
        ('CHECKOUT_REMINDER', 'Check-out Reminder'),
        ('DIGITAL_KEY_DELIVERY', 'Digital Key Delivery'),
        ('BOOKING_MODIFICATION', 'Booking Modification'),
        ('CANCELLATION_CONFIRMATION', 'Cancellation Confirmation'),
    ]
    
    NOTIFICATION_CHANNELS = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('BOTH', 'Email and SMS'),
    ]
    
    name = models.CharField(
        max_length=100,
        help_text="Template name for identification"
    )
    template_type = models.CharField(
        max_length=30,
        choices=TEMPLATE_TYPES,
        help_text="Type of notification template"
    )
    channel = models.CharField(
        max_length=10,
        choices=NOTIFICATION_CHANNELS,
        default='EMAIL',
        help_text="Notification delivery channel"
    )
    subject = models.CharField(
        max_length=200,
        help_text="Email subject line (supports template variables)"
    )
    email_content = models.TextField(
        help_text="Email content (supports HTML and template variables)"
    )
    sms_content = models.TextField(
        blank=True,
        help_text="SMS content (plain text, supports template variables)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Whether this template is currently active"
    )
    send_delay_minutes = models.IntegerField(
        default=0,
        help_text="Delay in minutes before sending notification"
    )
    variables_help = models.TextField(
        blank=True,
        help_text="Available template variables and their descriptions"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['template_type', 'name']
        verbose_name = 'Notification Template'
        verbose_name_plural = 'Notification Templates'
    
    def __str__(self):
        return f"{self.name} ({self.template_type})"
    
    def render_content(self, context_data):
        """Render template content with provided context data"""
        try:
            # Render subject
            subject_template = Template(self.subject)
            rendered_subject = subject_template.render(Context(context_data))
            
            # Render email content
            email_template = Template(self.email_content)
            rendered_email = email_template.render(Context(context_data))
            
            # Render SMS content if available
            rendered_sms = ""
            if self.sms_content:
                sms_template = Template(self.sms_content)
                rendered_sms = sms_template.render(Context(context_data))
            
            return {
                'subject': rendered_subject,
                'email_content': rendered_email,
                'sms_content': rendered_sms
            }
        except Exception as e:
            # Return error message if template rendering fails
            return {
                'subject': f"Template Error: {str(e)}",
                'email_content': f"Error rendering template: {str(e)}",
                'sms_content': f"Template error: {str(e)}"
            }


class NotificationLog(models.Model):
    """Track sent notifications for audit and debugging"""
    
    NOTIFICATION_TYPES = [
        ('EMAIL', 'Email'),
        ('SMS', 'SMS'),
        ('PUSH', 'Push Notification'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('SENT', 'Sent'),
        ('FAILED', 'Failed'),
        ('DELIVERED', 'Delivered'),
        ('BOUNCED', 'Bounced'),
    ]
    
    booking = models.ForeignKey(
        'booking.Booking',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
        help_text="Associated booking"
    )
    checkin = models.ForeignKey(
        'checkin.CheckIn',
        on_delete=models.CASCADE,
        related_name='notifications',
        null=True,
        blank=True,
        help_text="Associated check-in"
    )
    template = models.ForeignKey(
        NotificationTemplate,
        on_delete=models.CASCADE,
        related_name='sent_notifications',
        help_text="Template used for this notification"
    )
    notification_type = models.CharField(
        max_length=10,
        choices=NOTIFICATION_TYPES,
        help_text="Type of notification sent"
    )
    recipient_email = models.EmailField(
        blank=True,
        help_text="Recipient email address"
    )
    recipient_phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Recipient phone number"
    )
    subject = models.CharField(
        max_length=200,
        blank=True,
        help_text="Rendered subject line"
    )
    content = models.TextField(
        help_text="Rendered notification content"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='PENDING',
        help_text="Notification delivery status"
    )
    sent_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When notification was sent"
    )
    delivered_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When notification was delivered"
    )
    error_message = models.TextField(
        blank=True,
        help_text="Error message if delivery failed"
    )
    external_id = models.CharField(
        max_length=100,
        blank=True,
        help_text="External service message ID"
    )
    retry_count = models.IntegerField(
        default=0,
        help_text="Number of delivery retry attempts"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Notification Log'
        verbose_name_plural = 'Notification Logs'
    
    def __str__(self):
        recipient = self.recipient_email or self.recipient_phone or "Unknown"
        return f"{self.notification_type} to {recipient} - {self.status}"
    
    def mark_sent(self, external_id=None):
        """Mark notification as sent"""
        self.status = 'SENT'
        self.sent_at = timezone.now()
        if external_id:
            self.external_id = external_id
        self.save()
    
    def mark_delivered(self):
        """Mark notification as delivered"""
        self.status = 'DELIVERED'
        self.delivered_at = timezone.now()
        self.save()
    
    def mark_failed(self, error_message):
        """Mark notification as failed"""
        self.status = 'FAILED'
        self.error_message = error_message
        self.save()
    
    def increment_retry(self):
        """Increment retry count"""
        self.retry_count += 1
        self.save()
    
    @property
    def can_retry(self):
        """Check if notification can be retried"""
        return self.status == 'FAILED' and self.retry_count < 3


class GuestFeedback(models.Model):
    """Store guest feedback and satisfaction ratings"""
    
    FEEDBACK_TYPES = [
        ('CHECKIN', 'Check-in Experience'),
        ('ROOM', 'Room Quality'),
        ('SERVICE', 'Service Quality'),
        ('OVERALL', 'Overall Experience'),
        ('COMPLAINT', 'Complaint'),
        ('SUGGESTION', 'Suggestion'),
    ]
    
    RATING_CHOICES = [
        (1, 'Very Poor'),
        (2, 'Poor'),
        (3, 'Average'),
        (4, 'Good'),
        (5, 'Excellent'),
    ]
    
    checkin = models.ForeignKey(
        'checkin.CheckIn',
        on_delete=models.CASCADE,
        related_name='feedback',
        help_text="Associated check-in"
    )
    feedback_type = models.CharField(
        max_length=20,
        choices=FEEDBACK_TYPES,
        default='OVERALL',
        help_text="Type of feedback"
    )
    rating = models.IntegerField(
        choices=RATING_CHOICES,
        null=True,
        blank=True,
        help_text="Rating from 1-5"
    )
    comments = models.TextField(
        blank=True,
        help_text="Guest comments and feedback"
    )
    is_anonymous = models.BooleanField(
        default=False,
        help_text="Whether feedback is submitted anonymously"
    )
    staff_response = models.TextField(
        blank=True,
        help_text="Staff response to feedback"
    )
    is_resolved = models.BooleanField(
        default=False,
        help_text="Whether issue has been resolved"
    )
    follow_up_required = models.BooleanField(
        default=False,
        help_text="Whether follow-up is required"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Guest Feedback'
        verbose_name_plural = 'Guest Feedback'
    
    def __str__(self):
        rating_text = f" ({self.rating}/5)" if self.rating else ""
        return f"{self.feedback_type} feedback{rating_text} - {self.checkin.guest.full_name}"
    
    @property
    def is_positive(self):
        """Check if feedback is positive (rating >= 4)"""
        return self.rating and self.rating >= 4
    
    @property
    def is_negative(self):
        """Check if feedback is negative (rating <= 2)"""
        return self.rating and self.rating <= 2
    
    @property
    def needs_attention(self):
        """Check if feedback needs immediate attention"""
        return (self.is_negative or 
                self.feedback_type == 'COMPLAINT' or 
                self.follow_up_required)


class MobileCheckInSession(models.Model):
    """Track mobile check-in sessions for analytics and security"""
    
    SESSION_STATUS = [
        ('STARTED', 'Started'),
        ('IN_PROGRESS', 'In Progress'),
        ('COMPLETED', 'Completed'),
        ('ABANDONED', 'Abandoned'),
        ('FAILED', 'Failed'),
    ]
    
    session_id = models.CharField(
        max_length=50,
        unique=True,
        help_text="Unique session identifier"
    )
    booking = models.ForeignKey(
        'booking.Booking',
        on_delete=models.CASCADE,
        related_name='mobile_sessions',
        null=True,
        blank=True,
        help_text="Associated booking"
    )
    guest_email = models.EmailField(
        help_text="Guest email used for session"
    )
    confirmation_number = models.CharField(
        max_length=50,
        blank=True,
        help_text="Booking confirmation number used"
    )
    status = models.CharField(
        max_length=20,
        choices=SESSION_STATUS,
        default='STARTED',
        help_text="Current session status"
    )
    device_info = models.JSONField(
        default=dict,
        help_text="Device and browser information"
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        help_text="Client IP address"
    )
    steps_completed = models.JSONField(
        default=list,
        help_text="List of completed check-in steps"
    )
    session_data = models.JSONField(
        default=dict,
        help_text="Session data and form inputs"
    )
    started_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="When session was completed"
    )
    last_activity_at = models.DateTimeField(
        auto_now=True,
        help_text="Last activity timestamp"
    )
    
    class Meta:
        ordering = ['-started_at']
        verbose_name = 'Mobile Check-In Session'
        verbose_name_plural = 'Mobile Check-In Sessions'
    
    def __str__(self):
        return f"Mobile Session {self.session_id} - {self.status}"
    
    def save(self, *args, **kwargs):
        if not self.session_id:
            self.session_id = f"MCS{timezone.now().strftime('%Y%m%d')}{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)
    
    def complete_session(self, checkin=None):
        """Mark session as completed"""
        self.status = 'COMPLETED'
        self.completed_at = timezone.now()
        if checkin:
            self.session_data['checkin_id'] = checkin.check_in_id
        self.save()
    
    def abandon_session(self):
        """Mark session as abandoned"""
        self.status = 'ABANDONED'
        self.save()
    
    def is_expired(self, timeout_hours=24):
        """Check if session has expired"""
        from datetime import timedelta
        expiry_time = self.started_at + timedelta(hours=timeout_hours)
        return timezone.now() > expiry_time
    
    @property
    def duration(self):
        """Get session duration"""
        end_time = self.completed_at or timezone.now()
        return end_time - self.started_at
    

class CheckIn(models.Model):
    """Model for managing guest check-ins"""
    
    PAYMENT_STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('PARTIAL', 'Partial Payment'),
        ('PAID', 'Fully Paid'),
        ('REFUNDED', 'Refunded'),
    ]
    
    GST_CHOICES = [
        ('INCLUDING', 'Including GST'),
        ('EXCLUDING', 'Excluding GST')
    ]
    
    check_in_id = models.CharField(
        max_length=20,
        unique=True,
        help_text="Unique check-in identifier"
    )
    
    # Link to booking or guest (one must be provided)
    booking = models.ForeignKey(
        Booking,
        on_delete=models.CASCADE,
        related_name='check_ins',
        blank=True,
        null=True,
        help_text="Associated booking (if pre-booked)"
    )
    
    guest = models.ForeignKey(
        Guest,
        on_delete=models.CASCADE,
        related_name='check_ins',
        help_text="Primary guest checking in"
    )
    
    actual_check_in_date_time = models.DateTimeField(
        default=timezone.now,
        help_text="Actual date and time of check-in"
    )
    
    room_number = models.ForeignKey(
        Room,
        on_delete=models.CASCADE,
        related_name='check_ins',
        help_text="Room assigned for check-in"
    )
    
    id_proof_verified = models.BooleanField(
        default=False,
        help_text="Whether guest's ID proof has been verified"
    )
    
    payment_status = models.CharField(
        max_length=10,
        choices=PAYMENT_STATUS_CHOICES,
        default='PENDING',
        help_text="Current payment status"
    )
    
    assigned_staff = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="Staff member who handled the check-in"
    )
    
    remarks_notes = models.TextField(
        blank=True,
        null=True,
        help_text="Additional remarks or notes about the check-in"
    )
    
    # Additional useful fields
    expected_check_out_date = models.DateField(
        blank=True,
        null=True,
        help_text="Expected check-out date"
    )
    
    number_of_guests = models.PositiveIntegerField(
        default=1,
        help_text="Total number of guests checking in"
    )
    
    advance_payment = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Advance payment received"
    )
    
    total_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Total amount for the stay"
    )
    
    base_tariff = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        help_text="Base room tariff",
        default=000.00,
        null=True


    )
    gst_type = models.CharField(
        max_length=20,
        choices=GST_CHOICES,
        default='EXCLUDING',
        help_text="Whether tariff includes GST"
    )
    cgst_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=9.00,
        help_text="CGST rate in percentage"
    )
    sgst_rate = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=9.00,
        help_text="SGST rate in percentage"
    )
    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0.00,
        help_text="Discount amount"
    )
    final_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        help_text="Final amount after GST and discount",
        null=True
    )
    
    # Enhanced fields for improved functionality
    digital_key_issued = models.BooleanField(
        default=False,
        help_text="Track if digital key card has been issued"
    )
    mobile_checkin = models.BooleanField(
        default=False,
        help_text="Track if check-in was done via mobile"
    )
    checkin_duration = models.DurationField(
        null=True,
        blank=True,
        help_text="Time taken to complete check-in process"
    )
    satisfaction_rating = models.IntegerField(
        null=True,
        blank=True,
        help_text="Guest satisfaction rating (1-5)"
    )
    
    # Workflow tracking
    workflow_completed = models.BooleanField(
        default=False,
        help_text="Whether check-in workflow is completed"
    )
    
    # Additional check-in details
    checkin_method = models.CharField(
        max_length=20,
        choices=[
            ('FRONT_DESK', 'Front Desk'),
            ('MOBILE', 'Mobile Check-in'),
            ('KIOSK', 'Self-Service Kiosk'),
        ],
        default='FRONT_DESK',
        help_text="Method used for check-in"
    )
    
    # ID verification details
    id_verification_method = models.CharField(
        max_length=20,
        choices=[
            ('MANUAL', 'Manual Verification'),
            ('DIGITAL', 'Digital Verification'),
            ('AUTOMATED', 'Automated Verification'),
        ],
        blank=True,
        help_text="Method used for ID verification"
    )
    
    # Welcome package and amenities
    welcome_package_provided = models.BooleanField(
        default=False,
        help_text="Whether welcome package was provided"
    )
    
    # Special requests handling
    special_requests_fulfilled = models.BooleanField(
        default=False,
        help_text="Whether special requests were fulfilled"
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-actual_check_in_date_time']
        verbose_name = 'Check-In'
        verbose_name_plural = 'Check-Ins'
    
    def __str__(self):
        return f"Check-In {self.check_in_id} - {self.guest.full_name} - Room {self.room_number.room_number}"
    
    def calculate_gst(self):
        """Calculate GST amounts"""
        if self.gst_type == 'EXCLUDING':
            # For including GST, we need to extract GST from the base_tariff
            total_gst_rate = (self.cgst_rate + self.sgst_rate) / 100
            base_without_gst = self.base_tariff / (1 + total_gst_rate)
            cgst_amount = base_without_gst * (self.cgst_rate / 100)
            sgst_amount = base_without_gst * (self.sgst_rate / 100)
        else:
            # For excluding GST, we add GST to base_tariff
            cgst_amount = self.base_tariff * (self.cgst_rate / 100)
            sgst_amount = self.base_tariff * (self.sgst_rate / 100)
        
        return cgst_amount, sgst_amount

    def calculate_final_amount(self):
        """Calculate final amount including GST and discount"""
        cgst_amount, sgst_amount = self.calculate_gst()
        
        if self.gst_type == 'EXCLUDING':
            final = self.base_tariff
        else:
            final = self.base_tariff + cgst_amount + sgst_amount
        
        # Apply discount
        final -= self.discount_amount
        
        self.final_amount = final
        return final
    
    def save(self, *args, **kwargs):
        # Auto-generate check_in_id if not provided
        if not self.check_in_id:
            today = timezone.now().date()
            date_str = today.strftime('%Y%m%d')
            count = CheckIn.objects.filter(
                actual_check_in_date_time__date=today
            ).count() + 1
            self.check_in_id = f"CI{date_str}{count:03d}"
        
        # Set total amount from booking if available
        if self.booking and not self.total_amount:
            self.total_amount = self.booking.total_amount
        
        # Set expected check-out from booking if available
        if self.booking and not self.expected_check_out_date:
            self.expected_check_out_date = self.booking.check_out_date
            
        self.calculate_final_amount()
        super().save(*args, **kwargs)
    
    @property
    def remaining_amount(self):
        """Calculate remaining amount to be paid"""
        return self.total_amount - self.advance_payment
    
    @property
    def payment_percentage(self):
        """Calculate payment completion percentage"""
        if self.total_amount > 0:
            return (self.advance_payment / self.total_amount) * 100
        return 0
    
    @property
    def is_walk_in(self):
        """Check if this is a walk-in guest (no prior booking)"""
        return self.booking is None
    
    @property
    def days_since_checkin(self):
        """Calculate days since check-in"""
        return (timezone.now().date() - self.actual_check_in_date_time.date()).days
    
    def generate_digital_key(self, expires_hours=24):
        """Generate digital key card for the guest"""
        from checkin.enhanced_models import DigitalKeyCard
        from datetime import timedelta
        
        # Deactivate any existing keys
        existing_keys = DigitalKeyCard.objects.filter(checkin=self, is_active=True)
        existing_keys.update(is_active=False)
        
        # Create new digital key
        expires_at = timezone.now() + timedelta(hours=expires_hours)
        digital_key = DigitalKeyCard.objects.create(
            checkin=self,
            expires_at=expires_at
        )
        
        # Mark that digital key has been issued
        self.digital_key_issued = True
        self.save(update_fields=['digital_key_issued'])
        
        return digital_key
    
    def send_welcome_notification(self):
        """Send welcome message to guest"""
        from checkin.enhanced_models import NotificationTemplate, NotificationLog
        
        try:
            # Get welcome message template
            template = NotificationTemplate.objects.get(
                template_type='WELCOME_MESSAGE',
                is_active=True
            )
            
            # Prepare context for template rendering
            context = {
                'guest_name': self.guest.full_name,
                'room_number': self.room_number.room_number,
                'checkin_id': self.check_in_id,
                'hotel_name': 'Your Hotel Name',  # This could be from settings
                'checkin_date': self.actual_check_in_date_time.strftime('%B %d, %Y'),
                'checkout_date': self.expected_check_out_date.strftime('%B %d, %Y') if self.expected_check_out_date else 'TBD',
            }
            
            # Render template content
            rendered_content = template.render_content(context)
            
            # Create notification log entry
            notification = NotificationLog.objects.create(
                checkin=self,
                template=template,
                notification_type='EMAIL',
                recipient_email=self.guest.email,
                subject=rendered_content['subject'],
                content=rendered_content['email_content']
            )
            
            # Here you would integrate with actual email service
            # For now, just mark as sent
            notification.mark_sent()
            
            return notification
        except NotificationTemplate.DoesNotExist:
            # Template not found, skip notification
            pass
        except Exception as e:
            # Log error but don't fail the check-in process
            print(f"Error sending welcome notification: {e}")
        
        return None
    
    def calculate_checkin_duration(self, start_time=None):
        """Calculate and store check-in duration"""
        if start_time and self.actual_check_in_date_time:
            duration = self.actual_check_in_date_time - start_time
            self.checkin_duration = duration
            self.save(update_fields=['checkin_duration'])
            return duration
        return None
    
    def create_workflow(self):
        """Create a check-in workflow if it doesn't exist"""
        from checkin.enhanced_models import CheckInWorkflow
        
        if not hasattr(self, 'workflow'):
            workflow = CheckInWorkflow.objects.create(checkin=self)
            return workflow
        return self.workflow
    
    def complete_workflow_step(self, step_name, data=None):
        """Complete a workflow step"""
        workflow = self.create_workflow()
        workflow.complete_step(step_name, data)
        return workflow