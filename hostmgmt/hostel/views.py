from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db import transaction, models as db_models
from django.contrib.auth.decorators import login_required
from django.utils import timezone
from .models import (
    Room, Student, Allocation,
    Complaint, MaintenanceRequest, GatePass, Visitor,
)
from django.contrib.auth import authenticate, login, logout

# NOTE: @login_required is intentionally commented out on most views.
# To enable, uncomment the decorator and ensure settings.LOGIN_URL is configured.


# ── DASHBOARD ──────────────────────────────────────────────────────────────────
# @login_required
def dashboard(request):
    total_rooms     = Room.objects.count()
    available_rooms = Room.objects.filter(is_under_repair=False, current_occupancy__lt=db_models.F('capacity')).count()
    occupied_rooms  = Room.objects.filter(current_occupancy__gt=0).count()
    repair_rooms    = Room.objects.filter(is_under_repair=True).count()
    total_students  = Student.objects.count()
    allocated       = Allocation.objects.filter(is_active=True).count()
    pending         = max(0, total_students - allocated)
    trainers_alloc  = 0
    batch_stats     = []

    return render(request, 'hostel/dashboard.html', {
        'total_rooms':     total_rooms,
        'available_rooms': available_rooms,
        'occupied_rooms':  occupied_rooms,
        'total_students':  total_students,
        'allocated':       allocated,
        'pending':         pending,
        'trainers_alloc':  trainers_alloc,
        'repair_rooms':    repair_rooms,
        'batch_stats':     batch_stats,
    })


# ── ROOMS ──────────────────────────────────────────────────────────────────────

def rooms_list(request):
    filter_type = request.GET.get('filter', 'all')
    qs = Room.objects.all().order_by('room_number')

    if filter_type == 'girls':
        qs = qs.filter(room_type='GIRLS')
    elif filter_type == 'boys':
        qs = qs.filter(room_type='BOYS')
    elif filter_type == 'trainer':
        qs = qs.filter(room_type='TRAINER')
    elif filter_type == 'repair':
        qs = qs.filter(is_under_repair=True)

    return render(request, 'hostel/rooms_list.html', {
        'rooms':       qs,
        'filter_type': filter_type,
    })


def room_detail(request, room_number):
    room = get_object_or_404(Room, room_number=room_number)
    allocations = Allocation.objects.filter(
        room=room, is_active=True
    ).select_related('student', 'allocated_by')
    history = Allocation.objects.filter(
        room=room
    ).select_related('student').order_by('-allocated_at')
    available_rooms = Room.objects.filter(
        is_under_repair=False
    ).filter(
        current_occupancy__lt=db_models.F('capacity')
    ).exclude(id=room.id).order_by('room_number')
    return render(request, 'hostel/room_detail.html', {
        'room':            room,
        'allocations':     allocations,
        'history':         history,
        'available_rooms': available_rooms,
    })


def add_room(request):
    if request.method == 'POST':
        try:
            room_number = int(request.POST['room_number'])
            room_type   = request.POST['room_type']
            capacity    = int(request.POST.get('capacity', 2))
            gender_map  = {'TRAINER': None, 'GIRLS': 'F', 'BOYS': 'M'}
            Room.objects.create(
                room_number=room_number,
                room_type=room_type,
                capacity=capacity,
                gender_category=gender_map.get(room_type),
            )
            messages.success(request, f'Room {room_number} added successfully.')
            return redirect('hostel:rooms')
        except Exception as e:
            messages.error(request, f'Error adding room: {e}')
    return render(request, 'hostel/add_room.html')


def edit_room(request, room_number):
    room = get_object_or_404(Room, room_number=room_number)
    if request.method == 'POST':
        try:
            room.capacity        = int(request.POST.get('capacity', room.capacity))
            room.is_under_repair = request.POST.get('is_under_repair') == 'on'
            room.save()
            messages.success(request, f'Room {room_number} updated.')
            return redirect('hostel:room_detail', room_number=room_number)
        except Exception as e:
            messages.error(request, f'Error updating room: {e}')
    return render(request, 'hostel/edit_room.html', {'room': room})


