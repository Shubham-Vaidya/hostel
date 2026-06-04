from django.shortcuts import render
from .models import Room, Allocation



def dashboard(request):
    return render(request, 'dashboard.html')

def room_list(request):
    rooms = Room.objects.all().prefetch_related("allocation_set")

    room_data = []

    for room in rooms:
        allocations = room.allocation_set.all()

        if room.is_under_repair:
            status = "grey"
        elif allocations.count() == 2:
            status = "red"
        elif allocations.count() == 1:
            status = "yellow"
        else:
            status = "green"

        room_data.append({
            "room": room,
            "students": allocations,
            "status": status
        })

    return render(request, "rooms.html", {"rooms": room_data})