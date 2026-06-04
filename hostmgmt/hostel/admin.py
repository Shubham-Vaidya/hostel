from django.contrib import admin
from .models import Room, Student, Allocation


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display  = ['room_number', 'room_type', 'capacity', 'current_occupancy', 'is_under_repair', 'status_label']
    list_filter   = ['room_type', 'is_under_repair']
    ordering      = ['room_number']
    search_fields = ['room_number']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display  = ['registration_id', 'full_name', 'gender', 'batch', 'allocation_status']
    list_filter   = ['batch', 'gender', 'allocation_status']
    search_fields = ['full_name', 'registration_id']
    ordering      = ['full_name']


@admin.register(Allocation)
class AllocationAdmin(admin.ModelAdmin):
    list_display  = ['student', 'room', 'allocation_type', 'allocated_at', 'is_active']
    list_filter   = ['allocation_type', 'is_active', 'room__room_type']
    raw_id_fields = ['student', 'room']
    ordering      = ['-allocated_at']