def toggle_repair(request, room_number):
    room = get_object_or_404(Room, room_number=room_number)
    if request.method == 'POST':
        room.is_under_repair = not room.is_under_repair
        room.save()
        status_text = 'marked under repair' if room.is_under_repair else 'marked as available'
        messages.success(request, f'Room {room_number} {status_text}.')
    return redirect('hostel:room_detail', room_number=room_number)


# ── STUDENTS ───────────────────────────────────────────────────────────────────

def students_list(request):
    batch_filter  = request.GET.get('batch', '')
    gender_filter = request.GET.get('gender', '')
    status_filter = request.GET.get('status', '')

    qs = Student.objects.all()
    if batch_filter:  qs = qs.filter(batch=batch_filter)
    if gender_filter: qs = qs.filter(gender=gender_filter)
    if status_filter: qs = qs.filter(allocation_status=status_filter)

    return render(request, 'hostel/students_list.html', {
        'students':      qs,
        'batch_filter':  batch_filter,
        'gender_filter': gender_filter,
        'status_filter': status_filter,
    })


def add_student(request):
    if request.method == 'POST':
        try:
            Student.objects.create(
                registration_id=request.POST['registration_id'],
                full_name=request.POST['full_name'],
                gender=request.POST['gender'],
                batch=request.POST['batch'],
                email=request.POST.get('email', ''),
                phone=request.POST.get('phone', ''),
            )
            messages.success(request, 'Student added successfully.')
            return redirect('hostel:students')
        except Exception as e:
            messages.error(request, f'Error: {e}')
    return render(request, 'hostel/add_student.html')


def import_students(request):
    """
    Import students from a CSV file.

    Expected CSV columns (header row required):
        registration_id, full_name, gender, batch [, email, phone]

    Gender values: M or F (case-insensitive)
    Batch values:  FSWD, AIML, DEVOPS (case-insensitive)
    """
    if request.method == 'POST':
        csv_file = request.FILES.get('csv_file')
        if not csv_file:
            messages.error(request, 'Please select a CSV file to upload.')
            return redirect('hostel:import_students')

        if not csv_file.name.endswith('.csv'):
            messages.error(request, 'Only .csv files are supported. Please upload a valid CSV file.')
            return redirect('hostel:import_students')

        try:
            import csv
            import io

            decoded = csv_file.read().decode('utf-8-sig')   # utf-8-sig handles BOM from Excel
            reader  = csv.DictReader(io.StringIO(decoded))

            # Normalise headers (strip whitespace, lowercase)
            reader.fieldnames = [h.strip().lower() for h in reader.fieldnames]

            created  = 0
            skipped  = 0
            errors   = []

            VALID_GENDERS = {'m': 'M', 'male': 'M', 'f': 'F', 'female': 'F', 'o': 'O', 'other': 'O'}
            VALID_BATCHES = {'fswd': 'FSWD', 'aiml': 'AIML', 'devops': 'DEVOPS'}

            for row_num, row in enumerate(reader, start=2):  # start=2 because row 1 is header
                try:
                    reg_id = row.get('registration_id', '').strip()
                    name   = row.get('full_name', '').strip()
                    gender = row.get('gender', '').strip().lower()
                    batch  = row.get('batch', '').strip().upper()
                    email  = row.get('email', '').strip()
                    phone  = row.get('phone', '').strip()

                    # Validate required fields
                    if not reg_id:
                        errors.append(f'Row {row_num}: Missing registration_id')
                        continue
                    if not name:
                        errors.append(f'Row {row_num}: Missing full_name')
                        continue
                    if gender not in VALID_GENDERS:
                        errors.append(f'Row {row_num}: Invalid gender "{gender}" (use M/F)')
                        continue
                    if batch not in VALID_BATCHES:
                        errors.append(f'Row {row_num}: Invalid batch "{batch}" (use FSWD/AIML/DEVOPS)')
                        continue

                    obj, was_created = Student.objects.get_or_create(
                        registration_id=reg_id,
                        defaults={
                            'full_name': name,
                            'gender':    VALID_GENDERS[gender],
                            'batch':     VALID_BATCHES[batch],
                            'email':     email or None,
                            'phone':     phone or None,
                        }
                    )
                    if was_created:
                        created += 1
                    else:
                        skipped += 1

                except Exception as e:
                    errors.append(f'Row {row_num}: {e}')

            # Report results
            if created:
                messages.success(request, f'Import complete: {created} student(s) added, {skipped} duplicate(s) skipped.')
            elif skipped and not errors:
                messages.warning(request, f'All {skipped} student(s) already exist — nothing new was imported.')
            else:
                messages.warning(request, f'Import finished: {created} added, {skipped} skipped.')

            if errors:
                for err in errors[:5]:   # Show max 5 errors to avoid flooding
                    messages.error(request, err)
                if len(errors) > 5:
                    messages.error(request, f'... and {len(errors) - 5} more row error(s). Check your CSV.')

            return redirect('hostel:students')

        except Exception as e:
            messages.error(request, f'Failed to process CSV file: {e}')
            return redirect('hostel:import_students')

    return render(request, 'hostel/import_students.html')



