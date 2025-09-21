from django.contrib import admin
from .models import DiscountMaster

@admin.register(DiscountMaster)
class DiscountMasterAdmin(admin.ModelAdmin):
    list_display = ('discount_id', 'description', 'discount_value', 'temporary_price')
    search_fields = ('description', 'discount_value')