from django.urls import path
from . import views

app_name = 'hostel'

urlpatterns = [
    # Dashboard
    path('',                                   views.dashboard,          name='dashboard'),

    # Rooms
    path('rooms/',                             views.rooms_list,         name='rooms'),
    path('rooms/add/',                         views.add_room,           name='add_room'),
    path('rooms/<int:room_number>/',           views.room_detail,        name='room_detail'),
    path('rooms/<int:room_number>/edit/',      views.edit_room,          name='edit_room'),
    path('rooms/<int:room_number>/repair/',    views.toggle_repair,      name='toggle_repair'),

    # Students
    path('students/',                          views.students_list,      name='students'),
    path('students/add/',                      views.add_student,        name='add_student'),
    path('students/import/',                   views.import_students,    name='import_students'),

    # Allocation
    path('allocate/auto/',                     views.auto_allocate,      name='auto_allocate'),
    path('allocate/auto/<str:batch>/',         views.auto_allocate,      name='auto_allocate_batch'),
    path('allocate/manual/',                   views.manual_allocate,    name='manual_allocate'),
    path('allocate/results/',                  views.allocation_results, name='allocation_results'),
    path('allocate/list/',                     views.allocation_list,    name='allocation_list'),
    path('allocate/remove/<int:allocation_id>/',   views.remove_allocation,  name='remove_allocation'),
    path('allocate/transfer/<int:allocation_id>/', views.transfer_student,   name='transfer_student'),
]