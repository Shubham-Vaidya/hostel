from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction
from django.utils import timezone
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from .models import (
    Hostel, Block, Floor,
    Room, Student, RoomAllocation,
    Complaint, MaintenanceRequest, GatePass, Visitor,
)


# ─────────────────────────────────────────────────────────────────────────────
# HELPERS (Auth removed)
# ─────────────────────────────────────────────────────────────────────────────

def is_admin(user):
    return True  # Always treat as admin since login is removed


def admin_required(view_fn):
    """Pass-through: no auth required."""
    def wrapper(request, *args, **kwargs):
        return view_fn(request, *args, **kwargs)
    wrapper.__name__ = view_fn.__name__
    return wrapper


def student_required(view_fn):
    """Pass-through: no auth required."""
    def wrapper(request, *args, **kwargs):
        return view_fn(request, *args, **kwargs)
    wrapper.__name__ = view_fn.__name__
    return wrapper


# ─────────────────────────────────────────────────────────────────────────────
# DASHBOARD
# ─────────────────────────────────────────────────────────────────────────────

def dashboard(request):
    total_rooms     = Room.objects.count()
    available_rooms = Room.objects.filter(status='Available').count()
    occupied_rooms  = Room.objects.filter(status='Occupied').count()
    partial_rooms   = Room.objects.filter(status='Partially Occupied').count()
    repair_rooms    = Room.objects.filter(status='Maintenance').count()
    total_students  = Student.objects.count()
    allocated       = RoomAllocation.objects.filter(status='Active').count()
    pending         = max(0, total_students - allocated)

    # Infrastructure stats from real DB
    total_hostels = Hostel.objects.count()
    total_blocks  = Block.objects.count()
    total_floors  = Floor.objects.count()

    return render(request, 'hostel/dashboard.html', {
        'total_rooms':     total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms':  occupied_rooms + partial_rooms,
        'total_students':  total_students,
        'allocated':       allocated,
        'pending':         pending,
        'trainers_alloc':  0,
        'repair_rooms':    repair_rooms,
        'batch_stats':     [],
        'total_hostels':   total_hostels,
        'total_blocks':    total_blocks,
        'total_floors':    total_floors,
    })


# ─────────────────────────────────────────────────────────────────────────────
# MY ROOM  (student view)
# ─────────────────────────────────────────────────────────────────────────────

@student_required
def my_room(request):
    # Without login, just show the first active allocation as a demo, or empty if none
    allocation = RoomAllocation.objects.filter(status='Active').select_related('room', 'student').first()

    roommates = []
    if allocation:
        roommates = RoomAllocation.objects.filter(
            room=allocation.room,
            status='Active'
        ).exclude(student=allocation.student).select_related('student')

    return render(request, 'hostel/my_room.html', {
        'allocation': allocation,
        'roommates':  roommates,
    })


# ─────────────────────────────────────────────────────────────────────────────
# ROOMS  (admin view — full CRUD)
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def rooms_view(request):
    """Admin rooms management with stat cards, filters, and table."""
    # ── stats ──
    total_rooms = Room.objects.count()
    available   = Room.objects.filter(status='Available').count()
    occupied    = Room.objects.filter(status='Occupied').count()
    maintenance = Room.objects.filter(status='Maintenance').count()

    # ── filters from GET ──
    filter_status    = request.GET.get('status', '')
    filter_room_type = request.GET.get('room_type', '')

    qs = Room.objects.all().order_by('room_no')
    if filter_status:
        qs = qs.filter(status=filter_status)
    if filter_room_type:
        qs = qs.filter(room_type=filter_room_type)

    # ── annotate occupied beds per room ──
    from django.db.models import Count, Q
    qs = qs.annotate(
        occupied_beds=Count(
            'allocations',
            filter=Q(allocations__status='Active')
        )
    )

    # ── handle Add Room POST (modal form) ──
    if request.method == 'POST' and request.POST.get('action') == 'add_room':
        try:
            room_no   = request.POST.get('room_no', '').strip()
            room_type = request.POST.get('room_type', 'Double')
            capacity  = int(request.POST.get('capacity', 2))
            if not room_no:
                messages.error(request, 'Room number is required.')
            elif Room.objects.filter(room_no=room_no).exists():
                messages.error(request, f'Room {room_no} already exists.')
            else:
                Room.objects.create(
                    room_no=room_no,
                    room_type=room_type,
                    capacity=capacity,
                    status='Available',
                )
                messages.success(request, f'Room {room_no} added successfully.')
        except Exception as e:
            messages.error(request, f'Error adding room: {e}')
        return redirect('hostel:rooms')

    return render(request, 'hostel/rooms_list.html', {
        'rooms':            qs,
        'total_rooms':      total_rooms,
        'available':        available,
        'occupied':         occupied,
        'maintenance':      maintenance,
        'filter_status':    filter_status,
        'filter_room_type': filter_room_type,
        'room_types':       ['Single', 'Double', 'Triple'],
        'statuses':         ['Available', 'Partially Occupied', 'Occupied', 'Maintenance'],
    })


@admin_required
def room_detail_ajax(request, room_id):
    """Returns room detail + active allocations as JSON for the modal."""
    import json
    room = get_object_or_404(Room, room_id=room_id)
    allocs = RoomAllocation.objects.filter(
        room=room, status='Active'
    ).select_related('student')

    occupants = []
    for a in allocs:
        occupants.append({
            'name':       a.student.full_name,
            'admission':  a.student.registration_id,
            'bed':        a.bed_number or '—',
            'gender':     a.student.gender or '—',
        })

    data = {
        'room_no':       room.room_no,
        'room_type':     room.room_type,
        'capacity':      room.capacity,
        'status':        room.status,
        'occupied_beds': len(occupants),
        'occupants':     occupants,
    }
    from django.http import JsonResponse
    return JsonResponse(data)


def room_detail(request, room_number):
    room = get_object_or_404(Room, room_no=room_number)
    allocations = RoomAllocation.objects.filter(
        room=room, status='Active'
    ).select_related('student')
    history = RoomAllocation.objects.filter(
        room=room
    ).select_related('student').order_by('-allocation_id')
    available_rooms = Room.objects.filter(
        status='Available'
    ).exclude(room_id=room.room_id)
    return render(request, 'hostel/room_detail.html', {
        'room':            room,
        'allocations':     allocations,
        'history':         history,
        'available_rooms': available_rooms,
    })


@admin_required
def add_room(request):
    if request.method == 'POST':
        try:
            room_no   = request.POST.get('room_number', '').strip()
            room_type = request.POST.get('room_type', 'Double')
            capacity  = int(request.POST.get('capacity', 2))
            Room.objects.create(
                room_no=room_no,
                room_type=room_type,
                capacity=capacity,
                status='Available',
            )
            messages.success(request, f'Room {room_no} added successfully.')
            return redirect('hostel:rooms')
        except Exception as e:
            messages.error(request, f'Error adding room: {e}')
    return render(request, 'hostel/add_room.html')


@admin_required
def edit_room(request, room_number):
    room = get_object_or_404(Room, room_no=room_number)
    if request.method == 'POST':
        try:
            room.capacity  = int(request.POST.get('capacity', room.capacity))
            new_status     = request.POST.get('status', room.status)
            if new_status in ['Available', 'Occupied', 'Maintenance']:
                room.status = new_status
            room.save()
            messages.success(request, f'Room {room_number} updated.')
            return redirect('hostel:room_detail', room_number=room_number)
        except Exception as e:
            messages.error(request, f'Error updating room: {e}')
    return render(request, 'hostel/edit_room.html', {'room': room})


@admin_required
def toggle_repair(request, room_number):
    room = get_object_or_404(Room, room_no=room_number)
    if request.method == 'POST':
        room.status = 'Maintenance' if room.status != 'Maintenance' else 'Available'
        room.save()
        messages.success(request, f'Room {room_number} status updated to {room.status}.')
    return redirect('hostel:room_detail', room_number=room_number)


# ─────────────────────────────────────────────────────────────────────────────
# STUDENTS
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def students_list(request):
    gender_filter = request.GET.get('gender', '')
    status_filter = request.GET.get('status', '')

    qs = Student.objects.all()
    if gender_filter:
        qs = qs.filter(gender=gender_filter)
    if status_filter == 'Active':
        qs = qs.filter(status='Active')
    elif status_filter == 'Inactive':
        qs = qs.filter(status='Inactive')

    return render(request, 'hostel/students_list.html', {
        'students':      qs,
        'batch_filter':  '',
        'gender_filter': gender_filter,
        'status_filter': status_filter,
    })


