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
        ordering = ['room_number']

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
        ordering = ['full_name']

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
        ordering = ['-allocated_at']

    def __str__(self):
        return f"{self.student} → Room {self.room.room_number}"
