from django.contrib import admin
from .models import DailyEvent, RoomType, Room, Booking, ContactMessage,Login

@admin.register(RoomType)
class RoomTypeAdmin(admin.ModelAdmin):
    list_display = ['name', 'price_per_night', 'capacity']
    list_filter = ['capacity']
    search_fields = ['name']

@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display = ['room_number', 'room_type', 'floor', 'is_available']
    list_filter = ['room_type', 'is_available', 'floor']
    search_fields = ['room_number']

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name','customer_phone', 'room', 'check_in_date', 'check_out_date', 'status', 'total_amount']
    list_filter = ['status', 'check_in_date', 'created_at']
    search_fields = ['customer_name', 'customer_email', 'room__room_number']
    readonly_fields = ['created_at', 'updated_at']

@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'created_at', 'is_read']
    list_filter = ['is_read', 'created_at']
    search_fields = ['name', 'email', 'subject']

@admin.register(Login)
class LoginAdmin(admin.ModelAdmin):
    list_display = ('email', 'role', 'is_active', 'created_at')
    search_fields = ('email', 'role')
    

@admin.register(DailyEvent)
class DailyEventAdmin(admin.ModelAdmin):
    list_display = ('name', 'event_type', 'event_date', 'show_on_home', 'is_active')
    list_filter = ('event_type', 'show_on_home', 'is_active')
    search_fields = ('name', 'description')
    ordering = ('-event_date',)