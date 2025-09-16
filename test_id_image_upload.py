#!/usr/bin/env python
"""
Test script to verify ID image upload functionality
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_management.settings')
django.setup()

from checkin.forms import EnhancedCheckInForm
from django.core.files.uploadedfile import SimpleUploadedFile

def test_id_image_upload():
    print("=== Testing ID Image Upload ===")
    
    # Test form with ID image field
    form = EnhancedCheckInForm()
    
    print(f"ID image field exists: {'guest_id_proof_image' in form.fields}")
    print(f"ID image field type: {type(form.fields['guest_id_proof_image'])}")
    print(f"ID image field required: {form.fields['guest_id_proof_image'].required}")
    
    # Test form validation with image
    print("\n=== Testing Form with Image Data ===")
    
    # Create a mock image file
    image_content = b'fake_image_content'
    mock_image = SimpleUploadedFile(
        "test_id.jpg", 
        image_content, 
        content_type="image/jpeg"
    )
    
    test_data = {
        'create_new_guest': True,
        'guest_first_name': 'Test',
        'guest_last_name': 'User',
        'guest_email': 'test.user@example.com',
        'guest_phone': '+919876543210',
        'guest_address': 'Test Address',
        'guest_id_proof_type': 'AADHAR',
        'guest_id_proof_number': '123456789012',
        'guest_gender': 'M',
        'number_of_guests': 1,
        'id_proof_verified': True,
    }
    
    test_files = {
        'guest_id_proof_image': mock_image
    }
    
    # Get an available room for testing
    from rooms.models import Room
    available_room = Room.objects.filter(status='AVAILABLE').first()
    
    if available_room:
        test_data['room_number'] = available_room.id
        
        form_with_image = EnhancedCheckInForm(data=test_data, files=test_files)
        print(f"Form with image data is valid: {form_with_image.is_valid()}")
        
        if not form_with_image.is_valid():
            print("Form errors:")
            for field, errors in form_with_image.errors.items():
                print(f"  - {field}: {errors}")
        else:
            print("✅ Form validation passed with image upload!")
    else:
        print("❌ No available rooms to test with")
    
    print("\n✅ ID image upload testing complete!")

if __name__ == '__main__':
    test_id_image_upload()