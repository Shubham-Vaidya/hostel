from django.contrib import admin
from .models import Room, Student, Allocation, Complaint, MaintenanceRequest, GatePass, Visitor


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


@admin.register(Complaint)
class ComplaintAdmin(admin.ModelAdmin):
    list_display  = ['complaint_id', 'student', 'complaint_type', 'complaint_date', 'status']
    list_filter   = ['complaint_type', 'status']
    search_fields = ['description']
    ordering      = ['-complaint_date']


@admin.register(MaintenanceRequest)
class MaintenanceRequestAdmin(admin.ModelAdmin):
    list_display  = ['request_id', 'room', 'requested_by', 'request_date', 'status', 'resolved_on']
    list_filter   = ['status']
    ordering      = ['-request_date']


@admin.register(GatePass)
class GatePassAdmin(admin.ModelAdmin):
    list_display  = ['pass_id', 'student', 'destination', 'out_date', 'return_date', 'status', 'approved_by']
    list_filter   = ['status']
    search_fields = ['destination', 'purpose']
    ordering      = ['-created_at']


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display  = ['visitor_id', 'visitor_name', 'student', 'relationship', 'mobile', 'checkin', 'checkout', 'status']
    list_filter   = ['status', 'relationship']
    search_fields = ['visitor_name', 'mobile']
    ordering      = ['-visitor_id']
