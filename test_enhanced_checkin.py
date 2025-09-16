#!/usr/bin/env python
"""
Test script to verify enhanced check-in functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_management.settings')
django.setup()

from checkin.forms import EnhancedCheckInForm
from guest.models import Guest
from rooms.models import Room

def test_enhanced_checkin_form():
    print("=== Testing Enhanced Check-In Form ===")
    
    # Test form initialization
    form = EnhancedCheckInForm()
    
    print(f"Form fields available:")
    for field_name in form.fields:
        print(f"  - {field_name}: {form.fields[field_name].label}")
    
    # Check guest creation fields
    guest_fields = [field for field in form.fields if field.startswith('guest_')]
    print(f"\nGuest creation fields: {len(guest_fields)}")
    for field in guest_fields:
        print(f"  - {field}")
    
    # Check if create_new_guest field exists
    print(f"\nCreate new guest field exists: {'create_new_guest' in form.fields}")
    
    # Test available rooms
    available_rooms = Room.objects.filter(status='AVAILABLE').count()
    print(f"Available rooms for selection: {available_rooms}")
    
    # Test existing guests
    existing_guests = Guest.objects.count()
    print(f"Existing guests in database: {existing_guests}")
    
    print("\n=== Form Validation Test ===")
    
    # Test form with new guest data
    test_data = {
        'create_new_guest': True,
        'guest_first_name': 'John',
        'guest_last_name': 'Doe',
        'guest_email': 'john.doe@example.com',
        'guest_phone': '+919876543210',
        'guest_address': '123 Test Street',
        'guest_id_proof_type': 'AADHAR',
        'guest_id_proof_number': '123456789012',
        'guest_gender': 'M',
        'room_number': Room.objects.filter(status='AVAILABLE').first().id if Room.objects.filter(status='AVAILABLE').exists() else None,
        'number_of_guests': 1,
        'id_proof_verified': True,
    }
    
    if test_data['room_number']:
        form_with_data = EnhancedCheckInForm(data=test_data)
        print(f"Form with new guest data is valid: {form_with_data.is_valid()}")
        if not form_with_data.is_valid():
            print("Form errors:")
            for field, errors in form_with_data.errors.items():
                print(f"  - {field}: {errors}")
    else:
        print("No available rooms to test with")
    
    print("\n✅ Enhanced check-in form testing complete!")

def test_guest_creation():
    print("\n=== Testing Guest Creation ===")
    
    # Test creating a guest manually
    try:
        guest = Guest.objects.create(
            first_name='Test',
            last_name='Guest',
            email='test.guest@example.com',
            contact_number='+919876543210',
            address='Test Address',
            id_proof_type='AADHAR',
            id_proof_number='123456789012',
            date_of_birth='1990-01-01',
            gender='M',
            nationality='Indian'
        )
        print(f"✅ Guest created successfully: {guest.full_name} (ID: {guest.guest_id})")
        
        # Clean up test guest
        guest.delete()
        print("✅ Test guest cleaned up")
        
    except Exception as e:
        print(f"❌ Error creating guest: {e}")

if __name__ == '__main__':
    test_enhanced_checkin_form()
    test_guest_creation()