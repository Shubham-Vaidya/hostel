from django.urls import path
from . import views

urlpatterns = [

    path('', views.dashboard, name='dashboard'),

    # Room Module (Srushti)
    path('rooms/', views.room_list, name='rooms'),

    # Existing Pages
    path('students/', views.students, name='students'),
    path('allocation/', views.allocation, name='allocation'),

    # Batch Allocation
    path('allocation/fswd/', views.fswd_allocation, name='fswd'),
    path('allocation/aiml/', views.aiml_allocation, name='aiml'),
    path('allocation/devops/', views.devops_allocation, name='devops'),

    # Auto Allocation
    path(
        'allocation/fswd/auto/',
        views.fswd_auto_allocate,
        name='fswd_auto_allocate'
    ),

]