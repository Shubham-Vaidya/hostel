from django.contrib import admin
from .models import Room, Student, RoomAllocation, Complaint, MaintenanceRequest, GatePass, Visitor


@admin.register(Room)
class RoomAdmin(admin.ModelAdmin):
    list_display  = ['room_id', 'room_no', 'room_type', 'capacity', 'status']
    list_filter   = ['room_type', 'status']
    search_fields = ['room_no']
    ordering      = ['room_no']


@admin.register(Student)
class StudentAdmin(admin.ModelAdmin):
    list_display  = ['student_id', 'admission_no', 'first_name', 'last_name', 'gender', 'email', 'status']
    list_filter   = ['gender', 'status']
    search_fields = ['first_name', 'last_name', 'admission_no', 'email']
    ordering      = ['first_name']


@admin.register(RoomAllocation)
class RoomAllocationAdmin(admin.ModelAdmin):
    list_display  = ['allocation_id', 'student', 'room', 'bed_number', 'allocation_date', 'checkout_date', 'status']
    list_filter   = ['status']
    raw_id_fields = ['student', 'room']
    ordering      = ['-allocation_id']


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
    list_display  = ['pass_id', 'student', 'destination', 'out_date', 'return_date', 'status']
    list_filter   = ['status']
    search_fields = ['destination', 'purpose']
    ordering      = ['-created_at']


@admin.register(Visitor)
class VisitorAdmin(admin.ModelAdmin):
    list_display  = ['visitor_id', 'visitor_name', 'student', 'relationship', 'mobile', 'checkin', 'status']
    list_filter   = ['status']
    search_fields = ['visitor_name', 'mobile']
    ordering      = ['-visitor_id']
