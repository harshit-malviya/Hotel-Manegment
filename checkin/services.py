"""
Service classes for enhanced check-in functionality
"""
from django.db import models
from django.utils import timezone
from datetime import timedelta, date
from typing import List, Optional, Dict, Any

from .models import CheckIn
from .enhanced_models import (
    CheckInWorkflow, DigitalKeyCard, NotificationTemplate, 
    NotificationLog, MobileCheckInSession
)
from booking.models import Booking
from guest.models import Guest


class CheckInWorkflowService:
    """Service for managing check-in workflow"""
    
    @staticmethod
    def create_workflow(checkin: CheckIn) -> CheckInWorkflow:
        """Create a new check-in workflow"""
        workflow = CheckInWorkflow.objects.create(
            checkin=checkin,
            current_step='booking_verification',
            workflow_data={
                'created_at': timezone.now().isoformat(),
                'guest_id': checkin.guest.id,
                'room_id': checkin.room_number.id
            }
        )
        return workflow
    
    @staticmethod
    def complete_step(workflow: CheckInWorkflow, step: str, data: Dict[str, Any] = None) -> bool:
        """Complete a workflow step"""
        try:
            workflow.complete_step(step, data)
            return True
        except Exception as e:
            print(f"Error completing workflow step: {e}")
            return False
    
    @staticmethod
    def get_next_step(workflow: CheckInWorkflow) -> Optional[str]:
        """Get the next step in the workflow"""
        if workflow.is_completed:
            return None
        return workflow.current_step
    
    @staticmethod
    def complete_checkin_workflow(workflow: CheckInWorkflow) -> bool:
        """Complete the entire check-in workflow"""
        try:
            # Mark all remaining steps as completed
            remaining_steps = [
                'booking_verification', 'id_verification', 'payment_processing',
                'room_assignment', 'key_generation', 'completion'
            ]
            
            for step in remaining_steps:
                if not workflow.is_step_completed(step):
                    workflow.complete_step(step)
            
            return True
        except Exception as e:
            print(f"Error completing check-in workflow: {e}")
            return False


class DigitalKeyService:
    """Service for managing digital key cards"""
    
    @staticmethod
    def generate_key(checkin: CheckIn, expires_hours: int = 24, key_type: str = 'STANDARD') -> DigitalKeyCard:
        """Generate a digital key card for check-in"""
        expires_at = timezone.now() + timedelta(hours=expires_hours)
        
        # Deactivate any existing active keys
        existing_keys = DigitalKeyCard.objects.filter(checkin=checkin, is_active=True)
        existing_keys.update(is_active=False)
        
        # Create new key
        digital_key = DigitalKeyCard.objects.create(
            checkin=checkin,
            key_type=key_type,
            expires_at=expires_at
        )
        
        return digital_key
    
    @staticmethod
    def validate_key(key_code: str) -> Optional[DigitalKeyCard]:
        """Validate a digital key code"""
        try:
            key = DigitalKeyCard.objects.get(key_code=key_code)
            if key.is_valid():
                key.use_key()
                return key
            return None
        except DigitalKeyCard.DoesNotExist:
            return None
    
    @staticmethod
    def extend_key_expiry(key: DigitalKeyCard, hours: int = 24) -> bool:
        """Extend key expiry time"""
        try:
            key.expires_at = timezone.now() + timedelta(hours=hours)
            key.save()
            return True
        except Exception:
            return False
    
    @staticmethod
    def deactivate_keys_for_checkin(checkin: CheckIn) -> int:
        """Deactivate all keys for a check-in"""
        keys = DigitalKeyCard.objects.filter(checkin=checkin, is_active=True)
        count = keys.count()
        keys.update(is_active=False)
        return count