@admin_required
def add_student(request):
    if request.method == 'POST':
        try:
            Student.objects.create(
                admission_no=request.POST.get('registration_id', '').strip() or None,
                first_name=request.POST.get('full_name', '').strip(),
                last_name='',
                gender=request.POST.get('gender', '').strip() or None,
                email=request.POST.get('email', '').strip() or None,
                mobile=request.POST.get('phone', '').strip() or None,
                status='Active',
            )
            messages.success(request, 'Student added successfully.')
            return redirect('hostel:students')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'hostel/add_student.html')


@admin_required
def import_students(request):
    """Import students from a CSV file."""
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            messages.error(request, 'Please select a CSV file to upload.')
            return redirect('hostel:import_students')
        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Only .csv files are supported.')
            return redirect('hostel:import_students')
        try:
            import csv, io
            decoded = csv_file.read().decode('utf-8-sig')
            reader  = csv.DictReader(io.StringIO(decoded))
            reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]
            created, skipped, errors = 0, 0, []
            for row_num, row in enumerate(reader, start=2):
                try:
                    admission_no = row.get('registration_id', row.get('admission_no', '')).strip()
                    first_name   = row.get('full_name', row.get('first_name', '')).strip()
                    last_name    = row.get('last_name', '').strip()
                    email        = row.get('email', '').strip()
                    mobile       = row.get('phone', row.get('mobile', '')).strip()
                    gender       = row.get('gender', '').strip()
                    if not first_name:
                        errors.append(f'Row {row_num}: Missing name')
                        continue
                    obj, was_created = Student.objects.get_or_create(
                        admission_no=admission_no or None,
                        defaults={
                            'first_name': first_name,
                            'last_name':  last_name,
                            'gender':     gender or None,
                            'email':      email or None,
                            'mobile':     mobile or None,
                            'status':     'Active',
                        }
                    )
                    if was_created:
                        created += 1
                    else:
                        skipped += 1
                except Exception as e:
                    errors.append(f'Row {row_num}: {e}')
            if created:
                messages.success(request, f'Import complete: {created} added, {skipped} skipped.')
            else:
                messages.warning(request, f'Import finished: {created} added, {skipped} skipped.')
            for err in errors[:5]:
                messages.error(request, err)
            if len(errors) > 5:
                messages.error(request, f'...and {len(errors)-5} more errors.')
            return redirect('hostel:students')
        except Exception as e:
            messages.error(request, f'Failed to process CSV: {e}')
            return redirect('hostel:import_students')
    return render(request, 'hostel/import_students.html')


# ─────────────────────────────────────────────────────────────────────────────
# AUTO ALLOCATION
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
@transaction.atomic
def auto_allocate(request, batch=None):
    if request.method != 'POST':
        unallocated_ids = RoomAllocation.objects.filter(
            status='Active'
        ).values_list('student_id', flat=True)
        pending_count = Student.objects.exclude(student_id__in=unallocated_ids).count()
        batches = [
            {'code': 'ALL', 'label': 'All Students', 'pending': pending_count},
        ]
        return render(request, 'hostel/auto_allocate.html', {
            'batches':      batches,
            'filter_batch': batch,
        })

    allocated_ids    = RoomAllocation.objects.filter(status='Active').values_list('student_id', flat=True)
    pending_students = list(Student.objects.exclude(student_id__in=allocated_ids))
    available_rooms  = list(Room.objects.filter(status='Available').order_by('room_no'))
    allocated_records, skipped = [], []

    room_idx = 0
    for student in pending_students:
        placed = False
        while room_idx < len(available_rooms):
            room    = available_rooms[room_idx]
            current = RoomAllocation.objects.filter(room=room, status='Active').count()
            if current < room.capacity:
                RoomAllocation.objects.create(student=student, room=room, status='Active')
                allocated_records.append(student)
                placed = True
                if current + 1 >= room.capacity:
                    room.status = 'Occupied'
                    room.save()
                    room_idx += 1
                break
            else:
                room.status = 'Occupied'
                room.save()
                room_idx += 1
        if not placed:
            skipped.append(student)

    request.session['alloc_summary'] = {
        'allocated_count': len(allocated_records),
        'skipped_count':   len(skipped),
        'batch':           'ALL',
    }
    if skipped:
        messages.warning(request, f'{len(skipped)} student(s) could not be allocated — no rooms available.')
    messages.success(request, f'Auto allocation complete. {len(allocated_records)} student(s) allocated.')
    return redirect('hostel:allocation_results')


