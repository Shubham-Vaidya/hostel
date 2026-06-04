from django.shortcuts import render

# Dummy Student Data

rooms = {
    7: [],
    8: [],
    9: [],
    10: [],
    11: [],
    12: [],
    13: [],
    14: [],
    15: [],
    16: [],

    17: [],
    18: [],
    19: [],
    20: [],
    21: [],
    22: [],
    23: [],
    24: [],
    25: [],
    26: [],
    27: [],
    28: [],
    29: [],
    30: [],
    31: [],
    32: [],
    33: [],
    34: [],
    35: [],
    36: [],
    37: [],
    38: [],
}

student_data = [

    {
        "id": 101,
        "name": "Rahul Sharma",
        "gender": "Male",
        "batch": "FSWD",
        "status": "Pending"
    },

    {
        "id": 102,
        "name": "Arjun Patil",
        "gender": "Male",
        "batch": "FSWD",
        "status": "Pending"
    },

    {
        "id": 103,
        "name": "Priya Singh",
        "gender": "Female",
        "batch": "FSWD",
        "status": "Pending"
    },

    {
        "id": 104,
        "name": "Sneha Joshi",
        "gender": "Female",
        "batch": "FSWD",
        "status": "Pending"
    },

    {
        "id": 201,
        "name": "Ananya Shah",
        "gender": "Female",
        "batch": "AIML",
        "status": "Pending"
    },

    {
        "id": 202,
        "name": "Riya Mehta",
        "gender": "Female",
        "batch": "AIML",
        "status": "Pending"
    },

    {
        "id": 301,
        "name": "Vikram Rao",
        "gender": "Male",
        "batch": "DEVOPS",
        "status": "Pending"
    },

    {
        "id": 302,
        "name": "Karan Gupta",
        "gender": "Male",
        "batch": "DEVOPS",
        "status": "Pending"
    },
    {
    "id":105,
    "name":"Karan Shah",
    "gender":"Male",
    "batch":"FSWD",
    "status":"Pending"
},
{
    "id":106,
    "name":"Aman Gupta",
    "gender":"Male",
    "batch":"FSWD",
    "status":"Pending"
},
{
    "id":107,
    "name":"Neha Patil",
    "gender":"Female",
    "batch":"FSWD",
    "status":"Pending"
},
{
    "id":108,
    "name":"Aditi Mehta",
    "gender":"Female",
    "batch":"FSWD",
    "status":"Pending"
},

]


# Dashboard

def dashboard(request):
    return render(request, 'dashboard.html')


# Rooms Page

def rooms(request):
    return render(request, 'rooms.html')


# Students Page

def students(request):
    return render(request, 'students.html')


# Allocation Landing Page

def allocation(request):
    return render(request, 'allocation.html')


# FSWD Allocation

def fswd_allocation(request):

    fswd_students = [
        student
        for student in student_data
        if student["batch"] == "FSWD"
    ]

    return render(
        request,
        "fswd_allocation.html",
        {
            "students": fswd_students
        }
    )


# AIML Allocation

def aiml_allocation(request):

    aiml_students = [
        student
        for student in student_data
        if student["batch"] == "AIML"
    ]

    return render(
        request,
        "aiml_allocation.html",
        {
            "students": aiml_students
        }
    )


# DEVOPS Allocation

def devops_allocation(request):

    devops_students = [
        student
        for student in student_data
        if student["batch"] == "DEVOPS"
    ]

    return render(
        request,
        "devops_allocation.html",
        {
            "students": devops_students
        }
    )

def auto_allocate_students(student_list):

    allocations = {}

    girls = []
    boys = []

    for student in student_list:

        if student["gender"] == "Female":
            girls.append(student)

        else:
            boys.append(student)

    # Girls Rooms 7-16

    room_number = 7

    for i in range(0, len(girls), 2):

        allocations[room_number] = girls[i:i+2]

        room_number += 1

    # Boys Rooms 17-38

    room_number = 17

    for i in range(0, len(boys), 2):

        allocations[room_number] = boys[i:i+2]

        room_number += 1

    return allocations

def fswd_auto_allocate(request):

    fswd_students = [
        student
        for student in student_data
        if student["batch"] == "FSWD"
    ]

    allocations = auto_allocate_students(fswd_students)

    return render(
        request,
        "allocation_result.html",
        {
            "allocations": allocations,
            "batch": "FSWD"
        }
    )

def auto_allocate_students(student_list):

    allocations = {}

    girls = []
    boys = []

    for student in student_list:

        if student["gender"] == "Female":
            girls.append(student)
        else:
            boys.append(student)

    # Girls -> Rooms 7-16

    room_number = 7

    for i in range(0, len(girls), 2):

        allocations[room_number] = girls[i:i+2]

        room_number += 1

    # Boys -> Rooms 17-38

    room_number = 17

    for i in range(0, len(boys), 2):

        allocations[room_number] = boys[i:i+2]

        room_number += 1

    return allocations

def fswd_auto_allocate(request):

    fswd_students = [
        student
        for student in student_data
        if student["batch"] == "FSWD"
    ]

    allocations = auto_allocate_students(fswd_students)

    total_students = len(fswd_students)

    allocated_students = sum(
        len(students)
        for students in allocations.values()
    )

    rooms_used = len(allocations)

    remaining_capacity = (32 * 2) - allocated_students
    # Rooms 7-38 = 32 rooms
    # Capacity = 64 beds

    return render(
        request,
        "allocation_result.html",
        {
            "allocations": allocations,
            "batch": "FSWD",

            "total_students": total_students,
            "allocated_students": allocated_students,
            "rooms_used": rooms_used,
            "remaining_capacity": remaining_capacity,
        }
    )