class NotificationService:
    """Service for handling notifications"""
    
    @staticmethod
    def send_notification(
        template_type: str,
        booking: Optional[Booking] = None,
        checkin: Optional[CheckIn] = None,
        context: Dict[str, Any] = None,
        notification_type: str = 'EMAIL'
    ) -> Optional[NotificationLog]:
        """Send a notification using a template"""
        try:
            # Get the template
            template = NotificationTemplate.objects.get(
                template_type=template_type,
                is_active=True
            )
            
            # Determine recipient
            recipient_email = ''
            recipient_phone = ''
            
            if booking:
                recipient_email = booking.guest.email
                recipient_phone = booking.guest.contact_number
            elif checkin:
                recipient_email = checkin.guest.email
                recipient_phone = checkin.guest.contact_number
            
            if not recipient_email and not recipient_phone:
                return None
            
            # Prepare context
            if context is None:
                context = {}
            
            # Add default context variables
            if booking:
                context.update({
                    'guest_name': booking.guest.full_name,
                    'booking': booking,
                    'checkin_date': booking.check_in_date.strftime('%B %d, %Y'),
                    'checkout_date': booking.check_out_date.strftime('%B %d, %Y'),
                    'total_amount': booking.total_amount,
                    'total_guests': booking.total_guests,
                    'room_type': booking.room.room_type.name if booking.room.room_type else 'Standard Room'
                })
            
            if checkin:
                context.update({
                    'guest_name': checkin.guest.full_name,
                    'checkin_id': checkin.check_in_id,
                    'room_number': checkin.room_number.room_number,
                    'checkin_date': checkin.actual_check_in_date_time.strftime('%B %d, %Y'),
                    'checkout_date': checkin.expected_check_out_date.strftime('%B %d, %Y') if checkin.expected_check_out_date else 'TBD'
                })
            
            # Add hotel name (this could come from settings)
            context['hotel_name'] = 'Your Hotel Name'
            
            # Render template content
            rendered_content = template.render_content(context)
            
            # Create notification log
            notification = NotificationLog.objects.create(
                booking=booking,
                checkin=checkin,
                template=template,
                notification_type=notification_type,
                recipient_email=recipient_email if notification_type in ['EMAIL', 'BOTH'] else '',
                recipient_phone=recipient_phone if notification_type in ['SMS', 'BOTH'] else '',
                subject=rendered_content['subject'],
                content=rendered_content['email_content'] if notification_type in ['EMAIL', 'BOTH'] else rendered_content['sms_content']
            )
            
            # Here you would integrate with actual email/SMS service
            # For now, we'll mark as sent
            notification.mark_sent()
            
            return notification
            
        except NotificationTemplate.DoesNotExist:
            print(f"Notification template not found: {template_type}")
            return None
        except Exception as e:
            print(f"Error sending notification: {e}")
            return None
    
    @staticmethod
    def send_booking_confirmation(booking: Booking) -> Optional[NotificationLog]:
        """Send booking confirmation notification"""
        return NotificationService.send_notification(
            template_type='BOOKING_CONFIRMATION',
            booking=booking,
            notification_type='EMAIL'
        )
    
    @staticmethod
    def send_welcome_message(checkin: CheckIn) -> Optional[NotificationLog]:
        """Send welcome message notification"""
        return NotificationService.send_notification(
            template_type='WELCOME_MESSAGE',
            checkin=checkin,
            notification_type='EMAIL'
        )
    
    @staticmethod
    def send_checkin_reminder(booking: Booking) -> Optional[NotificationLog]:
        """Send check-in reminder notification"""
        return NotificationService.send_notification(
            template_type='CHECKIN_REMINDER',
            booking=booking,
            notification_type='BOTH'
        )
    
    @staticmethod
    def send_payment_reminder(booking: Booking) -> Optional[NotificationLog]:
        """Send payment reminder notification"""
        context = {
            'paid_amount': booking.advance_payment,
            'outstanding_amount': booking.remaining_amount
        }
        return NotificationService.send_notification(
            template_type='PAYMENT_REMINDER',
            booking=booking,
            context=context,
            notification_type='EMAIL'
        )


