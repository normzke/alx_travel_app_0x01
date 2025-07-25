from django.contrib import admin
from .models import Listing, Booking, Payment

@admin.register(Listing)
class ListingAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'location', 'owner', 'created_at']
    list_filter = ['created_at', 'price']
    search_fields = ['title', 'description', 'location']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['user', 'listing', 'check_in', 'check_out', 'status', 'created_at']
    list_filter = ['status', 'check_in', 'check_out']
    search_fields = ['user__username', 'listing__title']

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['id', 'booking', 'amount', 'currency', 'status', 'created_at']
    list_filter = ['status', 'currency', 'created_at']
    search_fields = ['booking__user__username', 'booking__listing__title', 'chapa_reference']
    readonly_fields = ['id', 'created_at', 'updated_at'] 