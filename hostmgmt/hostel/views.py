from django.shortcuts import render

def dashboard(request):
    return render(request,'dashboard.html')

def rooms(request):
    return render(request,'rooms.html')

def students(request):
    return render(request,'students.html')

def allocation(request):
    return render(request,'allocation.html')