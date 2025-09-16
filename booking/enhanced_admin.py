"""
Admin configuration for enhanced booking models
"""
from django.contrib import admin
from .enhanced_models import (
    BookingWorkflow, RoomAvailabilityCache, GuestPreference, 
    RoomAssignmentRule, PaymentTransaction, BookingAnalytics, CheckInAnalytics
)


@admin.register(BookingWorkflow)
class BookingWorkflowAdmin(admin.ModelAdmin):
    list_display = ['booking', 'step_completed', 'get_progress_percentage', 'created_at']
    list_filter = ['step_completed', 'created_at']
    search_fields = ['booking__id', 'booking__guest__first_name', 'booking__guest__last_name']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_progress_percentage(self, obj):
        return f"{obj.get_progress_percentage():.1f}%"
    get_progress_percentage.short_description = 'Progress'
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('booking',)
        }),
        ('Workflow Status', {
            'fields': ('step_completed',)
        }),
        ('Workflow Data', {
            'fields': ('workflow_data',),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RoomAvailabilityCache)
class RoomAvailabilityCacheAdmin(admin.ModelAdmin):
    list_display = ['room', 'date', 'is_available', 'booking_id', 'last_updated']
    list_filter = ['is_available', 'date', 'last_updated']
    search_fields = ['room__room_number', 'booking_id']
    date_hierarchy = 'date'
    
    actions = ['mark_available', 'mark_unavailable']
    
    def mark_available(self, request, queryset):
        queryset.update(is_available=True, booking_id=None)
        self.message_user(request, f"{queryset.count()} rooms marked as available.")
    mark_available.short_description = "Mark selected rooms as available"
    
    def mark_unavailable(self, request, queryset):
        queryset.update(is_available=False)
        self.message_user(request, f"{queryset.count()} rooms marked as unavailable.")
    mark_unavailable.short_description = "Mark selected rooms as unavailable"


@admin.register(GuestPreference)
class GuestPreferenceAdmin(admin.ModelAdmin):
    list_display = ['guest', 'preferred_floor', 'preferred_view', 'preferred_bed_type', 'accessibility_needs']
    list_filter = ['preferred_view', 'preferred_bed_type', 'accessibility_needs', 'quiet_room_preference']
    search_fields = ['guest__first_name', 'guest__last_name', 'guest__email']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Guest Information', {
            'fields': ('guest',)
        }),
        ('Room Preferences', {
            'fields': ('preferred_floor', 'preferred_view', 'preferred_bed_type')
        }),
        ('Special Requirements', {
            'fields': ('accessibility_needs', 'quiet_room_preference', 'smoking_preference')
        }),
        ('Additional Requests', {
            'fields': ('special_requests',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(RoomAssignmentRule)
class RoomAssignmentRuleAdmin(admin.ModelAdmin):
    list_display = ['name', 'rule_type', 'priority', 'is_active', 'created_at']
    list_filter = ['rule_type', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    ordering = ['-priority', 'name']
    
    fieldsets = (
        ('Rule Information', {
            'fields': ('name', 'rule_type', 'priority', 'is_active')
        }),
        ('Rule Configuration', {
            'fields': ('conditions', 'description')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(PaymentTransaction)
class PaymentTransactionAdmin(admin.ModelAdmin):
    list_display = ['transaction_id', 'transaction_type', 'amount', 'payment_method', 'status', 'created_at']
    list_filter = ['transaction_type', 'payment_method', 'status', 'created_at']
    search_fields = ['transaction_id', 'booking__id', 'checkin__check_in_id', 'gateway_transaction_id']
    readonly_fields = ['transaction_id', 'created_at', 'updated_at']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Transaction Information', {
            'fields': ('transaction_id', 'transaction_type', 'amount', 'payment_method', 'status')
        }),
        ('Related Records', {
            'fields': ('booking', 'checkin')
        }),
        ('Gateway Information', {
            'fields': ('gateway_transaction_id', 'gateway_response'),
            'classes': ('collapse',)
        }),
        ('Processing Details', {
            'fields': ('processed_by', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_success', 'mark_failed']
    
    def mark_success(self, request, queryset):
        queryset.update(status='SUCCESS')
        self.message_user(request, f"{queryset.count()} transactions marked as successful.")
    mark_success.short_description = "Mark selected transactions as successful"
    
    def mark_failed(self, request, queryset):
        queryset.update(status='FAILED')
        self.message_user(request, f"{queryset.count()} transactions marked as failed.")
    mark_failed.short_description = "Mark selected transactions as failed"


@admin.register(BookingAnalytics)
class BookingAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_bookings', 'confirmed_bookings', 'total_revenue', 'occupancy_rate']
    list_filter = ['date']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Date', {
            'fields': ('date',)
        }),
        ('Booking Statistics', {
            'fields': ('total_bookings', 'confirmed_bookings', 'cancelled_bookings', 'pending_bookings')
        }),
        ('Revenue Metrics', {
            'fields': ('total_revenue', 'average_booking_value')
        }),
        ('Occupancy Metrics', {
            'fields': ('occupancy_rate', 'average_stay_duration')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(CheckInAnalytics)
class CheckInAnalyticsAdmin(admin.ModelAdmin):
    list_display = ['date', 'total_checkins', 'walk_in_checkins', 'payment_completion_rate', 'id_verification_rate']
    list_filter = ['date']
    date_hierarchy = 'date'
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Date', {
            'fields': ('date',)
        }),
        ('Check-in Statistics', {
            'fields': ('total_checkins', 'walk_in_checkins', 'booking_checkins', 'mobile_checkins')
        }),
        ('Performance Metrics', {
            'fields': ('average_checkin_time', 'payment_completion_rate', 'id_verification_rate')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )