from django.contrib import admin
from .models import TimeEntry

@admin.register(TimeEntry)
class TimeEntryAdmin(admin.ModelAdmin):
    list_display = ('entry_id', 'name', 'hours', 'created_at')
    search_fields = ('entry_id', 'name')
    ordering = ('-created_at',)
