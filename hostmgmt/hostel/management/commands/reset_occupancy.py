from django.core.management.base import BaseCommand
from django.db import transaction
from hostel.models import Room, Student, Allocation


class Command(BaseCommand):
    """
    Recalculates current_occupancy for all rooms and allocation_status
    for all students based on active Allocation records.

    Run this if the database gets out of sync (e.g. after manual admin edits).

    Usage:
        python manage.py reset_occupancy
    """
    help = 'Recalculate room occupancy and student allocation_status from active allocations'

    @transaction.atomic
    def handle(self, *args, **kwargs):
        self.stdout.write('Resetting occupancy and student statuses...')

        # Step 1: Reset all rooms to 0
        Room.objects.all().update(current_occupancy=0)

        # Step 2: Reset all students to PENDING
        Student.objects.all().update(allocation_status='PENDING')

        # Step 3: Recalculate from active allocations
        active_allocs = Allocation.objects.filter(is_active=True).select_related('room', 'student')

        room_counts  = {}
        student_ids  = []

        for alloc in active_allocs:
            rid = alloc.room.id
            room_counts[rid] = room_counts.get(rid, 0) + 1
            student_ids.append(alloc.student.id)

        # Step 4: Apply counts
        for room_id, count in room_counts.items():
            Room.objects.filter(id=room_id).update(current_occupancy=count)

        # Step 5: Mark allocated students
        if student_ids:
            Student.objects.filter(id__in=student_ids).update(allocation_status='ALLOCATED')

        # Step 6: Mark vacated students (inactive allocations, no active alloc)
        vacated_student_ids = Allocation.objects.filter(
            is_active=False
        ).exclude(
            student__id__in=student_ids
        ).values_list('student__id', flat=True).distinct()

        if vacated_student_ids:
            Student.objects.filter(id__in=vacated_student_ids).update(allocation_status='VACATED')

        active_count  = len(student_ids)
        room_count    = len(room_counts)

        self.stdout.write(self.style.SUCCESS(
            f'Done.\n'
            f'  {active_count} students marked ALLOCATED\n'
            f'  {room_count} rooms updated with live occupancy\n'
            f'  Remaining students set to PENDING or VACATED'
        ))
