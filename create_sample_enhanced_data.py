#!/usr/bin/env python
"""
Script to create sample data for enhanced booking and check-in models
"""

import os
import sys
import django
from datetime import datetime, timedelta, date
from decimal import Decimal

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_management.settings')
django.setup()

from booking.models import Booking
from booking.enhanced_models import (
    BookingWorkflow, RoomAvailabilityCache, GuestPreference, 
    RoomAssignmentRule, PaymentTransaction, BookingAnalytics
)
from checkin.models import CheckIn
from checkin.enhanced_models import (
    CheckInWorkflow, DigitalKeyCard, NotificationTemplate, 
    NotificationLog, GuestFeedback
)
from guest.models import Guest
from rooms.models import Room


def create_notification_templates():
    """Create sample notification templates"""
    templates = [
        {
            'name': 'Booking Confirmation Email',
            'template_type': 'BOOKING_CONFIRMATION',
            'subject': 'Booking Confirmation - {{booking.id}}',
            'email_content': '''
            <h2>Booking Confirmation</h2>
            <p>Dear {{guest.full_name}},</p>
            <p>Your booking has been confirmed!</p>
            <ul>
                <li>Booking ID: {{booking.id}}</li>
                <li>Check-in: {{booking.check_in_date}}</li>
                <li>Check-out: {{booking.check_out_date}}</li>
                <li>Room: {{booking.room.room_number}}</li>
                <li>Total Amount: ${{booking.total_amount}}</li>
            </ul>
            <p>Thank you for choosing our hotel!</p>
            ''',
            'sms_content': 'Booking confirmed! ID: {{booking.id}}, Check-in: {{booking.check_in_date}}, Room: {{booking.room.room_number}}'
        },
        {
            'name': 'Welcome Message',
            'template_type': 'WELCOME_MESSAGE',
            'subject': 'Welcome to Our Hotel - {{guest.full_name}}',
            'email_content': '''
            <h2>Welcome!</h2>
            <p>Dear {{guest.full_name}},</p>
            <p>Welcome to our hotel! We hope you have a wonderful stay.</p>
            <p>Your room details:</p>
            <ul>
                <li>Room Number: {{room_number}}</li>
                <li>Check-in ID: {{checkin_id}}</li>
                <li>Check-out Date: {{checkout_date}}</li>
            </ul>
            <p>If you need any assistance, please don't hesitate to contact our front desk.</p>
            ''',
            'sms_content': 'Welcome! Room: {{room_number}}, Check-in ID: {{checkin_id}}. Enjoy your stay!'
        },
        {
            'name': 'Payment Reminder',
            'template_type': 'PAYMENT_REMINDER',
            'subject': 'Payment Reminder - Booking {{booking.id}}',
            'email_content': '''
            <h2>Payment Reminder</h2>
            <p>Dear {{guest.full_name}},</p>
            <p>This is a friendly reminder about your outstanding payment:</p>
            <ul>
                <li>Booking ID: {{booking.id}}</li>
                <li>Outstanding Amount: ${{remaining_amount}}</li>
                <li>Due Date: {{due_date}}</li>
            </ul>
            <p>Please complete your payment at your earliest convenience.</p>
            ''',
            'sms_content': 'Payment reminder: ${{remaining_amount}} due for booking {{booking.id}}. Due: {{due_date}}'
        }
    ]
    
    created_count = 0
    for template_data in templates:
        template, created = NotificationTemplate.objects.get_or_create(
            name=template_data['name'],
            defaults=template_data
        )
        if created:
            created_count += 1
            print(f"Created notification template: {template.name}")
    
    print(f"Created {created_count} new notification templates")


def create_room_assignment_rules():
    """Create sample room assignment rules"""
    rules = [
        {
            'name': 'VIP Guest Priority',
            'rule_type': 'LOYALTY_BASED',
            'priority': 100,
            'description': 'Assign best available rooms to VIP guests',
            'conditions': {
                'guest_loyalty_level': ['DIAMOND', 'PLATINUM'],
                'room_features': ['high_floor', 'best_view']
            }
        },
        {
            'name': 'Accessibility Requirements',
            'rule_type': 'PREFERENCE_BASED',
            'priority': 90,
            'description': 'Assign accessible rooms to guests with accessibility needs',
            'conditions': {
                'accessibility_needs': True,
                'room_features': ['accessible', 'ground_floor']
            }
        },
        {
            'name': 'Quiet Room Preference',
            'rule_type': 'PREFERENCE_BASED',
            'priority': 50,
            'description': 'Assign quiet rooms away from elevators and common areas',
            'conditions': {
                'quiet_room_preference': True,
                'room_location': ['away_from_elevator', 'away_from_lobby']
            }
        }
    ]
    
    created_count = 0
    for rule_data in rules:
        rule, created = RoomAssignmentRule.objects.get_or_create(
            name=rule_data['name'],
            defaults=rule_data
        )
        if created:
            created_count += 1
            print(f"Created room assignment rule: {rule.name}")
    
    print(f"Created {created_count} new room assignment rules")


