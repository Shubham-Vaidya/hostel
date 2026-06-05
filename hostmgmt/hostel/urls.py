from django.urls import path
from . import views

app_name = 'hostel'

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),

    # Optional - keep these if you don't want errors when links exist
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

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

    # ── Complaints / Maintenance ───────────────────────────────────────────────
    path('complaints/raise/',                  views.raise_complaint,            name='raise_complaint'),
    path('complaints/my/',                     views.my_complaints_view,         name='my_complaints_view'),
    path('complaints/dashboard/',              views.maintenance_dashboard_view, name='maintenance_dashboard_view'),
    path('complaints/detail/<int:complaint_id>/', views.complaint_detail_view,  name='complaint_detail_view'),

    # ── Gate Pass ──────────────────────────────────────────────────────────────
    path('gatepass/request/',                  views.request_gate_pass,  name='request_gate_pass'),
    path('gatepass/my/',                       views.my_gate_passes,     name='my_gate_passes'),
    path('gatepass/dashboard/',                views.gate_pass_dashboard, name='gate_pass_dashboard'),
    path('gatepass/detail/<int:pass_id>/',     views.gate_pass_detail,   name='gate_pass_detail'),
    path('gatepass/approve/<int:pass_id>/',    views.approve_gate_pass,  name='approve_gate_pass'),
    path('gatepass/reject/<int:pass_id>/',     views.reject_gate_pass,   name='reject_gate_pass'),
    path('gatepass/returned/<int:pass_id>/',   views.mark_returned,      name='mark_returned'),

    # ── Visitors ───────────────────────────────────────────────────────────────
    path('visitors/request/',                  views.request_visitor_pass, name='request_visitor_pass'),
    path('visitors/my/',                       views.my_visitor_requests,  name='my_visitor_requests'),
    path('visitors/dashboard/',                views.visitor_dashboard,    name='visitor_dashboard'),
    path('visitors/approve/<int:visitor_id>/', views.approve_visitor,      name='approve_visitor'),
    path('visitors/reject/<int:visitor_id>/',  views.reject_visitor,       name='reject_visitor'),
]