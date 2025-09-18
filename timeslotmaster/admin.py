
from django.contrib import admin
from .models import TimeslotMaster

@admin.register(TimeslotMaster)
class TimeslotMasterAdmin(admin.ModelAdmin):
	list_display = ('id', 'name', 'time')
