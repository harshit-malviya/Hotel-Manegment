from django.contrib import admin
from .models import ReservationSource

@admin.register(ReservationSource)
class ReservationSourceAdmin(admin.ModelAdmin):
    list_display = ['source_id', 'name', 'source_type', 'contact_person', 'commission_rate', 'is_active', 'created_at']
    list_filter = ['source_type', 'is_active', 'created_at']
    search_fields = ['name', 'source_id', 'contact_person', 'email']
    list_editable = ['is_active']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('source_id', 'name', 'source_type', 'is_active')
        }),
        ('Contact Details', {
            'fields': ('contact_person', 'email', 'phone', 'address', 'website_url')
        }),
        ('Business Details', {
            'fields': ('commission_rate', 'notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )