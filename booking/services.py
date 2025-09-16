"""
Service classes for enhanced booking functionality
"""
from django.db import models
from django.utils import timezone
from datetime import timedelta, date
from decimal import Decimal
from typing import List, Optional, Dict, Any

from .models import Booking
from .enhanced_models import (
    BookingWorkflow, RoomAvailabilityCache, GuestPreference, 
    RoomAssignmentRule, PaymentTransaction, BookingAnalytics
)
from rooms.models import Room
from guest.models import Guest


class RoomAvailabilityService:
    """Service for managing room availability"""
    
    @staticmethod
    def check_availability(room: Room, start_date: date, end_date: date) -> bool:
        """Check if a room is available for the given date range"""
        return RoomAvailabilityCache.check_availability(room, start_date, end_date)
    
    @staticmethod
    def get_available_rooms(start_date: date, end_date: date, guest_count: int = 1) -> List[Room]:
        """Get all available rooms for the given date range and guest count"""
        # Get rooms that are not in maintenance or out of order
        available_rooms = Room.objects.filter(
            status__in=['AVAILABLE']
        )
        
        # Filter by capacity
        available_rooms = available_rooms.filter(
            models.Q(room_type__capacity__gte=guest_count) | 
            models.Q(room_type__capacity__isnull=True)
        )
        
        # Check availability cache
        available_room_ids = []
        for room in available_rooms:
            if RoomAvailabilityCache.check_availability(room, start_date, end_date):
                available_room_ids.append(room.id)
        
        return Room.objects.filter(id__in=available_room_ids).select_related('room_type')
    
    @staticmethod
    def update_availability_for_booking(booking: Booking, is_available: bool = False):
        """Update room availability cache for a booking"""
        RoomAvailabilityCache.update_availability(
            room=booking.room,
            start_date=booking.check_in_date,
            end_date=booking.check_out_date,
            is_available=is_available,
            booking_id=booking.id if not is_available else None
        )
    
    @staticmethod
    def refresh_availability_cache(days_ahead: int = 365):
        """Refresh the availability cache for the next N days"""
        from datetime import timedelta
        
        start_date = date.today()
        end_date = start_date + timedelta(days=days_ahead)
        
        # Clear existing cache for the date range
        RoomAvailabilityCache.objects.filter(
            date__gte=start_date,
            date__lte=end_date
        ).delete()
        
        # Get all active bookings
        active_bookings = Booking.objects.filter(
            status__in=['CONFIRMED', 'CHECKED_IN'],
            check_out_date__gte=start_date,
            check_in_date__lte=end_date
        )
        
        # Update cache for each booking
        for booking in active_bookings:
            RoomAvailabilityService.update_availability_for_booking(booking, is_available=False)


class RoomRecommendationService:
    """Service for recommending rooms based on guest preferences"""
    
    @staticmethod
    def get_recommended_rooms(guest: Guest, start_date: date, end_date: date, guest_count: int) -> List[Dict[str, Any]]:
        """Get recommended rooms for a guest based on their preferences"""
        # Get available rooms
        available_rooms = RoomAvailabilityService.get_available_rooms(start_date, end_date, guest_count)
        
        if not available_rooms:
            return []
        
        # Get guest preferences
        try:
            preferences = guest.preferences
        except GuestPreference.DoesNotExist:
            # No preferences, return rooms ordered by room number
            return [{'room': room, 'score': 0, 'reasons': []} for room in available_rooms.order_by('room_number')]
        
        # Score each room based on preferences
        room_recommendations = []
        for room in available_rooms:
            score = preferences.get_preference_score(room)
            reasons = RoomRecommendationService._get_match_reasons(preferences, room)
            
            room_recommendations.append({
                'room': room,
                'score': score,
                'reasons': reasons
            })
        
        # Sort by score (highest first)
        room_recommendations.sort(key=lambda x: x['score'], reverse=True)
        
        return room_recommendations
    
    @staticmethod
    def _get_match_reasons(preferences: GuestPreference, room: Room) -> List[str]:
        """Get reasons why a room matches guest preferences"""
        reasons = []
        
        if preferences.preferred_floor and room.floor == preferences.preferred_floor:
            reasons.append(f"Matches preferred floor ({room.floor})")
        
        if preferences.preferred_view and room.view == preferences.preferred_view:
            reasons.append(f"Matches preferred view ({room.get_view_display()})")
        
        if preferences.preferred_bed_type and room.bed_type == preferences.preferred_bed_type:
            reasons.append(f"Matches preferred bed type ({room.get_bed_type_display()})")
        
        if preferences.quiet_room_preference and room.floor >= 3:
            reasons.append("Higher floor for quieter stay")
        
        return reasons


