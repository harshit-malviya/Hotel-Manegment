"""
Management command to create default notification templates
"""
from django.core.management.base import BaseCommand
from checkin.enhanced_models import NotificationTemplate


class Command(BaseCommand):
    help = 'Create default notification templates'

    def handle(self, *args, **options):
        templates = [
            {
                'name': 'Booking Confirmation Email',
                'template_type': 'BOOKING_CONFIRMATION',
                'subject': 'Booking Confirmation - {{ booking.id }} | {{ hotel_name }}',
                'email_content': '''
                <html>
                <body>
                    <h2>Booking Confirmation</h2>
                    <p>Dear {{ guest_name }},</p>
                    
                    <p>Thank you for choosing {{ hotel_name }}! Your booking has been confirmed.</p>
                    
                    <h3>Booking Details:</h3>
                    <ul>
                        <li><strong>Booking ID:</strong> {{ booking.id }}</li>
                        <li><strong>Guest Name:</strong> {{ guest_name }}</li>
                        <li><strong>Check-in Date:</strong> {{ checkin_date }}</li>
                        <li><strong>Check-out Date:</strong> {{ checkout_date }}</li>
                        <li><strong>Room Type:</strong> {{ room_type }}</li>
                        <li><strong>Number of Guests:</strong> {{ total_guests }}</li>
                        <li><strong>Total Amount:</strong> ₹{{ total_amount }}</li>
                    </ul>
                    
                    <p>We look forward to welcoming you!</p>
                    
                    <p>Best regards,<br>{{ hotel_name }} Team</p>
                </body>
                </html>
                ''',
                'sms_content': 'Booking confirmed! ID: {{ booking.id }}, Check-in: {{ checkin_date }}, Room: {{ room_type }}. Welcome to {{ hotel_name }}!',
                'variables_help': 'Available variables: guest_name, booking.id, checkin_date, checkout_date, room_type, total_guests, total_amount, hotel_name'
            },
            {
                'name': 'Welcome Message',
                'template_type': 'WELCOME_MESSAGE',
                'subject': 'Welcome to {{ hotel_name }} - Room {{ room_number }}',
                'email_content': '''
                <html>
                <body>
                    <h2>Welcome to {{ hotel_name }}!</h2>
                    <p>Dear {{ guest_name }},</p>
                    
                    <p>Welcome! We're delighted to have you stay with us.</p>
                    
                    <h3>Your Stay Details:</h3>
                    <ul>
                        <li><strong>Check-in ID:</strong> {{ checkin_id }}</li>
                        <li><strong>Room Number:</strong> {{ room_number }}</li>
                        <li><strong>Check-in Date:</strong> {{ checkin_date }}</li>
                        <li><strong>Expected Check-out:</strong> {{ checkout_date }}</li>
                    </ul>
                    
                    <h3>Hotel Information:</h3>
                    <ul>
                        <li><strong>WiFi:</strong> Available in all rooms</li>
                        <li><strong>Breakfast:</strong> 7:00 AM - 10:00 AM</li>
                        <li><strong>Check-out Time:</strong> 12:00 PM</li>
                        <li><strong>Front Desk:</strong> 24/7 available</li>
                    </ul>
                    
                    <p>If you need any assistance, please don't hesitate to contact our front desk.</p>
                    
                    <p>Enjoy your stay!</p>
                    
                    <p>Best regards,<br>{{ hotel_name }} Team</p>
                </body>
                </html>
                ''',
                'sms_content': 'Welcome to {{ hotel_name }}! Room: {{ room_number }}, Check-in ID: {{ checkin_id }}. Need help? Call front desk. Enjoy your stay!',
                'variables_help': 'Available variables: guest_name, checkin_id, room_number, checkin_date, checkout_date, hotel_name'
            },
            {
                'name': 'Check-in Reminder',
                'template_type': 'CHECKIN_REMINDER',
                'subject': 'Check-in Reminder - {{ hotel_name }}',
                'email_content': '''
                <html>
                <body>
                    <h2>Check-in Reminder</h2>
                    <p>Dear {{ guest_name }},</p>
                    
                    <p>This is a friendly reminder that your check-in date is approaching.</p>
                    
                    <h3>Booking Details:</h3>
                    <ul>
                        <li><strong>Booking ID:</strong> {{ booking.id }}</li>
                        <li><strong>Check-in Date:</strong> {{ checkin_date }}</li>
                        <li><strong>Room Type:</strong> {{ room_type }}</li>
                        <li><strong>Check-in Time:</strong> 2:00 PM onwards</li>
                    </ul>
                    
                    <h3>What to Bring:</h3>
                    <ul>
                        <li>Valid photo ID</li>
                        <li>Booking confirmation</li>
                        <li>Payment method (if balance due)</li>
                    </ul>
                    
                    <p>We're excited to welcome you to {{ hotel_name }}!</p>
                    
                    <p>Best regards,<br>{{ hotel_name }} Team</p>
                </body>
                </html>
                ''',
                'sms_content': 'Reminder: Check-in tomorrow at {{ hotel_name }}. Booking ID: {{ booking.id }}. Bring valid ID. Check-in from 2 PM.',
                'variables_help': 'Available variables: guest_name, booking.id, checkin_date, room_type, hotel_name'
            },
            {
                'name': 'Payment Reminder',
                'template_type': 'PAYMENT_REMINDER',
                'subject': 'Payment Reminder - Booking {{ booking.id }}',
                'email_content': '''
                <html>
                <body>
                    <h2>Payment Reminder</h2>
                    <p>Dear {{ guest_name }},</p>
                    
                    <p>We hope you're enjoying your stay at {{ hotel_name }}!</p>
                    
                    <p>This is a friendly reminder that there is an outstanding balance on your booking.</p>
                    
                    <h3>Payment Details:</h3>
                    <ul>
                        <li><strong>Booking ID:</strong> {{ booking.id }}</li>
                        <li><strong>Total Amount:</strong> ₹{{ total_amount }}</li>
                        <li><strong>Amount Paid:</strong> ₹{{ paid_amount }}</li>
                        <li><strong>Outstanding Balance:</strong> ₹{{ outstanding_amount }}</li>
                    </ul>
                    
                    <p>Please settle the outstanding amount at your earliest convenience at the front desk.</p>
                    
                    <p>Thank you for your cooperation.</p>
                    
                    <p>Best regards,<br>{{ hotel_name }} Team</p>
                </body>
                </html>
                ''',
                'sms_content': 'Payment reminder: Outstanding balance ₹{{ outstanding_amount }} for booking {{ booking.id }}. Please settle at front desk. Thank you!',
                'variables_help': 'Available variables: guest_name, booking.id, total_amount, paid_amount, outstanding_amount, hotel_name'
            },
            {
                'name': 'Check-out Reminder',
                'template_type': 'CHECKOUT_REMINDER',
                'subject': 'Check-out Reminder - {{ hotel_name }}',
                'email_content': '''
                <html>
                <body>
                    <h2>Check-out Reminder</h2>
                    <p>Dear {{ guest_name }},</p>
                    
                    <p>We hope you've had a wonderful stay at {{ hotel_name }}!</p>
                    
                    <p>This is a reminder that your check-out is scheduled for today.</p>
                    
                    <h3>Check-out Information:</h3>
                    <ul>
                        <li><strong>Room Number:</strong> {{ room_number }}</li>
                        <li><strong>Check-out Time:</strong> 12:00 PM</li>
                        <li><strong>Late Check-out:</strong> Available upon request (charges may apply)</li>
                    </ul>
                    
                    <h3>Before You Leave:</h3>
                    <ul>
                        <li>Please settle any outstanding charges at the front desk</li>
                        <li>Return your room key card</li>
                        <li>Check for any personal belongings</li>
                    </ul>
                    
                    <p>Thank you for choosing {{ hotel_name }}. We hope to see you again soon!</p>
                    
                    <p>Best regards,<br>{{ hotel_name }} Team</p>
                </body>
                </html>
                ''',
                'sms_content': 'Check-out reminder: Room {{ room_number }} by 12 PM today. Settle charges at front desk. Thank you for staying at {{ hotel_name }}!',
                'variables_help': 'Available variables: guest_name, room_number, hotel_name'
            }
        ]
        
        created_count = 0
        for template_data in templates:
            template, created = NotificationTemplate.objects.get_or_create(
                name=template_data['name'],
                template_type=template_data['template_type'],
                defaults=template_data
            )
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'Created template: {template.name}')
                )
            else:
                self.stdout.write(
                    self.style.WARNING(f'Template already exists: {template.name}')
                )
        
        self.stdout.write(
            self.style.SUCCESS(f'Successfully created {created_count} notification templates')
        )