class MobileCheckInService:
    """Service for mobile check-in functionality"""
    
    @staticmethod
    def create_session(booking: Booking, guest_phone: str, guest_email: str) -> MobileCheckInSession:
        """Create a mobile check-in session"""
        expires_at = timezone.now() + timedelta(hours=2)  # 2-hour session
        
        session = MobileCheckInSession.objects.create(
            booking=booking,
            guest_phone=guest_phone,
            guest_email=guest_email,
            expires_at=expires_at
        )
        
        # Send verification code via SMS/Email
        # This would integrate with actual SMS/Email service
        print(f"Verification code for mobile check-in: {session.verification_code}")
        
        return session
    
    @staticmethod
    def verify_session(session_id: str, verification_code: str) -> Optional[MobileCheckInSession]:
        """Verify a mobile check-in session"""
        try:
            session = MobileCheckInSession.objects.get(session_id=session_id)
            if session.verify_code(verification_code):
                return session
            return None
        except MobileCheckInSession.DoesNotExist:
            return None
    
    @staticmethod
    def complete_mobile_checkin(session: MobileCheckInSession) -> Optional[CheckIn]:
        """Complete mobile check-in process"""
        try:
            # Create check-in record
            checkin = CheckIn.objects.create(
                booking=session.booking,
                guest=session.booking.guest,
                room_number=session.booking.room,
                actual_check_in_date_time=timezone.now(),
                expected_check_out_date=session.booking.check_out_date,
                number_of_guests=session.booking.total_guests,
                total_amount=session.booking.total_amount,
                advance_payment=session.booking.advance_payment,
                payment_status=session.booking.payment_status,
                mobile_checkin=True
            )
            
            # Update booking status
            session.booking.status = 'CHECKED_IN'
            session.booking.actual_check_in_time = timezone.now()
            session.booking.save()
            
            # Update room status
            session.booking.room.status = 'OCCUPIED'
            session.booking.room.save()
            
            # Generate digital key
            digital_key = DigitalKeyService.generate_key(checkin)
            
            # Send welcome notification
            NotificationService.send_welcome_message(checkin)
            
            # Complete session
            session.complete_session()
            
            return checkin
            
        except Exception as e:
            print(f"Error completing mobile check-in: {e}")
            return None
    
    @staticmethod
    def cancel_session(session_id: str) -> bool:
        """Cancel a mobile check-in session"""
        try:
            session = MobileCheckInSession.objects.get(session_id=session_id)
            session.status = 'CANCELLED'
            session.save()
            return True
        except MobileCheckInSession.DoesNotExist:
            return False


class CheckInAnalyticsService:
    """Service for check-in analytics"""
    
    @staticmethod
    def get_daily_checkin_stats(target_date: date = None) -> Dict[str, Any]:
        """Get daily check-in statistics"""
        if target_date is None:
            target_date = date.today()
        
        checkins = CheckIn.objects.filter(actual_check_in_date_time__date=target_date)
        
        return {
            'date': target_date,
            'total_checkins': checkins.count(),
            'walk_in_checkins': checkins.filter(booking__isnull=True).count(),
            'booking_checkins': checkins.filter(booking__isnull=False).count(),
            'mobile_checkins': checkins.filter(mobile_checkin=True).count(),
            'verified_ids': checkins.filter(id_proof_verified=True).count(),
            'paid_checkins': checkins.filter(payment_status='PAID').count(),
            'digital_keys_issued': checkins.filter(digital_key_issued=True).count()
        }
    
    @staticmethod
    def get_checkin_performance_metrics(start_date: date, end_date: date) -> Dict[str, Any]:
        """Get check-in performance metrics for a date range"""
        checkins = CheckIn.objects.filter(
            actual_check_in_date_time__date__gte=start_date,
            actual_check_in_date_time__date__lte=end_date
        )
        
        total_checkins = checkins.count()
        if total_checkins == 0:
            return {
                'start_date': start_date,
                'end_date': end_date,
                'total_checkins': 0,
                'metrics': {}
            }
        
        # Calculate metrics
        id_verification_rate = (checkins.filter(id_proof_verified=True).count() / total_checkins) * 100
        payment_completion_rate = (checkins.filter(payment_status='PAID').count() / total_checkins) * 100
        mobile_checkin_rate = (checkins.filter(mobile_checkin=True).count() / total_checkins) * 100
        
        # Average check-in duration (if available)
        checkins_with_duration = checkins.exclude(checkin_duration__isnull=True)
        avg_duration = None
        if checkins_with_duration.exists():
            total_seconds = sum(
                checkin.checkin_duration.total_seconds() 
                for checkin in checkins_with_duration
            )
            avg_duration = total_seconds / checkins_with_duration.count() / 60  # in minutes
        
        return {
            'start_date': start_date,
            'end_date': end_date,
            'total_checkins': total_checkins,
            'metrics': {
                'id_verification_rate': round(id_verification_rate, 2),
                'payment_completion_rate': round(payment_completion_rate, 2),
                'mobile_checkin_rate': round(mobile_checkin_rate, 2),
                'average_checkin_duration_minutes': round(avg_duration, 2) if avg_duration else None
            }
        }