class BookingWorkflowService:
    """Service for managing booking workflow"""
    
    @staticmethod
    def create_workflow(booking: Booking) -> BookingWorkflow:
        """Create a new booking workflow"""
        workflow = BookingWorkflow.objects.create(
            booking=booking,
            step_completed='guest_info',
            workflow_data={
                'created_at': timezone.now().isoformat(),
                'guest_id': booking.guest.id,
                'room_id': booking.room.id
            }
        )
        return workflow
    
    @staticmethod
    def advance_workflow(workflow: BookingWorkflow, next_step: str, data: Dict[str, Any] = None) -> bool:
        """Advance workflow to the next step"""
        try:
            workflow.advance_step(next_step, data)
            return True
        except Exception as e:
            print(f"Error advancing workflow: {e}")
            return False
    
    @staticmethod
    def complete_workflow(workflow: BookingWorkflow) -> bool:
        """Complete the booking workflow"""
        return BookingWorkflowService.advance_workflow(workflow, 'confirmation', {
            'completed_at': timezone.now().isoformat()
        })


class PaymentService:
    """Service for handling payments"""
    
    @staticmethod
    def create_transaction(
        booking: Optional[Booking] = None,
        checkin: Optional['CheckIn'] = None,
        transaction_type: str = 'BOOKING_ADVANCE',
        amount: Decimal = Decimal('0.00'),
        payment_method: str = 'CASH',
        processed_by: str = ''
    ) -> PaymentTransaction:
        """Create a new payment transaction"""
        transaction = PaymentTransaction.objects.create(
            booking=booking,
            checkin=checkin,
            transaction_type=transaction_type,
            amount=amount,
            payment_method=payment_method,
            processed_by=processed_by
        )
        return transaction
    
    @staticmethod
    def process_payment(transaction: PaymentTransaction, gateway_response: Dict[str, Any] = None) -> bool:
        """Process a payment transaction"""
        try:
            # Here you would integrate with actual payment gateway
            # For now, we'll simulate successful payment
            
            transaction.mark_success(
                gateway_transaction_id=f"GW{timezone.now().strftime('%Y%m%d%H%M%S')}",
                gateway_response=gateway_response or {'status': 'success', 'message': 'Payment processed successfully'}
            )
            
            # Update booking/checkin payment status
            if transaction.booking:
                transaction.booking.advance_payment += transaction.amount
                if transaction.booking.advance_payment >= transaction.booking.total_amount:
                    transaction.booking.payment_status = 'PAID'
                else:
                    transaction.booking.payment_status = 'PARTIAL'
                transaction.booking.save()
            
            if transaction.checkin:
                transaction.checkin.advance_payment += transaction.amount
                if transaction.checkin.advance_payment >= transaction.checkin.total_amount:
                    transaction.checkin.payment_status = 'PAID'
                else:
                    transaction.checkin.payment_status = 'PARTIAL'
                transaction.checkin.save()
            
            return True
        except Exception as e:
            transaction.mark_failed(str(e))
            return False


class AnalyticsService:
    """Service for generating analytics"""
    
    @staticmethod
    def generate_daily_analytics(target_date: date = None) -> Dict[str, Any]:
        """Generate analytics for a specific date"""
        if target_date is None:
            target_date = date.today()
        
        # Generate booking analytics
        booking_analytics = BookingAnalytics.calculate_for_date(target_date)
        
        # Generate check-in analytics
        from checkin.enhanced_models import CheckInAnalytics
        checkin_analytics = CheckInAnalytics.calculate_for_date(target_date)
        
        return {
            'date': target_date,
            'booking_analytics': booking_analytics,
            'checkin_analytics': checkin_analytics
        }
    
    @staticmethod
    def get_occupancy_rate(target_date: date = None) -> Decimal:
        """Get occupancy rate for a specific date"""
        if target_date is None:
            target_date = date.today()
        
        # Get total available rooms
        total_rooms = Room.objects.filter(status='AVAILABLE').count()
        
        if total_rooms == 0:
            return Decimal('0.00')
        
        # Get occupied rooms for the date
        occupied_rooms = Booking.objects.filter(
            check_in_date__lte=target_date,
            check_out_date__gt=target_date,
            status__in=['CONFIRMED', 'CHECKED_IN']
        ).count()
        
        return Decimal((occupied_rooms / total_rooms) * 100).quantize(Decimal('0.01'))
    
    @staticmethod
    def get_revenue_summary(start_date: date, end_date: date) -> Dict[str, Any]:
        """Get revenue summary for a date range"""
        bookings = Booking.objects.filter(
            created_at__date__gte=start_date,
            created_at__date__lte=end_date
        )
        
        total_revenue = sum(booking.total_amount for booking in bookings if booking.total_amount)
        total_bookings = bookings.count()
        confirmed_bookings = bookings.filter(status='CONFIRMED').count()
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_revenue': total_revenue,
            'total_bookings': total_bookings,
            'confirmed_bookings': confirmed_bookings,
            'average_booking_value': total_revenue / total_bookings if total_bookings > 0 else Decimal('0.00'),
            'confirmation_rate': (confirmed_bookings / total_bookings * 100) if total_bookings > 0 else Decimal('0.00')
        }