# ── AUTO ALLOCATION ────────────────────────────────────────────────────────────

@transaction.atomic
def auto_allocate(request, batch=None):
    if request.method != 'POST':
        batches = [
            {
                'code':    'FSWD',
                'label':   'FSWD',
                'pending': Student.objects.filter(batch='FSWD', allocation_status='PENDING').count(),
            },
            {
                'code':    'AIML',
                'label':   'AIML',
                'pending': Student.objects.filter(batch='AIML', allocation_status='PENDING').count(),
            },
            {
                'code':    'DEVOPS',
                'label':   'DevOps',
                'pending': Student.objects.filter(batch='DEVOPS', allocation_status='PENDING').count(),
            },
        ]
        return render(request, 'hostel/auto_allocate.html', {
            'batches':      batches,
            'filter_batch': batch,
        })

    filter_batch = request.POST.get('batch', '')

    # Fetch pending (unallocated) students
    qs = Student.objects.filter(allocation_status='PENDING')
    if filter_batch:
        qs = qs.filter(batch=filter_batch)

    girls = list(qs.filter(gender='F').order_by('batch', 'full_name'))
    boys  = list(qs.filter(gender='M').order_by('batch', 'full_name'))

    allocated_records = []
    skipped           = []

    def allocate_group(students, room_qs):
        rooms    = list(room_qs.filter(is_under_repair=False).order_by('room_number'))
        room_idx = 0
        for student in students:
            placed = False
            while room_idx < len(rooms):
                room = rooms[room_idx]
                room.refresh_from_db()
                if room.current_occupancy < room.capacity:
                    alloc = Allocation.objects.create(
                        student=student,
                        room=room,
                        allocated_by=request.user if request.user.is_authenticated else None,
                        allocation_type='AUTO',
                        is_active=True,
                    )
                    room.current_occupancy += 1
                    room.save()
                    student.allocation_status = 'ALLOCATED'
                    student.save()
                    allocated_records.append(alloc)
                    placed = True
                    if room.current_occupancy >= room.capacity:
                        room_idx += 1
                    break
                else:
                    room_idx += 1
            if not placed:
                skipped.append(student)

    # Segregated allocation: Girls → Rooms 7–16, Boys → Rooms 17–38
    allocate_group(girls, Room.objects.filter(room_type='GIRLS'))
    allocate_group(boys,  Room.objects.filter(room_type='BOYS'))

    # Store summary in session for results page
    request.session['alloc_summary'] = {
        'allocated_count': len(allocated_records),
        'skipped_count':   len(skipped),
        'batch':           filter_batch or 'ALL',
    }

    if skipped:
        messages.warning(
            request,
            f'{len(skipped)} student(s) could not be allocated — no available rooms.'
        )
    messages.success(
        request,
        f'Auto allocation complete. {len(allocated_records)} student(s) allocated.'
    )
    return redirect('hostel:allocation_results')


# ── MANUAL ALLOCATION ──────────────────────────────────────────────────────────

