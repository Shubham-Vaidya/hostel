from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

# ─────────────────────────────────────────────────────────────────────────────
# CORE HOSTEL MODELS — all managed=False, matching the actual MySQL schema
# ─────────────────────────────────────────────────────────────────────────────

class Room(models.Model):
    """Maps to: rooms(room_id, floor_id, room_no, room_type, capacity, status)"""
    ROOM_TYPE_CHOICES = [
        ('Single', 'Single'),
        ('Double', 'Double'),
        ('Triple', 'Triple'),
    ]
    STATUS_CHOICES = [
        ('Available',   'Available'),
        ('Occupied',    'Occupied'),
        ('Maintenance', 'Maintenance'),
    ]

    room_id   = models.AutoField(primary_key=True)
    floor_id  = models.IntegerField(default=1)
    room_no   = models.CharField(max_length=20)
    room_type = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES, default='Double')
    capacity  = models.IntegerField(default=2)
    status    = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Available')

    class Meta:
        managed  = False
        db_table = 'rooms'
        ordering = ['room_no']

    def __str__(self):
        return f"Room {self.room_no}"

    # ── Compatibility properties so existing templates keep working ──────────
    @property
    def room_number(self):
        return self.room_no

    @property
    def is_under_repair(self):
        return self.status == 'Maintenance'

    @property
    def current_occupancy(self):
        return self.allocations.filter(status='Active').count()

    @property
    def is_full(self):
        return self.status == 'Occupied' or self.current_occupancy >= self.capacity

    @property
    def is_available(self):
        return self.status == 'Available'

    @property
    def status_label(self):
        if self.status == 'Maintenance':
            return 'REPAIR'
        if self.status == 'Available':
            return 'EMPTY'
        return 'FULL'

    @property
    def status_color(self):
        mapping = {
            'Available':   'green',
            'Occupied':    'red',
            'Maintenance': 'black',
        }
        return mapping.get(self.status, 'black')

    @property
    def status_css(self):
        mapping = {
            'Available':   'empty',
            'Occupied':    'full',
            'Maintenance': 'repair',
        }
        return mapping.get(self.status, 'repair')


class Student(models.Model):
    """Maps to: students(student_id, admission_no, first_name, last_name,
                         gender, dob, mobile, email, academic_year, status, created_at)"""
    GENDER_CHOICES = [
        ('Male',   'Male'),
        ('Female', 'Female'),
        ('Other',  'Other'),
    ]
    STATUS_CHOICES = [
        ('Active',   'Active'),
        ('Inactive', 'Inactive'),
    ]

    student_id    = models.AutoField(primary_key=True)
    admission_no  = models.CharField(max_length=30, unique=True, blank=True, null=True)
    first_name    = models.CharField(max_length=100)
    last_name     = models.CharField(max_length=100, blank=True, null=True)
    gender        = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    dob           = models.DateField(blank=True, null=True)
    mobile        = models.CharField(max_length=15, blank=True, null=True)
    email         = models.EmailField(max_length=150, blank=True, null=True)
    academic_year = models.CharField(max_length=20, blank=True, null=True)
    status        = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Active')
    created_at    = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed  = False
        db_table = 'students'
        ordering = ['first_name', 'last_name']

    def __str__(self):
        return f"{self.first_name} {self.last_name or ''}".strip()

    # ── Compatibility properties so existing templates keep working ──────────
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name or ''}".strip()

    @property
    def registration_id(self):
        return self.admission_no or str(self.student_id)

    @property
    def allocation_status(self):
        """Derived from room_allocations — 'ALLOCATED' if active allocation exists."""
        if self.roomallocation_set.filter(status='Active').exists():
            return 'ALLOCATED'
        return 'PENDING'

    @property
    def allocation(self):
        """Return the active RoomAllocation for this student (or None)."""
        return self.roomallocation_set.filter(status='Active').first()

    # batch property for legacy templates
    @property
    def batch(self):
        return self.academic_year or '—'

    # phone property for legacy templates
    @property
    def phone(self):
        return self.mobile

    def get_gender_display(self):
        return self.gender or '—'


class RoomAllocation(models.Model):
    """Maps to: room_allocations(allocation_id, room_id, student_id,
                                  bed_number, allocation_date, checkout_date, status)"""
    STATUS_CHOICES = [
        ('Active',      'Active'),
        ('Vacated',     'Vacated'),
        ('Transferred', 'Transferred'),
    ]

    allocation_id   = models.AutoField(primary_key=True)
    room            = models.ForeignKey(
        Room, on_delete=models.PROTECT, db_column='room_id', related_name='allocations'
    )
    student         = models.ForeignKey(
        Student, on_delete=models.CASCADE, db_column='student_id', related_name='roomallocation_set'
    )
    bed_number      = models.CharField(max_length=10, blank=True, null=True)
    allocation_date = models.DateField(auto_now_add=True)
    checkout_date   = models.DateField(blank=True, null=True)
    status          = models.CharField(max_length=15, choices=STATUS_CHOICES, default='Active')

    class Meta:
        managed  = False
        db_table = 'room_allocations'

    def __str__(self):
        return f"{self.student} → Room {self.room.room_no}"

    # Compatibility alias so old views using alloc.is_active still work
    @property
    def is_active(self):
        return self.status == 'Active'

    # Compatibility: allocated_at for old templates
    @property
    def allocated_at(self):
        return self.allocation_date

    # Compatibility: allocated_by – not in schema, return None
    @property
    def allocated_by(self):
        return None

    # Compatibility: allocation_type
    @property
    def allocation_type(self):
        return 'MANUAL'


