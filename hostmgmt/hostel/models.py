from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

GENDER_CHOICES = [('M', 'Male'), ('F', 'Female'), ('O', 'Other')]
BATCH_CHOICES  = [('FSWD', 'FSWD'), ('AIML', 'AIML'), ('DEVOPS', 'DevOps')]
ROOM_TYPE_CHOICES = [
    ('TRAINER', 'Trainer Room'),
    ('GIRLS',   'Girls Hostel'),
    ('BOYS',    'Boys Hostel'),
]
ALLOC_TYPE_CHOICES   = [('AUTO', 'Auto'), ('MANUAL', 'Manual')]
ALLOC_STATUS_CHOICES = [
    ('PENDING',   'Pending'),
    ('ALLOCATED', 'Allocated'),
    ('VACATED',   'Vacated'),
]


class Room(models.Model):
    room_number       = models.IntegerField(unique=True)
    room_type         = models.CharField(max_length=10, choices=ROOM_TYPE_CHOICES)
    capacity          = models.IntegerField(default=2)
    is_under_repair   = models.BooleanField(default=False)
    gender_category   = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    current_occupancy = models.IntegerField(default=0)

    class Meta:
        # ordering = ['room_number']
       
        managed = False
        db_table = 'rooms'
         # Room data is pre-populated and not managed by Django migrations

    def __str__(self):
        return f"Room {self.room_number}"

    @property
    def is_full(self):
        return self.current_occupancy >= self.capacity

    @property
    def is_available(self):
        return not self.is_under_repair and not self.is_full

    @property
    def status_label(self):
        if self.is_under_repair:
            return 'REPAIR'
        if self.current_occupancy == 0:
            return 'EMPTY'
        if self.current_occupancy >= self.capacity:
            return 'FULL'
        return 'PARTIAL'

    @property
    def status_color(self):
        mapping = {
            'EMPTY':   'green',
            'PARTIAL': 'navy',
            'FULL':    'red',
            'REPAIR':  'black',
        }
        return mapping.get(self.status_label, 'black')

    @property
    def status_css(self):
        """Returns CSS class suffix for room card border."""
        mapping = {
            'EMPTY':   'empty',
            'PARTIAL': 'partial',
            'FULL':    'full',
            'REPAIR':  'repair',
        }
        return mapping.get(self.status_label, 'repair')


class Student(models.Model):
    registration_id   = models.CharField(max_length=30, unique=True)
    full_name         = models.CharField(max_length=200)
    gender            = models.CharField(max_length=1, choices=GENDER_CHOICES)
    batch             = models.CharField(max_length=10, choices=BATCH_CHOICES)
    email             = models.EmailField(blank=True, null=True)
    phone             = models.CharField(max_length=15, blank=True, null=True)
    allocation_status = models.CharField(
        max_length=15, choices=ALLOC_STATUS_CHOICES, default='PENDING'
    )

    class Meta:
        # ordering = ['full_name']
          managed = False
           

    def __str__(self):
        return f"{self.full_name} ({self.registration_id})"


class Allocation(models.Model):
    student         = models.OneToOneField(
        Student, on_delete=models.CASCADE, related_name='allocation'
    )
    room            = models.ForeignKey(
        Room, on_delete=models.PROTECT, related_name='allocations'
    )
    allocated_at    = models.DateTimeField(auto_now_add=True)
    allocated_by    = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True
    )
    allocation_type = models.CharField(
        max_length=6, choices=ALLOC_TYPE_CHOICES, default='AUTO'
    )
    is_active       = models.BooleanField(default=True)

    class Meta:
        # ordering = ['-allocated_at']
          managed = False
          db_table = 'room_allocations'


    def __str__(self):
        return f"{self.student} → Room {self.room.room_number}"


# ── NEW MODELS (managed=False — tables already exist in MySQL) ─────────────────

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

    complaint_id    = models.AutoField(primary_key=True)
    student         = models.ForeignKey(
        Student, on_delete=models.CASCADE, db_column='student_id', null=True, blank=True
    )
    room            = models.ForeignKey(
        'Room', on_delete=models.SET_NULL, db_column='room_id', null=True, blank=True
    )
    complaint_type  = models.CharField(max_length=50, choices=COMPLAINT_TYPE_CHOICES)
    description     = models.TextField()
    complaint_date  = models.DateTimeField(auto_now_add=True)
    status          = models.CharField(max_length=20, choices=COMPLAINT_STATUS_CHOICES, default='Pending')

    class Meta:
        managed  = False
        db_table = 'complaints'

    def __str__(self):
        return f"{self.complaint_type} – {self.status}"


class MaintenanceRequest(models.Model):
    STATUS_CHOICES = [
        ('Pending',   'Pending'),
        ('In Progress','In Progress'),
        ('Resolved',  'Resolved'),
    ]

    request_id   = models.AutoField(primary_key=True)
    room         = models.ForeignKey(
        'Room', on_delete=models.SET_NULL, db_column='room_id', null=True, blank=True
    )
    requested_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, db_column='requested_by', null=True, blank=True
    )
    request_date = models.DateTimeField(auto_now_add=True)
    description  = models.TextField()
    status       = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
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
    emergency_contact = models.CharField(max_length=20, blank=True, null=True)
    status            = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    approved_by       = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        db_column='approved_by', related_name='approved_passes'
    )
    approved_at       = models.DateTimeField(null=True, blank=True)
    pdf_path          = models.CharField(max_length=500, blank=True, null=True)
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

    visitor_id    = models.AutoField(primary_key=True)
    student       = models.ForeignKey(
        Student, on_delete=models.CASCADE, db_column='student_id', null=True, blank=True
    )
    visitor_name  = models.CharField(max_length=200)
    relationship  = models.CharField(max_length=100, blank=True, null=True)
    mobile        = models.CharField(max_length=20, blank=True, null=True)
    checkin       = models.DateTimeField(null=True, blank=True)
    checkout      = models.DateTimeField(null=True, blank=True)
    purpose       = models.TextField(blank=True, null=True)
    status        = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    approved_by   = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True,
        db_column='approved_by', related_name='approved_visitors'
    )
    approved_at   = models.DateTimeField(null=True, blank=True)
    pdf_path      = models.CharField(max_length=500, blank=True, null=True)

    class Meta:
        managed  = False
        db_table = 'visitors'

    def __str__(self):
        return f"{self.visitor_name} → {self.student}"
