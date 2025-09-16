#!/usr/bin/env python
"""
Create sample rooms for testing room type selection
"""

import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'hotel_management.settings')
django.setup()

from rooms.models import Room, RoomType
from decimal import Decimal

def create_sample_rooms():
    print("Creating sample rooms for testing...")
    
    # Get existing room types
    room_types = list(RoomType.objects.all())
    
    if not room_types:
        print("No room types found. Creating sample room types...")
        
        # Create sample room types
        deluxe = RoomType.objects.create(
            name="Deluxe Room",
            description="Comfortable room with modern amenities",
            price_per_night=Decimal('3500.00'),
            capacity=2,
            bed_type='DOUBLE'
        )
        
        suite = RoomType.objects.create(
            name="Executive Suite",
            description="Spacious suite with separate living area",
            price_per_night=Decimal('6500.00'),
            capacity=4,
            bed_type='KING'
        )
        
        standard = RoomType.objects.create(
            name="Standard Room",
            description="Basic comfortable accommodation",
            price_per_night=Decimal('2500.00'),
            capacity=2,
            bed_type='SINGLE'
        )
        
        room_types = [deluxe, suite, standard]
        print(f"Created {len(room_types)} room types")
    
    # Create sample rooms
    rooms_created = 0
    
    for i, room_type in enumerate(room_types):
        # Create 5 rooms for each type
        for j in range(1, 6):
            room_number = f"{i+2}{j:02d}"  # 201, 202, 203... 301, 302, 303... etc.
            
            # Check if room already exists
            if not Room.objects.filter(room_number=room_number).exists():
                room = Room.objects.create(
                    room_number=room_number,
                    room_type=room_type,
                    floor=i+2,  # Floor 2, 3, 4
                    bed_type=room_type.bed_type,
                    max_occupancy=room_type.capacity,
                    allow_pax=room_type.capacity,
                    status='AVAILABLE',
                    view='CITY' if j <= 2 else 'GARDEN',
                    rate_default=room_type.price_per_night,
                    description=f"{room_type.name} on floor {i+2}"
                )
                rooms_created += 1
                print(f"Created Room {room_number} ({room_type.name})")
    
    print(f"\n✅ Created {rooms_created} new rooms")
    
    # Show summary
    print("\n=== Room Summary ===")
    for room_type in RoomType.objects.all():
        available_count = Room.objects.filter(room_type=room_type, status='AVAILABLE').count()
        total_count = Room.objects.filter(room_type=room_type).count()
        print(f"{room_type.name}: {available_count}/{total_count} available - ₹{room_type.price_per_night}/night")

if __name__ == '__main__':
    create_sample_rooms()