# Keep Allocation as an alias so any remaining old imports don't break
Allocation = RoomAllocation


# ─────────────────────────────────────────────────────────────────────────────
# NEW MODULE MODELS — managed=False, tables already exist in MySQL
# ─────────────────────────────────────────────────────────────────────────────

class Complaint(models.Model):
    COMPLAINT_TYPE_CHOICES = [
        ('Bathroom',    'Bathroom'),
        ('Electrical',  'Electrical'),
        ('Cleaning',    'Cleaning'),
        ('Pest Control','Pest Control'),
        ('Furniture',   'Furniture'),
        ('Other',       'Other'),
    ]
    COMPLAINT_STATUS_CHOICES = [
        ('Pending',     'Pending'),
        ('In Progress', 'In Progress'),
        ('Resolved',    'Resolved'),
    ]

    complaint_id   = models.AutoField(primary_key=True)
    student        = models.ForeignKey(
        Student, on_delete=models.CASCADE, db_column='student_id', null=True, blank=True
    )
    room           = models.ForeignKey(
        Room, on_delete=models.SET_NULL, db_column='room_id', null=True, blank=True
    )
    complaint_type = models.CharField(max_length=50, choices=COMPLAINT_TYPE_CHOICES)
    description    = models.TextField()
    complaint_date = models.DateTimeField(auto_now_add=True)
    status         = models.CharField(max_length=20, choices=COMPLAINT_STATUS_CHOICES, default='Pending')

    class Meta:
        managed  = False
        db_table = 'complaints'

    def __str__(self):
        return f"{self.complaint_type} – {self.status}"


class MaintenanceRequest(models.Model):
    STATUS_CHOICES = [
        ('Open',        'Open'),
        ('Assigned',    'Assigned'),
        ('In Progress', 'In Progress'),
        ('Completed',   'Completed'),
    ]

    request_id   = models.AutoField(primary_key=True)
    room         = models.ForeignKey(
        Room, on_delete=models.SET_NULL, db_column='room_id', null=True, blank=True
    )
    requested_by = models.IntegerField(null=True, blank=True)
    request_date = models.DateTimeField(auto_now_add=True)
    description  = models.TextField()
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Open')
    resolved_on  = models.DateTimeField(null=True, blank=True)

    class Meta:
        managed  = False
        db_table = 'maintenance_requests'

    def __str__(self):
        return f"Maintenance #{self.request_id} – {self.status}"


class GatePass(models.Model):
    STATUS_CHOICES = [
        ('Pending',  'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
        ('Returned', 'Returned'),
    ]

    pass_id           = models.AutoField(primary_key=True)
    student           = models.ForeignKey(
        Student, on_delete=models.CASCADE, db_column='student_id', null=True, blank=True
    )
    room_no           = models.CharField(max_length=20, blank=True, null=True)
    destination       = models.CharField(max_length=200)
    purpose           = models.TextField(blank=True, null=True)
    out_date          = models.DateField()
    out_time          = models.TimeField()
    return_date       = models.DateField()
    return_time       = models.TimeField()
    emergency_contact = models.CharField(max_length=15, blank=True, null=True)
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    approved_by       = models.IntegerField(null=True, blank=True)
    approved_at       = models.DateTimeField(null=True, blank=True)
    pdf_path          = models.CharField(max_length=255, blank=True, null=True)
    created_at        = models.DateTimeField(auto_now_add=True)

    class Meta:
        managed  = False
        db_table = 'gate_passes'

    def __str__(self):
        return f"GatePass #{self.pass_id} – {self.status}"


class Visitor(models.Model):
    STATUS_CHOICES = [
        ('Pending',  'Pending'),
        ('Approved', 'Approved'),
        ('Rejected', 'Rejected'),
    ]

    visitor_id   = models.AutoField(primary_key=True)
    student      = models.ForeignKey(
        Student, on_delete=models.CASCADE, db_column='student_id', null=True, blank=True
    )
    visitor_name = models.CharField(max_length=100)
    relationship = models.CharField(max_length=50, blank=True, null=True)
    mobile       = models.CharField(max_length=15, blank=True, null=True)
    checkin      = models.DateTimeField(null=True, blank=True)
    checkout     = models.DateTimeField(null=True, blank=True)
    purpose      = models.CharField(max_length=200, blank=True, null=True)
    status       = models.CharField(max_length=10, choices=STATUS_CHOICES, default='Pending')
    approved_by  = models.IntegerField(null=True, blank=True)
    approved_at  = models.DateTimeField(null=True, blank=True)
    pdf_path     = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed  = False
        db_table = 'visitors'

    def __str__(self):
        return f"{self.visitor_name} → {self.student}"