# ─────────────────────────────────────────────────────────────────────────────
# MANUAL ALLOCATION
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def manual_allocate(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        room_id    = request.POST.get('room_id')
        if not student_id or not room_id:
            messages.error(request, 'Please select both a student and a room.')
            return redirect('hostel:manual_allocate')
        student = get_object_or_404(Student, student_id=student_id)
        room    = get_object_or_404(Room, room_id=room_id)
        if RoomAllocation.objects.filter(student=student, status='Active').exists():
            messages.error(request, f'{student.full_name} is already allocated to a room.')
            return redirect('hostel:manual_allocate')
        if room.status == 'Maintenance':
            messages.error(request, f'Room {room.room_no} is under maintenance.')
            return redirect('hostel:manual_allocate')
        if room.status == 'Occupied':
            if RoomAllocation.objects.filter(room=room, status='Active').count() >= room.capacity:
                messages.error(request, f'Room {room.room_no} is full.')
                return redirect('hostel:manual_allocate')
        with transaction.atomic():
            RoomAllocation.objects.create(student=student, room=room, status='Active')
            if RoomAllocation.objects.filter(room=room, status='Active').count() >= room.capacity:
                room.status = 'Occupied'
                room.save()
        messages.success(request, f'{student.full_name} allocated to Room {room.room_no}.')
        return redirect('hostel:manual_allocate')

    allocated_ids   = RoomAllocation.objects.filter(status='Active').values_list('student_id', flat=True)
    unallocated     = Student.objects.exclude(student_id__in=allocated_ids)
    available_rooms = Room.objects.filter(status='Available')
    return render(request, 'hostel/manual_allocate.html', {
        'unallocated':     unallocated,
        'available_rooms': available_rooms,
    })


# ─────────────────────────────────────────────────────────────────────────────
# ALLOCATION RESULTS & LIST
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def allocation_results(request):
    allocations = RoomAllocation.objects.filter(
        status='Active'
    ).select_related('student', 'room').order_by('room__room_no')
    rooms_data = {}
    for alloc in allocations:
        rn = alloc.room.room_no
        if rn not in rooms_data:
            rooms_data[rn] = {'room': alloc.room, 'occupants': []}
        rooms_data[rn]['occupants'].append(alloc.student)
    total     = Student.objects.count()
    allocated = RoomAllocation.objects.filter(status='Active').count()
    summary   = request.session.pop('alloc_summary', {})
    return render(request, 'hostel/allocation_results.html', {
        'rooms_data':         rooms_data.values(),
        'rooms_used':         len(rooms_data),
        'total_students':     total,
        'allocated_students': allocated,
        'remaining_capacity': 0,
        'summary':            summary,
    })


@admin_required
def allocation_list(request):
    gender_filter = request.GET.get('gender', '')
    type_filter   = request.GET.get('room_type', '')
    qs = RoomAllocation.objects.filter(
        status='Active'
    ).select_related('student', 'room').order_by('room__room_no')
    if gender_filter:
        qs = qs.filter(student__gender=gender_filter)
    if type_filter:
        qs = qs.filter(room__room_type=type_filter)
    return render(request, 'hostel/allocation_list.html', {
        'allocations':   qs,
        'batch_filter':  '',
        'gender_filter': gender_filter,
        'type_filter':   type_filter,
        'alloc_filter':  '',
    })


# ─────────────────────────────────────────────────────────────────────────────
# CSV EXPORT & COMMON SERVICES DISPATCH
# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def export_allocation_csv(request):
    """
    Streams a CSV file containing full allocation details for all active
    room allocations. Columns: Admission No, Name, Email, Mobile, Gender,
    Academic Year, Hostel, Block, Floor, Room No, Room Type, Capacity,
    Bed No, Allocation Date.
    """
    import csv
    from django.http import StreamingHttpResponse
    from django.db import connection

    # Fetch all active allocations with full room hierarchy via raw SQL
    # so we can join hostels/blocks/floors which don't have direct FKs in models
    sql = """
        SELECT
            s.admission_no,
            CONCAT(COALESCE(s.first_name,''), ' ', COALESCE(s.last_name,'')) AS full_name,
            s.email,
            s.mobile,
            s.gender,
            s.academic_year,
            h.hostel_name,
            b.block_name,
            f.floor_no,
            r.room_no,
            r.room_type,
            r.capacity,
            ra.bed_number,
            ra.allocation_date
        FROM room_allocations ra
        JOIN students s  ON ra.student_id = s.student_id
        JOIN rooms    r  ON ra.room_id    = r.room_id
        JOIN floors   f  ON r.floor_id    = f.floor_id
        JOIN blocks   b  ON f.block_id    = b.block_id
        JOIN hostels  h  ON b.hostel_id   = h.hostel_id
        WHERE ra.status = 'Active'
        ORDER BY h.hostel_name, b.block_name, r.room_no, s.first_name
    """

    class EchoWriter:
        """A writer that returns the value written."""
        def write(self, value):
            return value

    def generate_rows(cursor):
        writer = csv.writer(EchoWriter())
        # Header
        yield writer.writerow([
            'Admission No', 'Full Name', 'Email', 'Mobile', 'Gender',
            'Academic Year', 'Hostel', 'Block', 'Floor No',
            'Room No', 'Room Type', 'Capacity', 'Bed No', 'Allocation Date'
        ])
        cursor.execute(sql)
        for row in cursor.fetchall():
            yield writer.writerow(row)

    cursor = connection.cursor()
    response = StreamingHttpResponse(
        generate_rows(cursor),
        content_type='text/csv',
    )
    from datetime import date
    filename = f'room_allocation_{date.today().isoformat()}.csv'
    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response


@admin_required
def send_to_common_services(request):
    """
    Generates the allocation CSV in memory and POSTs it to the configured
    Common Services email endpoint (COMMON_SERVICES_EMAIL_URL in settings.py).
    Common Services is expected to read each row, generate a personalized PDF,
    and email it to the student.
    """
    if request.method != 'POST':
        return redirect('hostel:allocation_results')

    import csv, io, urllib.request, urllib.error
    from django.conf import settings
    from django.db import connection

    endpoint = getattr(settings, 'COMMON_SERVICES_EMAIL_URL', '')
    if not endpoint or 'YOUR_COMMON_SERVICES_HOST' in endpoint:
        messages.warning(
            request,
            'Common Services endpoint is not configured. '
            'Set COMMON_SERVICES_EMAIL_URL in settings.py to the real URL, then try again.'
        )
        return redirect('hostel:allocation_results')

    sql = """
        SELECT
            s.admission_no,
            CONCAT(COALESCE(s.first_name,''), ' ', COALESCE(s.last_name,'')) AS full_name,
            s.email,
            s.mobile,
            s.gender,
            s.academic_year,
            h.hostel_name,
            b.block_name,
            f.floor_no,
            r.room_no,
            r.room_type,
            r.capacity,
            ra.bed_number,
            ra.allocation_date
        FROM room_allocations ra
        JOIN students s  ON ra.student_id = s.student_id
        JOIN rooms    r  ON ra.room_id    = r.room_id
        JOIN floors   f  ON r.floor_id    = f.floor_id
        JOIN blocks   b  ON f.block_id    = b.block_id
        JOIN hostels  h  ON b.hostel_id   = h.hostel_id
        WHERE ra.status = 'Active'
        ORDER BY h.hostel_name, b.block_name, r.room_no, s.first_name
    """

    cursor = connection.cursor()
    cursor.execute(sql)
    rows = cursor.fetchall()

    if not rows:
        messages.warning(request, 'No active allocations found. Nothing was sent.')
        return redirect('hostel:allocation_results')

    # Build CSV in memory
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow([
        'Admission No', 'Full Name', 'Email', 'Mobile', 'Gender',
        'Academic Year', 'Hostel', 'Block', 'Floor No',
        'Room No', 'Room Type', 'Capacity', 'Bed No', 'Allocation Date'
    ])
    for row in rows:
        writer.writerow(row)

    csv_bytes = output.getvalue().encode('utf-8')

    # POST to Common Services
    try:
        boundary = b'----PravaahHostelCSVBoundary'
        body = (
            b'--' + boundary + b'\r\n'
            b'Content-Disposition: form-data; name="csv_file"; filename="room_allocation.csv"\r\n'
            b'Content-Type: text/csv\r\n\r\n' +
            csv_bytes + b'\r\n'
            b'--' + boundary + b'--\r\n'
        )
        req = urllib.request.Request(
            endpoint,
            data=body,
            headers={
                'Content-Type': f'multipart/form-data; boundary={boundary.decode()}',
                'X-Source': 'PRAVAAH-Hostel',
            },
            method='POST',
        )
        with urllib.request.urlopen(req, timeout=10) as resp:
            status = resp.getcode()
        messages.success(
            request,
            f'✅ Allocation data for {len(rows)} student(s) sent to Common Services '
            f'(HTTP {status}). Emails with PDF attachments will be dispatched shortly.'
        )
    except urllib.error.URLError as e:
        messages.error(
            request,
            f'❌ Could not reach Common Services at {endpoint}: {e.reason}. '
            f'CSV data is ready — use "Download CSV" to send it manually.'
        )
    except Exception as e:
        messages.error(request, f'❌ Unexpected error sending to Common Services: {e}')

    return redirect('hostel:allocation_results')


# ─────────────────────────────────────────────────────────────────────────────

@admin_required
def remove_allocation(request, allocation_id):
    alloc = get_object_or_404(RoomAllocation, allocation_id=allocation_id)
    if request.method == 'POST':
        with transaction.atomic():
            alloc.status = 'Vacated'
            alloc.save()
            if RoomAllocation.objects.filter(room=alloc.room, status='Active').count() == 0:
                alloc.room.status = 'Available'
                alloc.room.save()
        messages.success(request, f'{alloc.student.full_name} removed from Room {alloc.room.room_no}.')
    return redirect(request.META.get('HTTP_REFERER', '/hostel/allocate/list/'))


@admin_required
def transfer_student(request, allocation_id):
    alloc = get_object_or_404(RoomAllocation, allocation_id=allocation_id)
    if request.method == 'POST':
        new_room_id = request.POST.get('new_room_id')
        new_room    = get_object_or_404(Room, room_id=new_room_id)
        if new_room.status == 'Maintenance':
            messages.error(request, f'Room {new_room.room_no} is under maintenance.')
            return redirect('hostel:transfer_student', allocation_id=allocation_id)
        if RoomAllocation.objects.filter(room=new_room, status='Active').count() >= new_room.capacity:
            messages.error(request, f'Room {new_room.room_no} is full.')
            return redirect('hostel:transfer_student', allocation_id=allocation_id)
        with transaction.atomic():
            old_room      = alloc.room
            alloc.status  = 'Transferred'
            alloc.save()
            if RoomAllocation.objects.filter(room=old_room, status='Active').count() == 0:
                old_room.status = 'Available'
                old_room.save()
            RoomAllocation.objects.create(student=alloc.student, room=new_room, status='Active')
            if RoomAllocation.objects.filter(room=new_room, status='Active').count() >= new_room.capacity:
                new_room.status = 'Occupied'
                new_room.save()
        messages.success(
            request,
            f'{alloc.student.full_name} transferred from Room {old_room.room_no} to Room {new_room.room_no}.'
        )
        return redirect('hostel:allocation_list')
    available_rooms = Room.objects.filter(status='Available').exclude(room_id=alloc.room.room_id)
    return render(request, 'hostel/transfer_student.html', {
        'alloc':           alloc,
        'available_rooms': available_rooms,
    })


# ─────────────────────────────────────────────────────────────────────────────
# AUTH (Removed)
# ─────────────────────────────────────────────────────────────────────────────

# Login and logout views have been completely removed as per user request.


# ═══════════════════════════════════════════════════════════════════════════════
# COMPLAINTS  (admin: maintenance_dashboard; student: raise + my list)
# ═══════════════════════════════════════════════════════════════════════════════

def raise_complaint(request):
    if request.method == 'POST':
        complaint_type = request.POST.get('complaint_type', '').strip()
        description    = request.POST.get('description', '').strip()
        if not complaint_type or not description:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('hostel:raise_complaint')
        # Using a mock active student since authentication is removed
        student = Student.objects.filter(status='Active').first()
        
        # We must provide a room_id for the complaint. Find the student's active room.
        from .models import RoomAllocation, Room
        allocation = RoomAllocation.objects.filter(student=student, status='Active').first()
        room = allocation.room if allocation else Room.objects.first()

        Complaint.objects.create(
            student=student,
            room=room,
            complaint_type=complaint_type,
            description=description,
            status='Pending',
        )
        messages.success(request, 'Your complaint has been submitted.')
        return redirect('hostel:my_complaints_view')

    COMPLAINT_TYPES = ['Bathroom', 'Electrical', 'Cleaning', 'Pest Control', 'Furniture', 'Other']
    return render(request, 'hostel/complaints/raise_complaint.html', {
        'complaint_types': COMPLAINT_TYPES,
    })


def my_complaints_view(request):
    # Show all complaints since there is no login/role isolation
    complaints = Complaint.objects.all().order_by('-complaint_date')
    return render(request, 'hostel/complaints/my_complaints.html', {'complaints': complaints})


@admin_required
def maintenance_dashboard_view(request):
    total       = Complaint.objects.count()
    pending     = Complaint.objects.filter(status='Pending').count()
    in_progress = Complaint.objects.filter(status='In Progress').count()
    resolved    = Complaint.objects.filter(status='Resolved').count()
    complaints  = Complaint.objects.select_related('student', 'room').order_by('-complaint_date')
    return render(request, 'hostel/complaints/maintenance_dashboard.html', {
        'total': total, 'pending': pending, 'in_progress': in_progress,
        'resolved': resolved, 'complaints': complaints,
    })


@admin_required
def complaint_detail_view(request, complaint_id):
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        if new_status in ['Pending', 'In Progress', 'Resolved']:
            complaint.status = new_status
            complaint.save()
            messages.success(request, f'Complaint #{complaint_id} updated to {new_status}.')
    return redirect('hostel:maintenance_dashboard_view')


# ═══════════════════════════════════════════════════════════════════════════════
# GATE PASS
# ═══════════════════════════════════════════════════════════════════════════════

def request_gate_pass(request):
    if request.method == 'POST':
        try:
            # Using a mock active student since authentication is removed
            student = Student.objects.filter(status='Active').first()
            GatePass.objects.create(
                student=student,
                room_no=request.POST.get('room_no', '').strip(),
                destination=request.POST.get('destination', '').strip(),
                purpose=request.POST.get('purpose', '').strip(),
                out_date=request.POST.get('out_date'),
                out_time=request.POST.get('out_time'),
                return_date=request.POST.get('return_date'),
                return_time=request.POST.get('return_time'),
                emergency_contact=request.POST.get('emergency_contact', '').strip() or None,
                status='Pending',
            )
            messages.success(request, 'Gate pass request submitted successfully.')
            return redirect('hostel:my_gate_passes')
        except Exception as e:
            messages.error(request, f'Error submitting gate pass: {e}')

    student_name = student_id_val = room_no = ''
    # Using a mock active student since authentication is removed
    student = Student.objects.filter(status='Active').first()
    if student:
        student_name   = student.full_name
        student_id_val = student.registration_id
        alloc = RoomAllocation.objects.filter(student=student, status='Active').first()
        if alloc:
            room_no = alloc.room.room_no
    return render(request, 'hostel/gatepass/request_gate_pass.html', {
        'student_name': student_name, 'student_id_val': student_id_val, 'room_no': room_no,
    })


def my_gate_passes(request):
    # Show all gate passes since there is no login/role isolation
    passes  = GatePass.objects.all().order_by('-created_at')
    return render(request, 'hostel/gatepass/my_gate_passes.html', {'passes': passes})


@admin_required
def gate_pass_dashboard(request):
    total    = GatePass.objects.count()
    pending  = GatePass.objects.filter(status='Pending').count()
    approved = GatePass.objects.filter(status='Approved').count()
    rejected = GatePass.objects.filter(status='Rejected').count()
    returned = GatePass.objects.filter(status='Returned').count()
    passes   = GatePass.objects.select_related('student').order_by('-created_at')
    return render(request, 'hostel/gatepass/gate_pass_dashboard.html', {
        'total': total, 'pending': pending, 'approved': approved,
        'rejected': rejected, 'returned': returned, 'passes': passes,
    })


def gate_pass_detail(request, pass_id):
    gp = get_object_or_404(GatePass, pass_id=pass_id)
    return render(request, 'hostel/gatepass/request_gate_pass.html', {'gp': gp, 'view_only': True})


@admin_required
def approve_gate_pass(request, pass_id):
    gp = get_object_or_404(GatePass, pass_id=pass_id)
    if request.method == 'POST':
        gp.status = 'Approved'; gp.approved_by = request.user.id; gp.approved_at = timezone.now(); gp.save()
        messages.success(request, f'Gate pass #{pass_id} approved.')
    return redirect('hostel:gate_pass_dashboard')


@admin_required
def reject_gate_pass(request, pass_id):
    gp = get_object_or_404(GatePass, pass_id=pass_id)
    if request.method == 'POST':
        gp.status = 'Rejected'; gp.save()
        messages.warning(request, f'Gate pass #{pass_id} rejected.')
    return redirect('hostel:gate_pass_dashboard')


@admin_required
def mark_returned(request, pass_id):
    gp = get_object_or_404(GatePass, pass_id=pass_id)
    if request.method == 'POST':
        gp.status = 'Returned'; gp.save()
        messages.success(request, f'Gate pass #{pass_id} marked as returned.')
    return redirect('hostel:gate_pass_dashboard')


# ═══════════════════════════════════════════════════════════════════════════════
# VISITORS
# ═══════════════════════════════════════════════════════════════════════════════

def request_visitor_pass(request):
    if request.method == 'POST':
        try:
            # Using a mock active student since authentication is removed
            student = Student.objects.filter(status='Active').first()
            Visitor.objects.create(
                student=student,
                visitor_name=request.POST.get('visitor_name', '').strip(),
                relationship=request.POST.get('relationship', '').strip() or None,
                mobile=request.POST.get('mobile', '').strip() or None,
                checkin=request.POST.get('checkin') or None,
                checkout=request.POST.get('checkout') or None,
                purpose=request.POST.get('purpose', '').strip() or None,
                status='Pending',
            )
            messages.success(request, 'Visitor request submitted successfully.')
            return redirect('hostel:my_visitor_requests')
        except Exception as e:
            messages.error(request, f'Error registering visitor: {e}')
    return render(request, 'hostel/visitors/request_visitor_pass.html')


def my_visitor_requests(request):
    # Show all visitor requests since there is no login/role isolation
    visitors = Visitor.objects.all().order_by('-visitor_id')
    return render(request, 'hostel/visitors/my_visitor_requests.html', {'visitors': visitors})


@admin_required
def visitor_dashboard(request):
    total    = Visitor.objects.count()
    pending  = Visitor.objects.filter(status='Pending').count()
    approved = Visitor.objects.filter(status='Approved').count()
    rejected = Visitor.objects.filter(status='Rejected').count()
    visitors = Visitor.objects.select_related('student').order_by('-visitor_id')
    return render(request, 'hostel/visitors/visitor_dashboard.html', {
        'total': total, 'pending': pending, 'approved': approved, 'rejected': rejected, 'visitors': visitors,
    })


@admin_required
def approve_visitor(request, visitor_id):
    v = get_object_or_404(Visitor, visitor_id=visitor_id)
    if request.method == 'POST':
        v.status = 'Approved'; v.approved_by = request.user.id; v.approved_at = timezone.now(); v.save()
        messages.success(request, f'Visitor #{visitor_id} approved.')
    return redirect('hostel:visitor_dashboard')


@admin_required
def reject_visitor(request, visitor_id):
    v = get_object_or_404(Visitor, visitor_id=visitor_id)
    if request.method == 'POST':
        v.status = 'Rejected'; v.save()
        messages.warning(request, f'Visitor #{visitor_id} rejected.')
    return redirect('hostel:visitor_dashboard')