def manual_allocate(request):
    if request.method == 'POST':
        student_id = request.POST.get('student_id')
        room_id    = request.POST.get('room_id')

        if not student_id or not room_id:
            messages.error(request, 'Please select both a student and a room.')
            return redirect('hostel:manual_allocate')

        student = get_object_or_404(Student, id=student_id)
        room    = get_object_or_404(Room, id=room_id)

        # Validation chain
        if student.allocation_status == 'ALLOCATED':
            messages.error(request, f'{student.full_name} is already allocated to a room.')
            return redirect('hostel:manual_allocate')
        if room.is_under_repair:
            messages.error(request, f'Room {room.room_number} is under repair. Choose another room.')
            return redirect('hostel:manual_allocate')
        if room.is_full:
            messages.error(request, f'Room {room.room_number} is full. Choose another room.')
            return redirect('hostel:manual_allocate')

        gender_map      = {'GIRLS': 'F', 'BOYS': 'M'}
        required_gender = gender_map.get(room.room_type)
        if required_gender and student.gender != required_gender:
            gender_label = 'Girls' if required_gender == 'F' else 'Boys'
            messages.error(
                request,
                f'Gender mismatch! Room {room.room_number} is a {gender_label} hostel room. '
                f'{student.full_name} cannot be placed here.'
            )
            return redirect('hostel:manual_allocate')

        with transaction.atomic():
            Allocation.objects.create(
                student=student,
                room=room,
                allocated_by=request.user if request.user.is_authenticated else None,
                allocation_type='MANUAL',
                is_active=True,
            )
            room.current_occupancy += 1
            room.save()
            student.allocation_status = 'ALLOCATED'
            student.save()

        messages.success(
            request,
            f'{student.full_name} successfully allocated to Room {room.room_number}.'
        )
        return redirect('hostel:manual_allocate')

    unallocated = Student.objects.filter(
        allocation_status='PENDING'
    ).order_by('batch', 'full_name')

    available_rooms = Room.objects.filter(
        is_under_repair=False
    ).filter(
        current_occupancy__lt=db_models.F('capacity')
    ).order_by('room_number')

    return render(request, 'hostel/manual_allocate.html', {
        'unallocated':     unallocated,
        'available_rooms': available_rooms,
    })


# ── ALLOCATION RESULTS & LIST ──────────────────────────────────────────────────

def allocation_results(request):
    allocations = Allocation.objects.filter(
        is_active=True
    ).select_related('student', 'room').order_by('room__room_number')

    # Group by room for the cards view
    rooms_data = {}
    for alloc in allocations:
        rn = alloc.room.room_number
        if rn not in rooms_data:
            rooms_data[rn] = {'room': alloc.room, 'occupants': []}
        rooms_data[rn]['occupants'].append(alloc.student)

    rooms_used = len(rooms_data)
    total      = Student.objects.count()
    allocated  = Allocation.objects.filter(is_active=True).count()

    remaining_agg = Room.objects.filter(is_under_repair=False).aggregate(
        cap=db_models.Sum(db_models.F('capacity') - db_models.F('current_occupancy'))
    )
    remaining = remaining_agg['cap'] or 0

    summary = request.session.pop('alloc_summary', {})

    return render(request, 'hostel/allocation_results.html', {
        'rooms_data':          rooms_data.values(),
        'rooms_used':          rooms_used,
        'total_students':      total,
        'allocated_students':  allocated,
        'remaining_capacity':  remaining,
        'summary':             summary,
    })


def allocation_list(request):
    batch_filter  = request.GET.get('batch', '')
    gender_filter = request.GET.get('gender', '')
    type_filter   = request.GET.get('room_type', '')
    alloc_filter  = request.GET.get('alloc_type', '')

    qs = Allocation.objects.filter(
        is_active=True
    ).select_related('student', 'room', 'allocated_by').order_by('room__room_number')

    if batch_filter:  qs = qs.filter(student__batch=batch_filter)
    if gender_filter: qs = qs.filter(student__gender=gender_filter)
    if type_filter:   qs = qs.filter(room__room_type=type_filter)
    if alloc_filter:  qs = qs.filter(allocation_type=alloc_filter)

    return render(request, 'hostel/allocation_list.html', {
        'allocations':  qs,
        'batch_filter': batch_filter,
        'gender_filter': gender_filter,
        'type_filter':  type_filter,
        'alloc_filter': alloc_filter,
    })


# ── ADMIN ACTIONS ──────────────────────────────────────────────────────────────