def create_guest_preferences():
    """Create sample guest preferences for existing guests"""
    guests = Guest.objects.all()[:5]  # Get first 5 guests
    
    created_count = 0
    for guest in guests:
        if not hasattr(guest, 'preferences'):
            preference = GuestPreference.objects.create(
                guest=guest,
                preferred_floor=3 if guest.loyalty_level in ['GOLD', 'PLATINUM', 'DIAMOND'] else None,
                preferred_view='SEA' if guest.loyalty_level == 'DIAMOND' else 'CITY',
                preferred_bed_type='KING' if guest.loyalty_level in ['PLATINUM', 'DIAMOND'] else 'DOUBLE',
                accessibility_needs=False,
                quiet_room_preference=guest.loyalty_level in ['GOLD', 'PLATINUM', 'DIAMOND'],
                high_floor_preference=guest.loyalty_level in ['PLATINUM', 'DIAMOND'],
                notes=f"Auto-generated preferences based on loyalty level: {guest.loyalty_level}"
            )
            created_count += 1
            print(f"Created preferences for guest: {guest.full_name}")
    
    print(f"Created {created_count} guest preferences")


def update_room_availability_cache():
    """Update room availability cache for the next 30 days"""
    rooms = Room.objects.all()
    today = date.today()
    
    cache_entries_created = 0
    for room in rooms:
        for i in range(30):  # Next 30 days
            cache_date = today + timedelta(days=i)
            
            # Check if room is booked on this date
            is_booked = Booking.objects.filter(
                room=room,
                status__in=['CONFIRMED', 'CHECKED_IN'],
                check_in_date__lte=cache_date,
                check_out_date__gt=cache_date
            ).exists()
            
            cache_entry, created = RoomAvailabilityCache.objects.get_or_create(
                room=room,
                date=cache_date,
                defaults={
                    'is_available': not is_booked,
                    'booking_id': None
                }
            )
            
            if created:
                cache_entries_created += 1
    
    print(f"Created {cache_entries_created} room availability cache entries")


def create_sample_workflows():
    """Create sample workflows for existing bookings and check-ins"""
    # Create booking workflows
    bookings = Booking.objects.filter(workflow__isnull=True)[:5]
    booking_workflows_created = 0
    
    for booking in bookings:
        workflow = BookingWorkflow.objects.create(
            booking=booking,
            step_completed='CONFIRMATION' if booking.status == 'CONFIRMED' else 'GUEST_INFO'
        )
        booking_workflows_created += 1
        print(f"Created booking workflow for booking #{booking.id}")
    
    # Create check-in workflows
    checkins = CheckIn.objects.filter(workflow__isnull=True)[:5]
    checkin_workflows_created = 0
    
    for checkin in checkins:
        workflow = CheckInWorkflow.objects.create(
            checkin=checkin,
            current_step='COMPLETION' if checkin.payment_status == 'PAID' else 'PAYMENT_PROCESSING',
            steps_completed=['BOOKING_RETRIEVAL', 'ID_VERIFICATION'] if checkin.id_proof_verified else ['BOOKING_RETRIEVAL']
        )
        checkin_workflows_created += 1
        print(f"Created check-in workflow for check-in {checkin.check_in_id}")
    
    print(f"Created {booking_workflows_created} booking workflows and {checkin_workflows_created} check-in workflows")


def create_sample_analytics():
    """Create sample analytics data for the past week"""
    from booking.enhanced_models import BookingAnalytics, CheckInAnalytics
    
    today = date.today()
    analytics_created = 0
    
    for i in range(7):  # Past 7 days
        analytics_date = today - timedelta(days=i)
        
        # Create booking analytics
        booking_analytics, created = BookingAnalytics.objects.get_or_create(
            date=analytics_date,
            defaults={
                'total_bookings': 5 + i,
                'confirmed_bookings': 4 + i,
                'cancelled_bookings': 1,
                'walk_in_bookings': 2,
                'total_revenue': Decimal('1500.00') + (i * 200),
                'average_booking_value': Decimal('300.00'),
                'occupancy_rate': Decimal('75.5') + i,
                'average_daily_rate': Decimal('250.00'),
                'revenue_per_available_room': Decimal('188.75')
            }
        )
        
        if created:
            analytics_created += 1
        
        # Create check-in analytics
        checkin_analytics, created = CheckInAnalytics.objects.get_or_create(
            date=analytics_date,
            defaults={
                'total_checkins': 4 + i,
                'walk_in_checkins': 1,
                'mobile_checkins': 2,
                'payment_completion_rate': Decimal('85.5') + i,
                'id_verification_rate': Decimal('95.0'),
                'digital_key_issuance_rate': Decimal('60.0') + i,
                'average_satisfaction_rating': Decimal('4.2')
            }
        )
        
        if created:
            analytics_created += 1
    
    print(f"Created {analytics_created} analytics records")


def main():
    """Main function to create all sample data"""
    print("Creating sample enhanced data...")
    
    try:
        create_notification_templates()
        create_room_assignment_rules()
        create_guest_preferences()
        update_room_availability_cache()
        create_sample_workflows()
        create_sample_analytics()
        
        print("\n✅ Sample enhanced data created successfully!")
        print("\nYou can now:")
        print("1. View the enhanced models in Django Admin")
        print("2. Test booking and check-in workflows")
        print("3. Use room availability cache for better performance")
        print("4. Send notifications using templates")
        print("5. View analytics data in the dashboard")
        
    except Exception as e:
        print(f"❌ Error creating sample data: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()