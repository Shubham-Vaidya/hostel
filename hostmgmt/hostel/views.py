from django.shortcuts import render

# Dummy Student Data

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
    }

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