def remove_allocation(request, allocation_id):
    alloc = get_object_or_404(Allocation, id=allocation_id)
    if request.method == 'POST':
        with transaction.atomic():
            alloc.is_active = False
            alloc.save()
            alloc.room.current_occupancy = max(0, alloc.room.current_occupancy - 1)
            alloc.room.save()
            alloc.student.allocation_status = 'PENDING'
            alloc.student.save()
        messages.success(
            request,
            f'{alloc.student.full_name} removed from Room {alloc.room.room_number}. '
            f'Status reset to Pending.'
        )
    return redirect(request.META.get('HTTP_REFERER', '/hostel/allocate/list/'))


def transfer_student(request, allocation_id):
    alloc = get_object_or_404(Allocation, id=allocation_id)

    if request.method == 'POST':
        new_room_id = request.POST.get('new_room_id')
        new_room    = get_object_or_404(Room, id=new_room_id)

        # Validations
        if new_room.is_under_repair:
            messages.error(request, f'Room {new_room.room_number} is under repair.')
            return redirect('hostel:transfer_student', allocation_id=allocation_id)
        if new_room.is_full:
            messages.error(request, f'Room {new_room.room_number} is full.')
            return redirect('hostel:transfer_student', allocation_id=allocation_id)

        gender_map      = {'GIRLS': 'F', 'BOYS': 'M'}
        required_gender = gender_map.get(new_room.room_type)
        if required_gender and alloc.student.gender != required_gender:
            gender_label = 'Girls' if required_gender == 'F' else 'Boys'
            messages.error(
                request,
                f'Gender mismatch! Room {new_room.room_number} is a {gender_label} hostel room.'
            )
            return redirect('hostel:transfer_student', allocation_id=allocation_id)

        with transaction.atomic():
            old_room = alloc.room
            old_room.current_occupancy = max(0, old_room.current_occupancy - 1)
            old_room.save()

            alloc.room            = new_room
            alloc.allocation_type = 'MANUAL'
            alloc.save()

            new_room.current_occupancy += 1
            new_room.save()

        messages.success(
            request,
            f'{alloc.student.full_name} transferred from Room {old_room.room_number} '
            f'to Room {new_room.room_number}.'
        )
        return redirect('hostel:allocation_list')

    available_rooms = Room.objects.filter(
        is_under_repair=False
    ).filter(
        current_occupancy__lt=db_models.F('capacity')
    ).exclude(id=alloc.room.id).order_by('room_number')

    return render(request, 'hostel/transfer_student.html', {
        'alloc':           alloc,
        'available_rooms': available_rooms,
    })


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect('hostel:dashboard')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'login.html')


def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out.')
    return redirect('hostel:login')


# ═══════════════════════════════════════════════════════════════════════════════
# ── COMPLAINTS MODULE ──────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def raise_complaint(request):
    """Allow a student to submit a new complaint."""
    if request.method == 'POST':
        complaint_type = request.POST.get('complaint_type', '').strip()
        description    = request.POST.get('description', '').strip()

        if not complaint_type or not description:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('hostel:raise_complaint')

        # Link to student if authenticated and a student record exists
        student = None
        if request.user.is_authenticated:
            student = Student.objects.filter(email=request.user.email).first()

        Complaint.objects.create(
            student=student,
            complaint_type=complaint_type,
            description=description,
            status='Pending',
        )
        messages.success(request, 'Your complaint has been submitted. The warden will review it shortly.')
        return redirect('hostel:my_complaints_view')

    COMPLAINT_TYPES = ['Bathroom', 'Electrical', 'Cleaning', 'Pest Control', 'Furniture', 'Other']
    return render(request, 'hostel/complaints/raise_complaint.html', {
        'complaint_types': COMPLAINT_TYPES,
    })


def my_complaints_view(request):
    """Show the current user's complaints."""
    student = None
    complaints = Complaint.objects.none()

    if request.user.is_authenticated:
        student = Student.objects.filter(email=request.user.email).first()
        if student:
            complaints = Complaint.objects.filter(student=student).order_by('-complaint_date')
        elif request.user.is_staff:
            complaints = Complaint.objects.all().order_by('-complaint_date')

    return render(request, 'hostel/complaints/my_complaints.html', {
        'complaints': complaints,
    })


