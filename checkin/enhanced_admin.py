"""
Admin configuration for enhanced check-in models
"""
from django.contrib import admin
from .enhanced_models import (
    CheckInWorkflow, DigitalKeyCard, NotificationTemplate, 
    NotificationLog, MobileCheckInSession, GuestFeedback
)


@admin.register(CheckInWorkflow)
class CheckInWorkflowAdmin(admin.ModelAdmin):
    list_display = ['checkin', 'current_step', 'get_progress_percentage', 'started_at']
    list_filter = ['current_step', 'started_at']
    search_fields = ['checkin__check_in_id', 'checkin__guest__first_name', 'checkin__guest__last_name']
    readonly_fields = ['started_at', 'completed_at']
    
    def get_progress_percentage(self, obj):
        return f"{obj.get_progress_percentage():.1f}%"
    get_progress_percentage.short_description = 'Progress'
    
    fieldsets = (
        ('Check-in Information', {
            'fields': ('checkin',)
        }),
        ('Workflow Status', {
            'fields': ('current_step', 'steps_completed')
        }),
        ('Workflow Data', {
            'fields': ('workflow_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(DigitalKeyCard)
class DigitalKeyCardAdmin(admin.ModelAdmin):
    list_display = ['key_code', 'checkin', 'is_active', 'expires_at', 'access_count']
    list_filter = ['is_active', 'expires_at', 'created_at']
    search_fields = ['key_code', 'checkin__check_in_id', 'checkin__guest__first_name', 'checkin__guest__last_name']
    readonly_fields = ['key_code', 'qr_code_data', 'access_count', 'last_used_at', 'created_at']
    date_hierarchy = 'expires_at'
    
    fieldsets = (
        ('Key Information', {
            'fields': ('key_code', 'is_active')
        }),
        ('Check-in Details', {
            'fields': ('checkin',)
        }),
        ('Expiration', {
            'fields': ('expires_at',)
        }),
        ('QR Code', {
            'fields': ('qr_code_data',),
            'classes': ('collapse',)
        }),
        ('Usage Statistics', {
            'fields': ('access_count', 'last_used_at'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['deactivate_keys', 'extend_expiry']
    
    def deactivate_keys(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} keys deactivated.")
    deactivate_keys.short_description = "Deactivate selected keys"
    
    def extend_expiry(self, request, queryset):
        from django.utils import timezone
        from datetime import timedelta
        
        new_expiry = timezone.now() + timedelta(hours=24)
        queryset.update(expires_at=new_expiry)
        self.message_user(request, f"{queryset.count()} keys extended by 24 hours.")
    extend_expiry.short_description = "Extend expiry by 24 hours"


@admin.register(NotificationTemplate)
class NotificationTemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'template_type', 'is_active', 'created_at']
    list_filter = ['template_type', 'is_active', 'created_at']
    search_fields = ['name', 'subject']
    
    fieldsets = (
        ('Template Information', {
            'fields': ('name', 'template_type', 'is_active')
        }),
        ('Email Content', {
            'fields': ('subject', 'email_content')
        }),
        ('SMS Content', {
            'fields': ('sms_content',)
        }),
        ('Help Information', {
            'fields': ('variables_help',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(NotificationLog)
class NotificationLogAdmin(admin.ModelAdmin):
    list_display = ['template', 'notification_type', 'recipient_email', 'status', 'sent_at']
    list_filter = ['notification_type', 'status', 'sent_at', 'created_at']
    search_fields = ['recipient_email', 'recipient_phone', 'subject', 'template__name']
    readonly_fields = ['sent_at', 'delivered_at', 'created_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Notification Details', {
            'fields': ('template', 'notification_type')
        }),
        ('Recipients', {
            'fields': ('recipient_email', 'recipient_phone')
        }),
        ('Content', {
            'fields': ('subject', 'content'),
            'classes': ('collapse',)
        }),
        ('Status Information', {
            'fields': ('status', 'sent_at', 'delivered_at', 'retry_count')
        }),
        ('Related Records', {
            'fields': ('booking', 'checkin'),
            'classes': ('collapse',)
        }),
        ('Error Information', {
            'fields': ('error_message',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at',),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['retry_failed_notifications', 'mark_as_sent']
    
    def retry_failed_notifications(self, request, queryset):
        failed_notifications = queryset.filter(status='FAILED')
        # Here you would implement the retry logic
        self.message_user(request, f"{failed_notifications.count()} failed notifications queued for retry.")
    retry_failed_notifications.short_description = "Retry failed notifications"
    
    def mark_as_sent(self, request, queryset):
        queryset.update(status='SENT')
        self.message_user(request, f"{queryset.count()} notifications marked as sent.")
    mark_as_sent.short_description = "Mark as sent"


@admin.register(MobileCheckInSession)
class MobileCheckInSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'booking', 'guest_email', 'status', 'started_at']
    list_filter = ['status', 'started_at']
    search_fields = ['session_id', 'guest_email', 'confirmation_number', 'booking__id']
    readonly_fields = ['session_id', 'started_at', 'completed_at', 'last_activity_at']
    date_hierarchy = 'started_at'
    
    fieldsets = (
        ('Session Information', {
            'fields': ('session_id', 'booking', 'status')
        }),
        ('Guest Details', {
            'fields': ('guest_email', 'confirmation_number')
        }),
        ('Device Information', {
            'fields': ('device_info', 'ip_address'),
            'classes': ('collapse',)
        }),
        ('Session Data', {
            'fields': ('steps_completed', 'session_data'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('started_at', 'completed_at', 'last_activity_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['abandon_sessions']
    
    def abandon_sessions(self, request, queryset):
        queryset.update(status='ABANDONED')
        self.message_user(request, f"{queryset.count()} sessions marked as abandoned.")
    abandon_sessions.short_description = "Mark sessions as abandoned"


@admin.register(GuestFeedback)
class GuestFeedbackAdmin(admin.ModelAdmin):
    list_display = ['checkin', 'feedback_type', 'rating', 'is_resolved', 'created_at']
    list_filter = ['feedback_type', 'rating', 'is_resolved', 'follow_up_required', 'created_at']
    search_fields = ['checkin__guest__first_name', 'checkin__guest__last_name', 'comments']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Feedback Information', {
            'fields': ('checkin', 'feedback_type', 'rating')
        }),
        ('Content', {
            'fields': ('comments', 'is_anonymous')
        }),
        ('Staff Response', {
            'fields': ('staff_response', 'is_resolved', 'follow_up_required')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_resolved', 'mark_follow_up_required']
    
    def mark_resolved(self, request, queryset):
        queryset.update(is_resolved=True)
        self.message_user(request, f"{queryset.count()} feedback items marked as resolved.")
    mark_resolved.short_description = "Mark as resolved"
    
    def mark_follow_up_required(self, request, queryset):
        queryset.update(follow_up_required=True)
        self.message_user(request, f"{queryset.count()} feedback items marked for follow-up.")
    mark_follow_up_required.short_description = "Mark for follow-up"