def maintenance_dashboard_view(request):
    """Admin-only: overview of all complaints."""
    total      = Complaint.objects.count()
    pending    = Complaint.objects.filter(status='Pending').count()
    in_progress = Complaint.objects.filter(status='In Progress').count()
    resolved   = Complaint.objects.filter(status='Resolved').count()
    complaints = Complaint.objects.select_related('student', 'room').order_by('-complaint_date')

    return render(request, 'hostel/complaints/maintenance_dashboard.html', {
        'total':       total,
        'pending':     pending,
        'in_progress': in_progress,
        'resolved':    resolved,
        'complaints':  complaints,
    })


def complaint_detail_view(request, complaint_id):
    """View and update a single complaint (admin)."""
    complaint = get_object_or_404(Complaint, complaint_id=complaint_id)

    if request.method == 'POST' and request.user.is_staff:
        new_status = request.POST.get('status')
        if new_status in ['Pending', 'In Progress', 'Resolved']:
            complaint.status = new_status
            complaint.save()
            messages.success(request, f'Complaint #{complaint_id} status updated to {new_status}.')
        return redirect('hostel:maintenance_dashboard_view')

    return render(request, 'hostel/complaints/maintenance_dashboard.html', {
        'complaint': complaint,
    })


# ═══════════════════════════════════════════════════════════════════════════════
# ── GATE PASS MODULE ───────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def request_gate_pass(request):
    """Allow a student to request a gate pass."""
    if request.method == 'POST':
        try:
            student = None
            if request.user.is_authenticated:
                student = Student.objects.filter(email=request.user.email).first()

            GatePass.objects.create(
                student=student,
                room_no=request.POST.get('room_no', '').strip(),
                destination=request.POST.get('destination', '').strip(),
                purpose=request.POST.get('purpose', '').strip(),
                out_date=request.POST.get('out_date'),
                out_time=request.POST.get('out_time'),
                return_date=request.POST.get('return_date'),
                return_time=request.POST.get('return_time'),
                emergency_contact=request.POST.get('emergency_contact', '').strip(),
                status='Pending',
            )
            messages.success(request, 'Gate pass request submitted successfully.')
            return redirect('hostel:my_gate_passes')
        except Exception as e:
            messages.error(request, f'Error submitting gate pass: {e}')

    # Pre-fill student info
    student_name = ''
    student_id_val = ''
    room_no = ''
    if request.user.is_authenticated:
        student = Student.objects.filter(email=request.user.email).first()
        if student:
            student_name   = student.full_name
            student_id_val = student.registration_id
            alloc = Allocation.objects.filter(student=student, is_active=True).first()
            if alloc:
                room_no = alloc.room.room_number

    return render(request, 'hostel/gatepass/request_gate_pass.html', {
        'student_name':    student_name,
        'student_id_val':  student_id_val,
        'room_no':         room_no,
    })


def my_gate_passes(request):
    """Show the current student's gate passes."""
    passes = GatePass.objects.none()
    if request.user.is_authenticated:
        student = Student.objects.filter(email=request.user.email).first()
        if student:
            passes = GatePass.objects.filter(student=student).order_by('-created_at')
        elif request.user.is_staff:
            passes = GatePass.objects.all().order_by('-created_at')

    return render(request, 'hostel/gatepass/my_gate_passes.html', {
        'passes': passes,
    })


def gate_pass_dashboard(request):
    """Admin-only gate pass overview."""
    total    = GatePass.objects.count()
    pending  = GatePass.objects.filter(status='Pending').count()
    approved = GatePass.objects.filter(status='Approved').count()
    rejected = GatePass.objects.filter(status='Rejected').count()
    returned = GatePass.objects.filter(status='Returned').count()
    passes   = GatePass.objects.select_related('student', 'approved_by').order_by('-created_at')

    return render(request, 'hostel/gatepass/gate_pass_dashboard.html', {
        'total':    total,
        'pending':  pending,
        'approved': approved,
        'rejected': rejected,
        'returned': returned,
        'passes':   passes,
    })


def gate_pass_detail(request, pass_id):
    gp = get_object_or_404(GatePass, pass_id=pass_id)
    return render(request, 'hostel/gatepass/request_gate_pass.html', {'gp': gp, 'view_only': True})


def approve_gate_pass(request, pass_id):
    gp = get_object_or_404(GatePass, pass_id=pass_id)
    if request.method == 'POST' and request.user.is_staff:
        gp.status      = 'Approved'
        gp.approved_by = request.user
        gp.approved_at = timezone.now()
        gp.save()
        messages.success(request, f'Gate pass #{pass_id} approved.')
    return redirect('hostel:gate_pass_dashboard')


def reject_gate_pass(request, pass_id):
    gp = get_object_or_404(GatePass, pass_id=pass_id)
    if request.method == 'POST' and request.user.is_staff:
        gp.status = 'Rejected'
        gp.save()
        messages.warning(request, f'Gate pass #{pass_id} rejected.')
    return redirect('hostel:gate_pass_dashboard')


def mark_returned(request, pass_id):
    gp = get_object_or_404(GatePass, pass_id=pass_id)
    if request.method == 'POST':
        gp.status = 'Returned'
        gp.save()
        messages.success(request, f'Gate pass #{pass_id} marked as returned.')
    return redirect('hostel:gate_pass_dashboard')


# ═══════════════════════════════════════════════════════════════════════════════
# ── VISITORS MODULE ────────────────────────────────────────────────────────────
# ═══════════════════════════════════════════════════════════════════════════════

def request_visitor_pass(request):
    """Allow a student to register a visitor."""
    if request.method == 'POST':
        try:
            student = None
            if request.user.is_authenticated:
                student = Student.objects.filter(email=request.user.email).first()

            Visitor.objects.create(
                student=student,
                visitor_name=request.POST.get('visitor_name', '').strip(),
                relationship=request.POST.get('relationship', '').strip(),
                mobile=request.POST.get('mobile', '').strip(),
                checkin=request.POST.get('checkin') or None,
                checkout=request.POST.get('checkout') or None,
                purpose=request.POST.get('purpose', '').strip(),
                status='Pending',
            )
            messages.success(request, 'Visitor request submitted successfully.')
            return redirect('hostel:my_visitor_requests')
        except Exception as e:
            messages.error(request, f'Error registering visitor: {e}')

    return render(request, 'hostel/visitors/request_visitor_pass.html')


def my_visitor_requests(request):
    """Show the current student's visitor requests."""
    visitors = Visitor.objects.none()
    if request.user.is_authenticated:
        student = Student.objects.filter(email=request.user.email).first()
        if student:
            visitors = Visitor.objects.filter(student=student).order_by('-visitor_id')
        elif request.user.is_staff:
            visitors = Visitor.objects.all().order_by('-visitor_id')

    return render(request, 'hostel/visitors/my_visitor_requests.html', {
        'visitors': visitors,
    })


def visitor_dashboard(request):
    """Admin-only visitor overview."""
    total    = Visitor.objects.count()
    pending  = Visitor.objects.filter(status='Pending').count()
    approved = Visitor.objects.filter(status='Approved').count()
    rejected = Visitor.objects.filter(status='Rejected').count()
    visitors = Visitor.objects.select_related('student', 'approved_by').order_by('-visitor_id')

    return render(request, 'hostel/visitors/visitor_dashboard.html', {
        'total':    total,
        'pending':  pending,
        'approved': approved,
        'rejected': rejected,
        'visitors': visitors,
    })


def approve_visitor(request, visitor_id):
    v = get_object_or_404(Visitor, visitor_id=visitor_id)
    if request.method == 'POST' and request.user.is_staff:
        v.status      = 'Approved'
        v.approved_by = request.user
        v.approved_at = timezone.now()
        v.save()
        messages.success(request, f'Visitor #{visitor_id} approved.')
    return redirect('hostel:visitor_dashboard')


def reject_visitor(request, visitor_id):
    v = get_object_or_404(Visitor, visitor_id=visitor_id)
    if request.method == 'POST' and request.user.is_staff:
        v.status = 'Rejected'
        v.save()
        messages.warning(request, f'Visitor #{visitor_id} rejected.')
    return redirect('hostel:visitor_dashboard')
